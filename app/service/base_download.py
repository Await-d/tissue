"""
基础下载服务
封装通用的带过滤规则的下载逻辑
"""
import time
import threading
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.service.download_filter import DownloadFilterService
from app.utils.qbittorent import qbittorent
from app.utils.logger import logger


class BaseDownloadService:
    """下载服务基类，封装通用的过滤逻辑"""
    
    def __init__(self, db: Session):
        self.db = db
        self.filter_service = DownloadFilterService(db)
    
    def _check_metadata_ready(self, torrent_hash: str, max_attempts: int = 30) -> bool:
        """
        检查种子元数据是否就绪

        Args:
            torrent_hash: 种子哈希
            max_attempts: 最大尝试次数（默认30次，最多等待50秒）

        Returns:
            bool: 元数据就绪返回True
        """
        for attempt in range(max_attempts):
            try:
                files_response = qbittorent.get_torrent_files(torrent_hash)
                files = files_response.json() if hasattr(files_response, 'json') else files_response
                if files and len(files) > 0:
                    logger.info(f"种子 {torrent_hash} 元数据已就绪，找到 {len(files)} 个文件")
                    return True
            except Exception as e:
                logger.debug(f"检查元数据第 {attempt+1} 次: {e}")

            if attempt < max_attempts - 1:
                # 渐进式等待：前10次1秒，之后2秒
                wait_time = 1 if attempt < 10 else 2
                time.sleep(wait_time)

        logger.warning(f"种子 {torrent_hash} 元数据未就绪，已等待约 {10 + (max_attempts-10)*2} 秒")
        return False
    
    def download_with_filter(self, 
                            magnet: str, 
                            savepath: str,
                            category: Optional[str] = None,
                            skip_filter: bool = False) -> Dict[str, Any]:
        """
        带过滤规则的下载
        
        Args:
            magnet: 磁力链接
            savepath: 保存路径
            category: 分类标签
            skip_filter: 是否跳过过滤（用于兼容旧逻辑）
            
        Returns:
            Dict: {
                'success': bool,
                'torrent_hash': str,
                'message': str,
                'filtered_files': int,
                'total_files': int
            }
        """
        result = {
            'success': False,
            'torrent_hash': None,
            'message': '',
            'filtered_files': 0,
            'total_files': 0
        }
        
        try:
            # 1. 检查种子是否已存在
            if qbittorent.is_magnet_exists(magnet):
                torrent_hash = qbittorent.extract_hash_from_magnet(magnet)
                result['torrent_hash'] = torrent_hash
                
                if skip_filter:
                    result['success'] = True
                    result['message'] = '种子已存在，跳过过滤检查'
                    logger.info(result['message'])
                    return result
                
                # 种子已存在，直接应用过滤规则
                logger.info(f"种子已存在于下载器中: {torrent_hash}，直接应用过滤规则")
                filter_result = self.filter_service.filter_torrent_files(torrent_hash)
                
                result['success'] = filter_result['success']
                result['message'] = filter_result['message']
                result['filtered_files'] = filter_result.get('filtered_files', 0)
                result['total_files'] = filter_result.get('original_files', 0)
                
                if not filter_result['success']:
                    logger.warning(f"过滤规则拒绝: {filter_result['message']}")
                else:
                    # 恢复下载（如果是暂停状态）
                    try:
                        qbittorent.resume_torrent(torrent_hash)
                    except:
                        pass  # 如果已经在下载中，忽略错误
                
                return result
            
            # 2. 添加新种子到下载器（暂停状态）
            logger.info(f"添加新种子到下载器（暂停状态）: {magnet[:50]}...")
            
            # 如果需要跳过过滤，直接正常下载
            add_response = qbittorent.add_magnet(
                magnet, 
                savepath, 
                category=category,
                paused=(not skip_filter)  # 需要过滤时暂停，跳过过滤时直接开始
            )
            
            if add_response.status_code != 200:
                result['message'] = f'添加种子失败: HTTP {add_response.status_code}'
                logger.error(result['message'])
                return result
            
            # 3. 获取种子哈希
            torrent_hash = qbittorent.extract_hash_from_magnet(magnet)
            if not torrent_hash:
                result['message'] = '无法提取种子哈希值'
                logger.error(result['message'])
                return result
            
            result['torrent_hash'] = torrent_hash
            logger.info(f"种子已添加: {torrent_hash}")
            
            # 如果跳过过滤，直接返回成功
            if skip_filter:
                result['success'] = True
                result['message'] = '种子已添加，跳过过滤检查'
                logger.info(result['message'])
                return result
            
            # 4. 等待元数据加载
            logger.info(f"等待种子元数据加载: {torrent_hash}")
            if not self._check_metadata_ready(torrent_hash):
                # 元数据未就绪，使用延迟过滤机制
                logger.warning(f"种子 {torrent_hash} 元数据加载超时，启动延迟过滤任务")

                # 启动后台线程进行延迟过滤
                self._schedule_delayed_filter(torrent_hash)

                # 先恢复下载，过滤会在后台完成
                qbittorent.resume_torrent(torrent_hash)

                result['success'] = True
                result['message'] = '种子已添加，元数据加载中，正在后台应用过滤规则'
                return result
            
            # 5. 应用过滤规则
            logger.info(f"应用过滤规则: {torrent_hash}")
            filter_result = self.filter_service.filter_torrent_files(torrent_hash)
            
            result['filtered_files'] = filter_result.get('filtered_files', 0)
            result['total_files'] = filter_result.get('original_files', 0)
            
            if not filter_result['success']:
                # 过滤失败，删除种子
                logger.warning(f"过滤规则拒绝，删除种子: {filter_result['message']}")
                try:
                    qbittorent.delete_torrent(torrent_hash, delete_files=True)
                    logger.info(f"已删除不符合过滤条件的种子: {torrent_hash}")
                except Exception as e:
                    logger.error(f"删除种子失败: {e}")
                
                result['success'] = False
                result['message'] = f"过滤规则拒绝: {filter_result['message']}"
                return result
            
            # 6. 恢复下载
            logger.info(f"过滤通过，恢复下载: {torrent_hash}")
            qbittorent.resume_torrent(torrent_hash)
            
            result['success'] = True
            result['message'] = filter_result['message']
            logger.info(f"下载任务创建成功: {result['message']}")
            
            return result
            
        except Exception as e:
            result['message'] = f"下载过程发生错误: {str(e)}"
            logger.error(result['message'])
            import traceback
            logger.debug(traceback.format_exc())
            return result
    
    def resume_torrent_if_needed(self, torrent_hash: str):
        """如果种子是暂停状态，则恢复下载"""
        try:
            qbittorent.resume_torrent(torrent_hash)
        except Exception as e:
            logger.debug(f"恢复种子下载失败（可能已在下载中）: {e}")

    def _schedule_delayed_filter(self, torrent_hash: str, max_retries: int = 6):
        """
        延迟应用过滤规则（用于元数据加载慢的情况）

        Args:
            torrent_hash: 种子哈希
            max_retries: 最大重试次数（默认6次，共60秒）
        """
        def delayed_filter():
            logger.info(f"延迟过滤任务启动: {torrent_hash}")

            for retry in range(max_retries):
                time.sleep(10)  # 每10秒重试一次

                try:
                    # 再次检查元数据
                    files_response = qbittorent.get_torrent_files(torrent_hash)
                    files = files_response.json() if hasattr(files_response, 'json') else files_response

                    if files and len(files) > 0:
                        logger.info(f"延迟过滤：种子 {torrent_hash} 元数据已就绪，开始应用过滤")

                        # 暂停下载
                        try:
                            qbittorent.pause_torrent(torrent_hash)
                            time.sleep(1)
                        except Exception as e:
                            logger.warning(f"暂停种子失败: {e}")

                        # 应用过滤
                        filter_result = self.filter_service.filter_torrent_files(torrent_hash)

                        if filter_result['success']:
                            logger.info(f"延迟过滤成功: {filter_result['message']}")
                            # 恢复下载
                            try:
                                qbittorent.resume_torrent(torrent_hash)
                            except Exception as e:
                                logger.error(f"恢复下载失败: {e}")
                        else:
                            logger.error(f"延迟过滤失败: {filter_result['message']}")
                            # 如果过滤失败，删除种子
                            try:
                                qbittorent.delete_torrent(torrent_hash, delete_files=True)
                                logger.info(f"延迟过滤失败，已删除种子: {torrent_hash}")
                            except Exception as e:
                                logger.error(f"删除种子失败: {e}")

                        return  # 成功应用过滤，退出

                except Exception as e:
                    logger.error(f"延迟过滤重试 {retry+1} 失败: {e}")

            logger.error(f"延迟过滤最终失败，种子 {torrent_hash} 将继续下载所有文件")

        # 在后台线程中执行
        thread = threading.Thread(target=delayed_filter, daemon=True)
        thread.start()
        logger.info(f"延迟过滤线程已启动: {torrent_hash}")
