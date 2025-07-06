import os

from fastapi import Depends
from requests import Session

from app import utils
from app.db import get_db, SessionFactory
from app.db.models import History, Torrent as DBTorrent
from app.exception import BizException
from app.schema import Torrent, TorrentFile, Setting, VideoNotify, VideoDetail
from app.service.base import BaseService
from app.service.video import VideoService
from app.utils import notify
from app.utils.logger import logger
from app.utils.qbittorent import qbittorent


def get_download_service(db: Session = Depends(get_db)):
    return DownloadService(db=db)


class DownloadService(BaseService):

    def __init__(self, db: Session):
        super().__init__(db)
        self.setting = Setting()
        self.qb = qbittorent

    def get_downloads(self, include_success=True, include_failed=True):
        if not self.setting.download.host:
            return []

        category = self.setting.download.category if self.setting.download.category else None
        infos = self.qb.get_torrents(category, include_success=include_success, include_failed=include_failed)
        torrents = []
        for info in infos:
            torrent = Torrent(hash=info['hash'], name=info['name'], size=utils.convert_size(info['total_size']),
                              path=info['save_path'], tags=list(map(lambda i: i.strip(), info['tags'].split(','))))
            files = self.qb.get_torrent_files(info['hash'])
            
            # 检查是否有任何文件
            if not files:
                # 如果没有文件信息，仍然添加种子但不添加文件
                torrents.append(torrent)
                continue
                
            # 处理文件列表
            for file in files:
                # 允许显示任何优先级不为0的文件，无论下载进度如何
                if file['priority'] == 0:
                    continue
                    
                _, ext_name = os.path.splitext(file['name'])
                name = file['name'].split('/')[-1]
                size = file['size']
                path = info['content_path'] if len(files) == 1 else os.path.join(info['save_path'],
                                                                                 file['name'])

                if path.startswith(self.setting.download.download_path):
                    path = path.replace(self.setting.download.download_path, self.setting.download.mapping_path, 1)

                # 仍然只显示视频文件
                if ext_name in self.setting.app.video_format.split(',') and size > (
                        self.setting.app.video_size_minimum * 1024 * 1024):
                    # 添加进度信息
                    progress = file.get('progress', 0)
                    
                    # 尝试获取番号和演员信息
                    num = None
                    actors = None
                    try:
                        # 首先检查是否有匹配的种子记录
                        matched_torrent = self.db.query(DBTorrent).filter_by(hash=info['hash']).one_or_none()
                        if matched_torrent is not None:
                            num = matched_torrent.num
                        else:
                            # 尝试从文件路径解析番号
                            video_service = VideoService(self.db)
                            video_info = video_service.parse_video(path)
                            if video_info and video_info.num:
                                num = video_info.num
                                
                                # 如果有番号，尝试获取演员信息
                                try:
                                    video_detail = video_service.get_video_by_num(num)
                                    if video_detail and video_detail.actors:
                                        actors = [actor.name for actor in video_detail.actors]
                                except:
                                    # 如果获取演员信息失败，忽略错误
                                    pass
                    except:
                        # 如果解析失败，忽略错误
                        pass
                    
                    file_info = TorrentFile(
                        name=name, 
                        size=utils.convert_size(size), 
                        path=path,
                        progress=progress,
                        num=num,
                        actors=actors
                    )
                    torrent.files.append(file_info)
            
            # 只有当种子包含文件时才添加到列表中
            if torrent.files or not files:
                torrents.append(torrent)
                
        return torrents

    def complete_download(self, torrent_hash: str, is_success: bool = True):
        self.qb.add_torrent_tags(torrent_hash, ['整理成功' if is_success else '整理失败'])
        
        # 如果设置了完成后停止做种，则暂停种子
        if is_success and self.setting.download.stop_seeding:
            try:
                self.qb.pause_torrent(torrent_hash)
                logger.info(f"种子已暂停做种: {torrent_hash}")
            except Exception as e:
                logger.error(f"暂停种子做种失败: {torrent_hash}, 错误: {e}")

    def delete_download(self, torrent_hash: str):
        self.qb.delete_torrent(torrent_hash)

    @classmethod
    def job_scrape_download(cls):
        setting = Setting()
        with SessionFactory() as db:
            download_service = DownloadService(db=db)
            video_service = VideoService(db=db)
            torrents = download_service.get_downloads(include_failed=True, include_success=True)
            logger.info(f"获取到{len(torrents)}个下载任务")
            for torrent in torrents:
                if any(tag in ["整理成功", "整理失败"] for tag in torrent.tags):
                    continue
                download_service.scrape_download(video_service, torrent, setting.download.trans_mode)
            db.commit()

    def scrape_download(self, video_service: VideoService, torrent: Torrent, trans_mode: str):
        has_error = False
        for file in torrent.files:
            num = None
            video = VideoNotify(path=file.path)
            try:
                matched_torrent = self.db.query(DBTorrent).filter_by(hash=torrent.hash).one_or_none()
                if matched_torrent is not None:
                    match_num = VideoDetail(**matched_torrent.__dict__)
                else:
                    match_num = video_service.parse_video(file.path)

                num = match_num.num
                if num is None:
                    raise BizException(message='番号识别失败')
                video = video_service.scrape_video(num)
                video.path = file.path
                video.is_zh = match_num.is_zh
                video.is_uncensored = match_num.is_uncensored
                video_service.save_video(video, mode='download')

                if matched_torrent is not None:
                    matched_torrent.delete(self.db)
            except BizException as e:
                has_error = True

                history = History(status=0, num=num, is_zh=video.is_zh,
                                  is_uncensored=video.is_uncensored,
                                  source_path=file.path, trans_method=trans_mode)
                history.add(video_service.db)

                video_notify = VideoNotify(**video.model_dump())
                if os.path.exists(file.path):
                    video_notify.size = utils.convert_size(os.stat(file.path).st_size)
                    video_notify.message = e.message
                else:
                    video_notify.size = 'N/A'
                    video_notify.message = '文件不存在'
                video_notify.is_success = False
                logger.error(f"影片刮削失败，{video_notify.message}")
                notify.send_video(video_notify)

        self.complete_download(torrent.hash, not has_error)

    @classmethod
    def job_delete_complete_download(cls):
        with SessionFactory() as db:
            download_service = DownloadService(db=db)
            torrents = download_service.get_downloads(include_success=True, include_failed=False)
            for torrent in torrents:
                if '整理成功' in torrent.tags:
                    download_service.delete_download(torrent.hash)
