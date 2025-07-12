"""
下载过滤服务
处理种子文件过滤相关的业务逻辑
"""
import json
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db import get_db
from app.db.models.download_filter import DownloadFilterSettings
from app.service.base import BaseService
from app.utils.torrent_parser import torrent_parser, TorrentFile
from app.utils.qbittorent import qbittorent
from app.utils.logger import logger


def get_download_filter_service(db: Session = Depends(get_db)):
    return DownloadFilterService(db=db)


class DownloadFilterService(BaseService):
    """下载过滤服务"""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.qb = qbittorent
    
    def get_filter_settings(self) -> Optional[DownloadFilterSettings]:
        """
        获取当前激活的过滤设置
        
        Returns:
            DownloadFilterSettings: 过滤设置，如果不存在返回None
        """
        return self.db.query(DownloadFilterSettings).filter_by(is_active=True).first()
    
    def create_or_update_filter_settings(self, settings_data: Dict) -> DownloadFilterSettings:
        """
        创建或更新过滤设置
        
        Args:
            settings_data: 设置数据
            
        Returns:
            DownloadFilterSettings: 更新后的设置
        """
        # 先禁用所有现有设置
        self.db.query(DownloadFilterSettings).update({"is_active": False})
        
        # 创建新设置
        settings = DownloadFilterSettings(**settings_data)
        settings.is_active = True
        
        self.db.add(settings)
        self.db.commit()
        self.db.refresh(settings)
        
        logger.info(f"更新下载过滤设置: 最小文件大小={settings.min_file_size_mb}MB")
        return settings
    
    def get_default_filter_settings(self) -> Dict:
        """
        获取默认过滤设置
        
        Returns:
            Dict: 默认设置字典
        """
        return {
            "min_file_size_mb": 300,
            "max_file_size_mb": None,
            "allowed_extensions": None,
            "blocked_extensions": None,
            "min_seed_count": 1,
            "max_total_size_gb": None,
            "enable_smart_filter": True,
            "skip_sample_files": True,
            "skip_subtitle_only": True,
            "media_files_only": False,
            "include_subtitles": True
        }
    
    def apply_filter_to_magnet(self, magnet_url: str) -> Dict:
        """
        对磁力链接应用过滤规则
        
        Args:
            magnet_url: 磁力链接
            
        Returns:
            Dict: 过滤结果，包含是否应该下载、过滤的文件等信息
        """
        result = {
            "should_download": False,
            "total_files": 0,
            "filtered_files": 0,
            "filtered_size_mb": 0,
            "filter_reason": "",
            "files": []
        }
        
        try:
            # 获取过滤设置
            filter_settings = self.get_filter_settings()
            if not filter_settings:
                result["filter_reason"] = "未找到过滤设置"
                return result
            
            # 解析磁力链接基本信息
            magnet_info = torrent_parser.parse_magnet_info(magnet_url)
            if not magnet_info:
                result["filter_reason"] = "无法解析磁力链接"
                return result
            
            # 检查种子是否已存在于qBittorrent中
            if self.qb.is_magnet_exists(magnet_url):
                logger.info(f"种子已存在，尝试获取文件列表进行过滤分析")
                
                # 获取种子hash
                torrent_hash = magnet_info["hash"]
                
                # 从qBittorrent获取文件列表
                qb_files = self.qb.get_torrent_files(torrent_hash)
                if not qb_files:
                    result["filter_reason"] = "无法获取种子文件列表"
                    return result
                
                # 解析文件列表
                files = torrent_parser.parse_qbittorrent_files(qb_files)
                result["total_files"] = len(files)
                
                # 应用过滤规则
                filtered_files = self._apply_filter_rules(files, filter_settings)
                result["filtered_files"] = len(filtered_files)
                result["filtered_size_mb"] = sum(f.size for f in filtered_files) / (1024 * 1024)
                result["files"] = [self._file_to_dict(f) for f in filtered_files]
                
                # 判断是否应该下载
                if len(filtered_files) > 0:
                    result["should_download"] = True
                    result["filter_reason"] = f"通过过滤，保留{len(filtered_files)}个文件"
                else:
                    result["filter_reason"] = "所有文件都被过滤掉"
            else:
                # 种子不存在，需要先添加然后分析
                result["filter_reason"] = "种子不存在于下载器中，建议先添加后分析"
                
        except Exception as e:
            logger.error(f"应用过滤规则时出错: {e}")
            result["filter_reason"] = f"过滤时发生错误: {str(e)}"
        
        return result
    
    def filter_torrent_files(self, torrent_hash: str) -> Dict:
        """
        对已存在的种子应用过滤规则
        
        Args:
            torrent_hash: 种子hash
            
        Returns:
            Dict: 过滤结果
        """
        result = {
            "success": False,
            "message": "",
            "original_files": 0,
            "filtered_files": 0,
            "filtered_size_mb": 0,
            "files": []
        }
        
        try:
            # 获取过滤设置
            filter_settings = self.get_filter_settings()
            if not filter_settings:
                result["message"] = "未找到过滤设置"
                return result
            
            # 从qBittorrent获取文件列表
            qb_files = self.qb.get_torrent_files(torrent_hash)
            if not qb_files:
                result["message"] = "无法获取种子文件列表"
                return result
            
            # 解析文件列表
            files = torrent_parser.parse_qbittorrent_files(qb_files)
            result["original_files"] = len(files)
            
            # 应用过滤规则
            filtered_files = self._apply_filter_rules(files, filter_settings)
            result["filtered_files"] = len(filtered_files)
            result["filtered_size_mb"] = sum(f.size for f in filtered_files) / (1024 * 1024)
            result["files"] = [self._file_to_dict(f) for f in filtered_files]
            
            # 在qBittorrent中设置文件优先级
            self._set_file_priorities(torrent_hash, files, filtered_files)
            
            result["success"] = True
            result["message"] = f"过滤完成，保留{len(filtered_files)}/{len(files)}个文件"
            
        except Exception as e:
            logger.error(f"过滤种子文件时出错: {e}")
            result["message"] = f"过滤时发生错误: {str(e)}"
        
        return result
    
    def _apply_filter_rules(self, files: List[TorrentFile], 
                          filter_settings: DownloadFilterSettings) -> List[TorrentFile]:
        """
        应用过滤规则
        
        Args:
            files: 文件列表
            filter_settings: 过滤设置
            
        Returns:
            List[TorrentFile]: 过滤后的文件列表
        """
        # 构建过滤参数
        filter_params = {
            "min_file_size_mb": filter_settings.min_file_size_mb,
            "max_file_size_mb": filter_settings.max_file_size_mb,
            "enable_smart_filter": filter_settings.enable_smart_filter,
            "skip_sample_files": filter_settings.skip_sample_files,
            "skip_subtitle_only": filter_settings.skip_subtitle_only,
            "media_files_only": getattr(filter_settings, 'media_files_only', False),
            "include_subtitles": getattr(filter_settings, 'include_subtitles', True),
            "video_only": not getattr(filter_settings, 'media_files_only', False),  # 如果启用媒体文件模式则不使用video_only
        }
        
        # 处理扩展名设置
        if filter_settings.allowed_extensions:
            try:
                filter_params["allowed_extensions"] = json.loads(filter_settings.allowed_extensions)
            except:
                pass
                
        if filter_settings.blocked_extensions:
            try:
                filter_params["blocked_extensions"] = json.loads(filter_settings.blocked_extensions)
            except:
                pass
        
        # 应用过滤
        filtered_files = torrent_parser.apply_filters(files, filter_params)
        
        return filtered_files
    
    def _set_file_priorities(self, torrent_hash: str, all_files: List[TorrentFile], 
                           filtered_files: List[TorrentFile]):
        """
        在qBittorrent中设置文件下载优先级
        
        Args:
            torrent_hash: 种子hash
            all_files: 所有文件列表
            filtered_files: 过滤后的文件列表
        """
        try:
            # 获取要保留的文件路径集合
            keep_paths = {f.path for f in filtered_files}
            
            # 构建优先级列表：保留的文件设为正常优先级(1)，其他设为不下载(0)
            priorities = []
            for file in all_files:
                if file.path in keep_paths:
                    priorities.append(1)  # 正常下载
                else:
                    priorities.append(0)  # 不下载
            
            # 调用qBittorrent API设置文件优先级
            response = self.qb.set_files_priority_bulk(torrent_hash, priorities)
            
            if hasattr(response, 'status_code') and response.status_code == 200:
                logger.info(f"种子 {torrent_hash}: 成功设置文件优先级，保留 {len(filtered_files)}/{len(all_files)} 个文件")
            else:
                logger.warning(f"种子 {torrent_hash}: 设置文件优先级响应异常")
            
        except Exception as e:
            logger.error(f"设置文件优先级失败: {e}")
    
    def _file_to_dict(self, file: TorrentFile) -> Dict:
        """
        将TorrentFile转换为字典
        
        Args:
            file: TorrentFile对象
            
        Returns:
            Dict: 文件信息字典
        """
        return {
            "name": file.name,
            "path": file.path,
            "size": file.size,
            "size_mb": round(file.size / (1024 * 1024), 2),
            "extension": file.extension,
            "is_video": file.is_video,
            "is_sample": file.is_sample,
            "is_subtitle": file.is_subtitle
        }
    
    def get_filter_statistics(self) -> Dict:
        """
        获取过滤统计信息
        
        Returns:
            Dict: 统计信息
        """
        # 这里可以添加统计逻辑，比如过滤的文件数量、节省的空间等
        return {
            "total_filtered_torrents": 0,
            "total_saved_space_gb": 0,
            "most_common_filtered_types": []
        }