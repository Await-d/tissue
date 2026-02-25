import os
import shutil
from typing import List, Optional

from cachetools import cached, LRUCache
from fastapi import Depends
from sqlalchemy.orm import Session

from app import utils
from app.db import get_db
from app.db.models import History
from app.exception import BizException
from app.schema import VideoList, VideoDetail, Setting, VideoNotify
from app.schema.video import VideoActor
from app.service.base import BaseService
from app.utils import nfo, spider, num_parser, cache, notify
from app.service.spider import get_video_info_with_config
from app.utils.image import save_images
from app.utils.logger import logger


def get_video_service(db: Session = Depends(get_db)):
    return VideoService(db=db)


video_cache = LRUCache(maxsize=1)


class VideoService(BaseService):
    @cached(cache=video_cache, key=lambda self: "videos")
    def get_videos(self) -> List[VideoList]:
        setting = Setting().app
        video_paths = []
        for root, _, files in os.walk(setting.video_path):
            for file in files:
                path = os.path.join(root, file)
                _, ext_name = os.path.splitext(path)
                size = os.stat(path).st_size

                if ext_name in setting.video_format.split(",") and size > (
                    setting.video_size_minimum * 1024 * 1024
                ):
                    video_paths.append(path)

        videos = []
        for path in video_paths:
            video = nfo.get_basic(path, include_actor=True)
            if not video:
                video = VideoList(title=path.split("/")[-1], path=path)
            videos.append(video)
        return videos

    def get_videos_force(self) -> List[VideoList]:
        video_cache.pop("videos")
        return self.get_videos()

    def get_video(self, path: str) -> VideoDetail:
        nfo_path = nfo.get_nfo_path_by_video(path)
        detail = nfo.get_full(nfo_path)
        if not detail:
            detail = VideoDetail(path=path)
        return detail

    def get_video_by_num(self, num: str) -> Optional[VideoDetail]:
        """通过番号获取视频详情

        Args:
            num: 视频番号

        Returns:
            VideoDetail: 视频详情，如果找不到则返回None
        """
        try:
            # 首先尝试在NFO文件中查找
            videos = self.get_videos()
            for video in videos:
                if video.num == num:
                    return self.get_video(video.path)

            # 如果在本地找不到，尝试从网络获取
            try:
                from app.service.home import HomeService

                home_service = HomeService(self.db)
                detail = home_service.get_ranking_detail(num=num)
                if detail:
                    return VideoDetail(**detail.dict())
            except:
                pass

            return None
        except Exception as e:
            logger.error(f"通过番号获取视频详情失败: {e}")
            return None

    def search_videos_by_actor(self, actor_name: str) -> List[VideoList]:
        """根据演员名称搜索视频列表"""
        if not actor_name:
            logger.info(f"搜索演员为空")
            return []

        logger.info(f"搜索演员：{actor_name}")
        videos = self.get_videos()
        logger.info(f"获取到视频数量：{len(videos)}")

        actor_name = actor_name.lower()

        result = []
        for video in videos:
            # 检查video.actors是否为None或空列表
            if not video.actors:
                continue

            for actor in video.actors:
                if actor.name and actor_name in actor.name.lower():
                    result.append(video)
                    logger.info(f"找到匹配视频：{video.title}, 演员：{actor.name}")
                    break

        logger.info(f"搜索结果数量：{len(result)}")
        return result

    def get_all_actors(self) -> List[VideoActor]:
        """获取所有演员列表，用于搜索建议"""
        videos = self.get_videos()
        logger.info(f"获取到视频数量：{len(videos)}")

        # 使用集合去重
        actors_set = set()
        actors = []

        for video in videos:
            # 检查video.actors是否为None或空列表
            if not video.actors:
                continue

            for actor in video.actors:
                if actor.name and actor.name not in actors_set:
                    actors_set.add(actor.name)
                    actors.append(actor)

        result = sorted(actors, key=lambda x: x.name)
        logger.info(f"获取到演员数量：{len(result)}")
        return result

    def parse_video(self, path: str):
        if not os.path.exists(path):
            raise BizException("视频不存在")
        return num_parser.parse(path)

    def scrape_video(self, num: str):
        # 使用新的并发刮削服务（带配置开关）
        video = get_video_info_with_config(num)
        if not video:
            raise BizException("未找到该番号")

        cache.clean_cache_file("cover", video.cover)
        for actor in video.actors:
            cache.clean_cache_file("cover", actor.thumb)

        return video

    def save_video(
        self,
        video: VideoDetail,
        mode: Optional[str] = None,
        trans_mode: Optional[str] = None,
    ):
        setting = Setting()
        if trans_mode is None:
            if mode == "file":
                trans_mode = setting.file.trans_mode
            elif mode == "download":
                trans_mode = setting.download.trans_mode
            else:
                trans_mode = "move"
        source_path = video.path
        if not os.path.exists(source_path):
            raise BizException("视频不存在")

        video_notify = VideoNotify(**video.model_dump())
        video_notify.mode = mode
        video_notify.trans_mode = trans_mode
        try:
            video_notify.size = utils.convert_size(os.stat(source_path).st_size)
        except FileNotFoundError:
            raise BizException("视频不存在")

        dest_path = self.trans(video, setting.app.video_path, trans_mode)
        if dest_path != source_path:
            history = History(
                status=1,
                num=video.num,
                is_zh=video.is_zh,
                is_uncensored=video.is_uncensored,
                source_path=source_path,
                dest_path=dest_path,
                trans_method=trans_mode,
            )
            history.add(self.db)
            self.db.commit()

            video_notify.is_success = True
            notify.send_video(video_notify)

        video_cache.pop("videos", None)

    def trans(self, video: VideoDetail, video_path: str, trans_mode: str):
        if not os.path.exists(video.path):
            raise BizException("视频不存在")

        _, ext_name = os.path.splitext(video.path)

        if trans_mode == "move":
            self.delete_video_meta(video.path)

        actor_folder = (
            (
                ",".join(map(lambda i: i.name, video.actors[0:3]))
                + ("等" if len(video.actors) > 3 else "")
            )
            if len(video.actors) > 0
            else "未知演员"
        )
        video_folder = video.title[0:80]
        save_path = os.path.join(video_path, actor_folder, video_folder)
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        video_tags = []
        if video.is_uncensored:
            video_tags.append("U")
        if video.is_zh:
            video_tags.append("C")

        video_path = os.path.join(
            save_path,
            video.num + (f"-{''.join(video_tags)}" if video_tags else "") + ext_name,
        )

        if video_path != video.path:
            if (
                os.path.exists(video_path)
                and os.stat(video_path).st_size != os.stat(video.path).st_size
            ):
                if trans_mode == "move":
                    os.remove(video.path)
            else:
                if trans_mode == "move":
                    logger.info(f"开始移动影片《{video.num}》...")
                    shutil.move(video.path, video_path)
                    logger.info(f"移动影片完成: {video_path}")
                else:
                    logger.info(f"开始复制影片...")
                    shutil.copy(video.path, video_path)
                    logger.info(f"复制影片完成: {video_path}")
            utils.remove_empty_directory(video.path)

        if video.cover:
            logger.info(f"生成封面及水印图片")
            save_images(video, video_path)

        logger.info(f"生成NFO文件")
        new_nfo_path = nfo.get_nfo_path_by_video(video_path)
        nfo.save(new_nfo_path, video)
        shutil.copy(new_nfo_path, os.path.join(save_path, "movie.nfo"))

        logger.info(f"影片保存完成")
        return video_path

    def delete_video(self, path):
        if not os.path.exists(path):
            raise BizException("视频不存在")
        self.delete_video_meta(path)
        os.remove(path)
        utils.remove_empty_directory(path)

        video_cache.pop("videos", None)

    def delete_video_meta(self, path):
        nfo_path = nfo.get_nfo_path_by_video(path)
        movie_nfo_path = os.path.join(os.path.split(nfo_path)[0], "movie.nfo")
        exist = nfo.get_full(nfo_path)
        if exist:
            if os.path.exists(nfo_path):
                os.remove(nfo_path)
            if os.path.exists(movie_nfo_path):
                os.remove(movie_nfo_path)
            exist_path, _ = os.path.split(path)
            for item in ["poster", "thumb", "fanart"]:
                image = getattr(exist, item)
                if not image or not isinstance(image, str):
                    continue
                image_path = (
                    image if os.path.isabs(image) else os.path.join(exist_path, image)
                )
                if os.path.exists(image_path):
                    os.remove(image_path)
