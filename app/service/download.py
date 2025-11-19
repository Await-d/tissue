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
from app.service.download_filter import DownloadFilterService
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
        self.filter_service = DownloadFilterService(db)

    def get_downloads(self, include_success=True, include_failed=True):
        logger.info(f"开始获取下载列表，参数: include_success={include_success}, include_failed={include_failed}")
        
        if not self.setting.download.host:
            logger.warning("qBittorrent主机地址未配置，请在设置页面配置下载器连接信息")
            return []

        logger.info(f"qBittorrent配置 - 主机: {self.setting.download.host}, 用户名: {self.setting.download.username}, 分类: {self.setting.download.category}")
        
        try:
            # 先测试qBittorrent连接
            test_result = self.qb.test_connection()
            logger.info(f"qBittorrent连接测试结果: {test_result}")
            if not test_result.get('status', False):
                logger.error(f"qBittorrent连接失败: {test_result.get('message', 'Unknown error')}")
                return []
            
            # 获取所有种子信息
            logger.info("开始获取所有种子信息...")
            response = self.qb.get_all_torrents()
            
            # 检查响应类型并处理
            if hasattr(response, 'json'):
                # 这是HTTP响应对象
                if response.status_code != 200:
                    logger.error(f"qBittorrent API返回错误状态: {response.status_code}")
                    return []
                infos = response.json()
            else:
                # 这是直接的列表数据
                infos = response
                
            logger.info(f"从qBittorrent获取到 {len(infos)} 个种子")
            
            if len(infos) > 0:
                # 打印前几个种子的基本信息用于调试
                for i, info in enumerate(infos[:3]):
                    logger.info(f"种子{i+1}: {info.get('name', 'Unknown')} - 状态: {info.get('state', 'Unknown')} - 标签: {info.get('tags', '')}")
            
            category = self.setting.download.category if self.setting.download.category else None
            
            # 如果设置了分类，则过滤分类
            if category:
                original_count = len(infos)
                infos = [info for info in infos if info.get('category') == category]
                logger.info(f"按分类'{category}'过滤后: {len(infos)} 个种子 (原来 {original_count} 个)")
            
            # 根据参数决定是否包含已处理的种子
            if not include_failed:
                original_count = len(infos)
                infos = [info for info in infos if "整理失败" not in info.get("tags", "")]
                logger.info(f"排除失败种子后: {len(infos)} 个种子 (原来 {original_count} 个)")
            
            if not include_success:
                original_count = len(infos)
                infos = [info for info in infos if "整理成功" not in info.get("tags", "")]
                logger.info(f"排除成功种子后: {len(infos)} 个种子 (原来 {original_count} 个)")
                
        except Exception as e:
            logger.error(f"获取种子列表失败: {str(e)}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return []
        torrents = []
        for info in infos:
            torrent = Torrent(hash=info['hash'], name=info['name'], size=utils.convert_size(info['total_size']),
                              path=info['save_path'], tags=list(map(lambda i: i.strip(), info['tags'].split(','))))
            files_response = self.qb.get_torrent_files(info['hash'])
            files = files_response.json() if hasattr(files_response, 'json') else files_response
            
            # 检查是否有任何文件
            if not files:
                # 如果没有文件信息，仍然添加种子但不添加文件
                torrents.append(torrent)
                continue
                
            # 使用新的过滤系统处理文件列表
            filter_result = self.filter_service.filter_torrent_files(info['hash'])
            if filter_result['success']:
                # 获取过滤后的文件列表
                filtered_files = filter_result['files']
                logger.debug(f"种子 {info['hash']} 过滤结果: {len(filtered_files)} 个文件通过过滤")
                
                # 创建文件路径到qb文件信息的映射
                qb_files_map = {file['name']: file for file in files}
                
                for filtered_file in filtered_files:
                    # 查找对应的qBittorrent文件信息
                    qb_file = qb_files_map.get(filtered_file['path'])
                    if not qb_file:
                        continue
                    
                    # 允许显示任何优先级不为0的文件，无论下载进度如何
                    if qb_file['priority'] == 0:
                        continue
                    
                    name = filtered_file['name']
                    size = filtered_file['size']
                    path = info['content_path'] if len(files) == 1 else os.path.join(info['save_path'], filtered_file['path'])

                    if path.startswith(self.setting.download.download_path):
                        path = path.replace(self.setting.download.download_path, self.setting.download.mapping_path, 1)

                    # 文件已经通过过滤系统筛选，直接处理
                    # 添加进度信息
                    progress = qb_file.get('progress', 0)
                    
                    # 尝试获取番号和演员信息
                    num = None
                    actors = None
                    try:
                        # 首先检查是否有匹配的种子记录
                        matched_torrent = self.db.query(DBTorrent).filter_by(hash=info['hash']).order_by(
                            DBTorrent.id.desc()).limit(1).one_or_none()
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
            else:
                # 如果过滤失败，使用旧的逻辑作为备用
                logger.warning(f"种子 {info['hash']} 过滤失败: {filter_result.get('message', 'Unknown error')}，使用备用逻辑")
                for file in files:
                    # 允许显示任何优先级不为0的文件，无论下载进度如何
                    if file['priority'] == 0:
                        continue
                        
                    _, ext_name = os.path.splitext(file['name'])
                    name = file['name'].split('/')[-1]
                    size = file['size']
                    path = info['content_path'] if len(files) == 1 else os.path.join(info['save_path'], file['name'])

                    if path.startswith(self.setting.download.download_path):
                        path = path.replace(self.setting.download.download_path, self.setting.download.mapping_path, 1)

                    # 仍然只显示视频文件，使用基本的大小检查
                    if ext_name in self.setting.app.video_format.split(',') and size > (300 * 1024 * 1024):
                        # 添加进度信息
                        progress = file.get('progress', 0)
                        
                        file_info = TorrentFile(
                            name=name, 
                            size=utils.convert_size(size), 
                            path=path,
                            progress=progress,
                            num=None,
                            actors=None
                        )
                        torrent.files.append(file_info)
            
            # 只有当种子包含文件时才添加到列表中
            if torrent.files or not files:
                torrents.append(torrent)
        
        logger.info(f"最终返回 {len(torrents)} 个下载任务")
        for i, torrent in enumerate(torrents[:3]):  # 只显示前3个作为示例
            logger.info(f"下载任务 {i+1}: {torrent.name} ({len(torrent.files)} 个文件)")
        
        return torrents

    def complete_download(self, torrent_hash: str, is_success: bool = True):
        self.qb.add_torrent_tags(torrent_hash, ['整理成功' if is_success else '整理失败'])
        
        # 如果设置了完成后停止做种，则停止种子
        if is_success and self.setting.download.stop_seeding:
            try:
                self.qb.stop_torrent(torrent_hash)
                logger.info(f"种子已停止做种: {torrent_hash}")
            except Exception as e:
                logger.error(f"停止种子做种失败: {torrent_hash}, 错误: {e}")

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
                matched_torrent = self.db.query(DBTorrent).filter_by(hash=torrent.hash).order_by(
                    DBTorrent.id.desc()).limit(1).one_or_none()
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
                    # 删除所有匹配的种子记录以避免重复
                    self.db.query(DBTorrent).filter_by(hash=torrent.hash).delete()
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

    @classmethod
    def job_stop_seeding_completed(cls):
        """检查已完成种子并停止做种的定时任务"""
        try:
            logger.info("开始检查已完成种子并停止做种...")
            with SessionFactory() as db:
                download_service = DownloadService(db=db)
                
                # 检查设置是否启用停止做种功能
                if not download_service.setting.download.stop_seeding:
                    logger.info("停止做种功能未启用，跳过检查")
                    return
                
                try:
                    # 获取qBittorrent中的所有种子
                    response = download_service.qb.get_all_torrents()
                    if hasattr(response, 'json'):
                        torrents = response.json() if response.status_code == 200 else []
                    else:
                        torrents = response
                    
                    stopped_count = 0
                    deleted_count = 0
                    checked_count = 0
                    
                    for torrent in torrents:
                        # 只处理指定分类的种子（如果有设置分类）
                        category = download_service.setting.download.category
                        if category and torrent.get('category') != category:
                            continue
                            
                        checked_count += 1
                        
                        # 检查种子状态：已完成下载且标记为整理成功，但仍在做种
                        state = torrent.get('state', '')
                        tags = torrent.get('tags', '')
                        progress = torrent.get('progress', 0)
                        name = torrent.get('name', 'Unknown')[:50]  # 截取前50个字符
                        
                        # 条件检查
                        is_completed = progress >= 1.0  # 下载进度100%
                        is_organized = '整理成功' in tags  # 已整理成功
                        is_seeding = state in ['uploading', 'stalledUP', 'queuedUP', 'forcedUP']  # 正在做种
                        
                        # 检查是否为丢失文件的种子
                        is_missing_files = state in ['missingFiles', 'error']
                        
                        # 输出详细调试信息（只显示前5个作为示例）
                        if checked_count <= 5:
                            logger.info(f"种子{checked_count}: {name}")
                            logger.info(f"  状态: {state}, 进度: {progress:.1%}, 标签: {tags}")
                            logger.info(f"  检查结果: 完成={is_completed}, 已整理={is_organized}, 做种中={is_seeding}, 丢失文件={is_missing_files}")
                        
                        # 处理丢失文件的种子
                        
                        if is_missing_files:
                            try:
                                # 删除丢失文件的种子（包括数据）
                                download_service.qb.delete_torrent(torrent['hash'], delete_files=True)
                                deleted_count += 1
                                logger.info(f"已删除丢失文件种子: {name} (hash: {torrent['hash'][:8]}...)")
                            except Exception as e:
                                logger.error(f"删除丢失文件种子失败: {name} - {str(e)}")
                            continue  # 跳过后续的停止做种检查
                        
                        # 修改条件：已完成下载 且 (已整理成功 或 没有整理相关标签) 且 正在做种
                        # 这样可以处理那些完成但还未整理的种子
                        has_organize_tag = '整理成功' in tags or '整理失败' in tags
                        should_stop = is_completed and is_seeding and (is_organized or not has_organize_tag)
                        
                        if should_stop:
                            try:
                                # 停止种子以停止做种
                                download_service.qb.stop_torrent(torrent['hash'])
                                stopped_count += 1
                                logger.info(f"已停止种子做种: {torrent.get('name', 'Unknown')} (hash: {torrent['hash'][:8]}...)")
                            except Exception as e:
                                logger.error(f"停止种子做种失败: {torrent.get('name', 'Unknown')} - {str(e)}")
                    
                    # 输出统计结果
                    result_messages = []
                    if stopped_count > 0:
                        result_messages.append(f"停止了 {stopped_count} 个种子的做种")
                    if deleted_count > 0:
                        result_messages.append(f"删除了 {deleted_count} 个丢失文件的种子")
                    
                    if result_messages:
                        logger.info(f"定时检查完成：检查了 {checked_count} 个种子，" + "，".join(result_messages))
                    else:
                        logger.info(f"定时检查完成：检查了 {checked_count} 个种子，无需处理的种子")
                        
                except Exception as e:
                    logger.error(f"获取qBittorrent种子列表失败: {str(e)}")
                    
        except Exception as e:
            logger.error(f"执行停止做种检查任务时出错: {str(e)}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")

    def get_torrent_files(self, torrent_hash: str):
        """
        获取种子的文件列表
        
        Args:
            torrent_hash: 种子哈希
            
        Returns:
            list: 文件列表，每个文件包含 name, path, size, progress, priority
        """
        try:
            files_response = self.qb.get_torrent_files(torrent_hash)
            files = files_response.json() if hasattr(files_response, 'json') else files_response
            
            if not files:
                return []
            
            result = []
            for index, file in enumerate(files):
                file_info = {
                    'index': index,
                    'name': file['name'].split('/')[-1],
                    'path': file['name'],
                    'size': file['size'],
                    'size_formatted': utils.convert_size(file['size']),
                    'progress': file.get('progress', 0),
                    'priority': file.get('priority', 1),
                    'is_seed': file.get('is_seed', False)
                }
                result.append(file_info)
            
            return result
            
        except Exception as e:
            logger.error(f"获取种子文件列表失败: {e}")
            raise

    def set_files_priority(self, torrent_hash: str, file_indices: list, priority: int):
        """
        设置文件下载优先级
        
        Args:
            torrent_hash: 种子哈希
            file_indices: 文件索引列表
            priority: 优先级 (0=不下载, 1=正常, 6=高, 7=最高)
            
        Returns:
            dict: 操作结果
        """
        try:
            # 验证优先级值
            valid_priorities = [0, 1, 6, 7]
            if priority not in valid_priorities:
                raise ValueError(f"无效的优先级值: {priority}，有效值为: {valid_priorities}")
            
            # 调用 qBittorrent API 设置优先级
            result = self.qb.set_files_priority_bulk(torrent_hash, file_indices, priority)
            
            priority_names = {0: '不下载', 1: '正常', 6: '高', 7: '最高'}
            logger.info(f"已设置种子 {torrent_hash} 的 {len(file_indices)} 个文件优先级为: {priority_names.get(priority, priority)}")
            
            return {
                'success': True,
                'updated_files': len(file_indices),
                'priority': priority,
                'priority_name': priority_names.get(priority, str(priority))
            }
            
        except Exception as e:
            logger.error(f"设置文件优先级失败: {e}")
            raise

    def apply_filter_to_torrent(self, torrent_hash: str):
        """
        对指定种子应用全局过滤规则
        
        Args:
            torrent_hash: 种子哈希
            
        Returns:
            dict: 过滤结果
        """
        try:
            filter_result = self.filter_service.filter_torrent_files(torrent_hash)
            return filter_result
        except Exception as e:
            logger.error(f"应用过滤规则失败: {e}")
            raise

    def pause_torrent(self, torrent_hash: str):
        """
        暂停种子下载
        
        Args:
            torrent_hash: 种子哈希
        """
        try:
            self.qb.pause_torrent(torrent_hash)
            logger.info(f"已暂停种子: {torrent_hash}")
        except Exception as e:
            logger.error(f"暂停种子失败: {e}")
            raise

    def resume_torrent(self, torrent_hash: str):
        """
        恢复种子下载
        
        Args:
            torrent_hash: 种子哈希
        """
        try:
            self.qb.resume_torrent(torrent_hash)
            logger.info(f"已恢复种子: {torrent_hash}")
        except Exception as e:
            logger.error(f"恢复种子失败: {e}")
            raise

    def delete_torrent(self, torrent_hash: str, delete_files: bool = False):
        """
        删除种子
        
        Args:
            torrent_hash: 种子哈希
            delete_files: 是否同时删除文件
        """
        try:
            self.qb.delete_torrent(torrent_hash, delete_files=delete_files)
            logger.info(f"已删除种子: {torrent_hash}" + ("（包含文件）" if delete_files else ""))
        except Exception as e:
            logger.error(f"删除种子失败: {e}")
            raise
