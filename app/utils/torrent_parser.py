"""
种子文件解析工具
用于解析torrent文件内容，获取文件列表和大小信息
"""
import os
import re
import hashlib
from typing import List, Dict, Optional, NamedTuple
from urllib.parse import urlparse, parse_qs

from app.utils.logger import logger


class TorrentFile(NamedTuple):
    """种子中的文件信息"""
    name: str              # 文件名
    path: str              # 文件路径
    size: int              # 文件大小(字节)
    extension: str         # 文件扩展名
    is_video: bool         # 是否为视频文件
    is_sample: bool        # 是否为样本文件
    is_subtitle: bool      # 是否为字幕文件


class TorrentInfo(NamedTuple):
    """种子信息"""
    name: str                    # 种子名称
    total_size: int             # 总大小(字节)
    files: List[TorrentFile]    # 文件列表
    hash: str                   # 种子hash
    trackers: List[str]         # tracker列表


class TorrentParser:
    """种子解析器"""
    
    # 视频文件扩展名
    VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.m4v', '.ts', '.m2ts'}
    
    # 字幕文件扩展名
    SUBTITLE_EXTENSIONS = {'.srt', '.ass', '.ssa', '.sub', '.idx', '.vtt', '.smi'}
    
    # 样本文件关键词
    SAMPLE_KEYWORDS = {'sample', 'preview', 'trailer', 'rarbg.to', 'rarbg.txt'}
    
    def __init__(self):
        pass
    
    def parse_magnet_info(self, magnet_url: str) -> Optional[Dict]:
        """
        从磁力链接解析基本信息
        
        Args:
            magnet_url: 磁力链接
            
        Returns:
            dict: 包含hash和名称的信息，如果解析失败返回None
        """
        try:
            if not magnet_url.startswith('magnet:'):
                return None
                
            parsed = urlparse(magnet_url)
            params = parse_qs(parsed.query)
            
            # 提取xt参数中的hash
            xt = params.get('xt', [])
            hash_value = None
            for x in xt:
                if x.startswith('urn:btih:'):
                    hash_value = x[9:].lower()
                    break
            
            if not hash_value:
                return None
                
            # 提取dn参数中的名称
            dn = params.get('dn', [''])[0]
            
            return {
                'hash': hash_value,
                'name': dn or 'Unknown',
                'magnet': magnet_url
            }
        except Exception as e:
            logger.error(f"解析磁力链接失败: {e}")
            return None
    
    def parse_qbittorrent_files(self, qb_files: List[Dict]) -> List[TorrentFile]:
        """
        解析qBittorrent API返回的文件列表
        
        Args:
            qb_files: qBittorrent API返回的文件列表
            
        Returns:
            List[TorrentFile]: 解析后的文件列表
        """
        files = []
        
        for file_info in qb_files:
            try:
                name = file_info.get('name', '')
                size = file_info.get('size', 0)
                
                # 获取文件名和扩展名
                file_name = os.path.basename(name)
                extension = os.path.splitext(file_name)[1].lower()
                
                # 判断文件类型
                is_video = extension in self.VIDEO_EXTENSIONS
                is_subtitle = extension in self.SUBTITLE_EXTENSIONS
                is_sample = self._is_sample_file(name.lower())
                
                torrent_file = TorrentFile(
                    name=file_name,
                    path=name,
                    size=size,
                    extension=extension,
                    is_video=is_video,
                    is_sample=is_sample,
                    is_subtitle=is_subtitle
                )
                
                files.append(torrent_file)
                
            except Exception as e:
                logger.error(f"解析文件信息失败: {file_info}, 错误: {e}")
                continue
        
        return files
    
    def _is_sample_file(self, filename: str) -> bool:
        """
        判断是否为样本文件
        
        Args:
            filename: 文件名（小写）
            
        Returns:
            bool: 是否为样本文件
        """
        # 检查文件名中是否包含样本关键词
        for keyword in self.SAMPLE_KEYWORDS:
            if keyword in filename:
                return True
                
        # 检查是否为RARBG等网站的宣传文件
        if 'rarbg' in filename or 'rargb' in filename:
            return True
            
        # 检查文件大小模式（通常样本文件很小）
        if 'sample' in filename or 'preview' in filename:
            return True
            
        return False
    
    def filter_files_by_size(self, files: List[TorrentFile], min_size_mb: int, 
                           max_size_mb: Optional[int] = None) -> List[TorrentFile]:
        """
        根据文件大小过滤文件
        
        Args:
            files: 文件列表
            min_size_mb: 最小文件大小(MB)
            max_size_mb: 最大文件大小(MB)，None表示无限制
            
        Returns:
            List[TorrentFile]: 过滤后的文件列表
        """
        min_size_bytes = min_size_mb * 1024 * 1024
        max_size_bytes = max_size_mb * 1024 * 1024 if max_size_mb else None
        
        filtered_files = []
        for file in files:
            if file.size < min_size_bytes:
                logger.debug(f"文件 {file.name} 大小 {file.size/1024/1024:.1f}MB 小于最小值 {min_size_mb}MB")
                continue
                
            if max_size_bytes and file.size > max_size_bytes:
                logger.debug(f"文件 {file.name} 大小 {file.size/1024/1024:.1f}MB 大于最大值 {max_size_mb}MB")
                continue
                
            filtered_files.append(file)
        
        return filtered_files
    
    def filter_files_by_type(self, files: List[TorrentFile], 
                           allowed_extensions: Optional[List[str]] = None,
                           blocked_extensions: Optional[List[str]] = None,
                           video_only: bool = False) -> List[TorrentFile]:
        """
        根据文件类型过滤文件
        
        Args:
            files: 文件列表
            allowed_extensions: 允许的扩展名列表
            blocked_extensions: 禁止的扩展名列表
            video_only: 是否只保留视频文件
            
        Returns:
            List[TorrentFile]: 过滤后的文件列表
        """
        filtered_files = []
        
        for file in files:
            # 如果设置了只保留视频文件
            if video_only and not file.is_video:
                continue
                
            # 检查禁止的扩展名
            if blocked_extensions and file.extension in blocked_extensions:
                continue
                
            # 检查允许的扩展名
            if allowed_extensions and file.extension not in allowed_extensions:
                continue
                
            filtered_files.append(file)
            
        return filtered_files
    
    def filter_smart(self, files: List[TorrentFile], 
                    skip_sample_files: bool = True,
                    skip_subtitle_only: bool = True) -> List[TorrentFile]:
        """
        智能过滤文件
        
        Args:
            files: 文件列表
            skip_sample_files: 跳过样本文件
            skip_subtitle_only: 跳过纯字幕文件
            
        Returns:
            List[TorrentFile]: 过滤后的文件列表
        """
        filtered_files = []
        
        for file in files:
            # 跳过样本文件
            if skip_sample_files and file.is_sample:
                logger.debug(f"跳过样本文件: {file.name}")
                continue
                
            # 跳过纯字幕文件（如果设置了跳过且没有对应的视频文件）
            if skip_subtitle_only and file.is_subtitle:
                logger.debug(f"跳过字幕文件: {file.name}")
                continue
                
            filtered_files.append(file)
            
        return filtered_files
    
    def apply_filters(self, files: List[TorrentFile], filter_settings: Dict) -> List[TorrentFile]:
        """
        应用所有过滤规则
        
        Args:
            files: 原始文件列表
            filter_settings: 过滤设置
            
        Returns:
            List[TorrentFile]: 过滤后的文件列表
        """
        filtered_files = files.copy()
        
        logger.info(f"开始过滤，原始文件数: {len(filtered_files)}")
        
        # 1. 智能过滤
        if filter_settings.get('enable_smart_filter', True):
            filtered_files = self.filter_smart(
                filtered_files,
                skip_sample_files=filter_settings.get('skip_sample_files', True),
                skip_subtitle_only=filter_settings.get('skip_subtitle_only', True)
            )
            logger.info(f"智能过滤后文件数: {len(filtered_files)}")
        
        # 2. 文件大小过滤
        min_size = filter_settings.get('min_file_size_mb')
        max_size = filter_settings.get('max_file_size_mb')
        if min_size:
            filtered_files = self.filter_files_by_size(
                filtered_files, 
                min_size_mb=min_size,
                max_size_mb=max_size
            )
            logger.info(f"大小过滤后文件数: {len(filtered_files)}")
        
        # 3. 文件类型过滤
        allowed_ext = filter_settings.get('allowed_extensions')
        blocked_ext = filter_settings.get('blocked_extensions')
        video_only = filter_settings.get('video_only', False)
        
        if allowed_ext or blocked_ext or video_only:
            filtered_files = self.filter_files_by_type(
                filtered_files,
                allowed_extensions=allowed_ext,
                blocked_extensions=blocked_ext,
                video_only=video_only
            )
            logger.info(f"类型过滤后文件数: {len(filtered_files)}")
        
        logger.info(f"过滤完成，最终文件数: {len(filtered_files)}")
        return filtered_files


# 全局实例
torrent_parser = TorrentParser()