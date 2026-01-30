"""
下载过滤服务
处理种子文件过滤相关的业务逻辑
"""

import json
import os
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

    def create_or_update_filter_settings(
        self, settings_data: Dict
    ) -> DownloadFilterSettings:
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
            "include_subtitles": True,
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
            "files": [],
        }

        try:
            # 获取过滤设置
            filter_settings = self.get_filter_settings()
            if not filter_settings:
                # 没有过滤设置时，使用默认设置
                logger.info("未找到过滤设置，使用默认设置")
                default_settings = self.get_default_filter_settings()
                from types import SimpleNamespace

                filter_settings = SimpleNamespace(**default_settings)

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
                qb_files_response = self.qb.get_torrent_files(torrent_hash)
                qb_files = (
                    qb_files_response.json()
                    if hasattr(qb_files_response, "json")
                    else qb_files_response
                )
                if not qb_files:
                    result["filter_reason"] = "无法获取种子文件列表"
                    return result

                # 解析文件列表
                files = torrent_parser.parse_qbittorrent_files(qb_files)
                result["total_files"] = len(files)

                # 应用过滤规则
                filtered_files = self._apply_filter_rules(files, filter_settings)
                result["filtered_files"] = len(filtered_files)
                result["filtered_size_mb"] = sum(f.size for f in filtered_files) / (
                    1024 * 1024
                )
                result["files"] = [self._file_to_dict(f) for f in filtered_files]

                # 判断是否应该下载
                if len(filtered_files) > 0:
                    result["should_download"] = True
                    result["filter_reason"] = (
                        f"通过过滤，保留{len(filtered_files)}个文件"
                    )
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
            "files": [],
        }

        try:
            # 获取过滤设置
            filter_settings = self.get_filter_settings()
            if not filter_settings:
                # 没有过滤设置时，使用默认设置继续过滤
                logger.info("未找到过滤设置，使用默认设置")
                default_settings = self.get_default_filter_settings()
                # 创建一个临时的设置对象
                from types import SimpleNamespace

                filter_settings = SimpleNamespace(**default_settings)

            # 从qBittorrent获取文件列表
            qb_files_response = self.qb.get_torrent_files(torrent_hash)
            qb_files = (
                qb_files_response.json()
                if hasattr(qb_files_response, "json")
                else qb_files_response
            )
            if not qb_files:
                result["message"] = "无法获取种子文件列表"
                return result

            # 解析文件列表
            files = torrent_parser.parse_qbittorrent_files(qb_files)
            result["original_files"] = len(files)

            # 应用过滤规则
            filtered_files = self._apply_filter_rules(files, filter_settings)
            result["filtered_files"] = len(filtered_files)
            result["filtered_size_mb"] = sum(f.size for f in filtered_files) / (
                1024 * 1024
            )
            result["files"] = [self._file_to_dict(f) for f in filtered_files]

            # 在qBittorrent中设置文件优先级
            self._set_file_priorities(torrent_hash, qb_files, filtered_files)

            result["success"] = True
            result["message"] = (
                f"过滤完成，保留{len(filtered_files)}/{len(files)}个文件"
            )

        except Exception as e:
            logger.error(f"过滤种子文件时出错: {e}")
            result["message"] = f"过滤时发生错误: {str(e)}"

        return result

    def _apply_filter_rules(
        self, files: List[TorrentFile], filter_settings: DownloadFilterSettings
    ) -> List[TorrentFile]:
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
            "media_files_only": getattr(filter_settings, "media_files_only", False),
            "include_subtitles": getattr(filter_settings, "include_subtitles", True),
            "video_only": not getattr(
                filter_settings, "media_files_only", False
            ),  # 如果启用媒体文件模式则不使用video_only
        }

        # 处理扩展名设置
        if filter_settings.allowed_extensions:
            try:
                filter_params["allowed_extensions"] = json.loads(
                    filter_settings.allowed_extensions
                )
            except:
                pass

        if filter_settings.blocked_extensions:
            try:
                filter_params["blocked_extensions"] = json.loads(
                    filter_settings.blocked_extensions
                )
            except:
                pass

        # 应用过滤
        filtered_files = torrent_parser.apply_filters(files, filter_params)

        return filtered_files

    def _set_file_priorities(
        self, torrent_hash: str, qb_files: List[Dict], filtered_files: List[TorrentFile]
    ):
        """
        在qBittorrent中设置文件下载优先级

        Args:
            torrent_hash: 种子hash
            qb_files: qBittorrent 文件列表（包含 index）
            filtered_files: 过滤后的文件列表
        """
        try:
            # 获取要保留的文件路径集合
            keep_paths = {f.path for f in filtered_files}

            keep_ids: List[int] = []
            skip_ids: List[int] = []

            # 使用 qBittorrent 返回的 index 作为文件 id
            for position, qb_file in enumerate(qb_files):
                file_path = qb_file.get("name") or qb_file.get("path") or ""
                file_index = qb_file.get("index")
                if file_index is None:
                    # 回退到数组位置，避免缺少 index 时无法设置优先级
                    logger.warning(
                        f"种子 {torrent_hash}: 文件缺少 index 字段，使用数组位置作为 id"
                    )
                    file_index = position

                if file_path in keep_paths:
                    keep_ids.append(file_index)
                else:
                    skip_ids.append(file_index)

            # 先将不需要的文件设置为不下载，再将保留的设置为正常下载
            if skip_ids:
                self.qb.set_file_priority(torrent_hash, skip_ids, 0)

            if keep_ids:
                self.qb.set_file_priority(torrent_hash, keep_ids, 1)

            logger.info(
                f"种子 {torrent_hash}: 设置文件优先级完成，保留 {len(keep_ids)}/{len(qb_files)} 个文件"
            )

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
            "is_subtitle": file.is_subtitle,
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
            "most_common_filtered_types": [],
        }

    def cleanup_torrent_files(self, torrent_hash: str, dry_run: bool = True) -> Dict:
        """
        清理种子中不需要的文件（根据过滤规则删除不在保留列表中的文件）

        Args:
            torrent_hash: 种子hash
            dry_run: 是否为模拟运行模式，True时仅返回将被删除的文件列表，不实际删除

        Returns:
            Dict: 清理结果，包含删除的文件列表、释放的空间等信息
        """
        result = {
            "success": False,
            "message": "",
            "torrent_hash": torrent_hash,
            "torrent_name": "",
            "save_path": "",
            "dry_run": dry_run,
            "total_files": 0,
            "kept_files": 0,
            "deleted_files": 0,
            "deleted_size_bytes": 0,
            "deleted_size_mb": 0,
            "files_to_delete": [],
            "files_to_keep": [],
            "errors": [],
        }

        try:
            # 获取种子属性（包含save_path）
            props_response = self.qb.get_torrent_properties(torrent_hash)
            if not props_response or props_response.status_code != 200:
                result["message"] = "无法获取种子属性"
                logger.error(f"种子 {torrent_hash}: 无法获取种子属性")
                return result

            props = props_response.json()
            save_path = props.get("save_path", "")
            result["save_path"] = save_path
            result["torrent_name"] = props.get("name", "")

            if not save_path:
                result["message"] = "种子保存路径为空"
                logger.error(f"种子 {torrent_hash}: 保存路径为空")
                return result

            # 获取过滤设置
            filter_settings = self.get_filter_settings()
            if not filter_settings:
                logger.info("未找到过滤设置，使用默认设置")
                default_settings = self.get_default_filter_settings()
                from types import SimpleNamespace

                filter_settings = SimpleNamespace(**default_settings)

            # 获取种子文件列表
            qb_files_response = self.qb.get_torrent_files(torrent_hash)
            qb_files = (
                qb_files_response.json()
                if hasattr(qb_files_response, "json")
                else qb_files_response
            )
            if not qb_files:
                result["message"] = "无法获取种子文件列表"
                logger.error(f"种子 {torrent_hash}: 无法获取文件列表")
                return result

            # 解析文件列表
            files = torrent_parser.parse_qbittorrent_files(qb_files)
            result["total_files"] = len(files)

            # 应用过滤规则，获取需要保留的文件
            keep_files = self._apply_filter_rules(files, filter_settings)
            keep_paths = {f.path for f in keep_files}

            result["kept_files"] = len(keep_files)
            result["files_to_keep"] = [self._file_to_dict(f) for f in keep_files]

            # 识别需要删除的文件
            files_to_delete = []
            for file in files:
                if file.path not in keep_paths:
                    files_to_delete.append(file)

            result["deleted_files"] = len(files_to_delete)
            result["files_to_delete"] = [self._file_to_dict(f) for f in files_to_delete]
            result["deleted_size_bytes"] = sum(f.size for f in files_to_delete)
            result["deleted_size_mb"] = round(
                result["deleted_size_bytes"] / (1024 * 1024), 2
            )

            logger.info(
                f"种子 {torrent_hash}: 总文件数={len(files)}, 保留={len(keep_files)}, "
                f"待删除={len(files_to_delete)}, 可释放空间={result['deleted_size_mb']}MB, dry_run={dry_run}"
            )

            # 如果不是模拟运行，实际删除文件
            if not dry_run and files_to_delete:
                deleted_count = 0
                for file in files_to_delete:
                    full_path = os.path.join(save_path, file.path)

                    # 安全检查：确保路径在预期的 save_path 内，防止路径遍历攻击
                    abs_full_path = os.path.abspath(full_path)
                    abs_save_path = os.path.abspath(save_path)
                    if not abs_full_path.startswith(abs_save_path):
                        logger.error(f"检测到非法路径，可能是路径遍历攻击: {file.path}")
                        result["errors"].append(f"非法路径: {file.path}")
                        continue

                    try:
                        if os.path.exists(full_path):
                            os.remove(full_path)
                            deleted_count += 1
                            logger.info(f"已删除文件: {full_path}")
                        else:
                            logger.warning(f"文件不存在，跳过: {full_path}")
                            result["errors"].append(f"文件不存在: {file.path}")
                    except PermissionError as e:
                        error_msg = f"权限不足，无法删除: {file.path}"
                        logger.error(f"{error_msg}: {e}")
                        result["errors"].append(error_msg)
                    except OSError as e:
                        error_msg = f"删除文件失败: {file.path}"
                        logger.error(f"{error_msg}: {e}")
                        result["errors"].append(error_msg)

                # 删除完成后重新校验种子
                if deleted_count > 0:
                    try:
                        recheck_response = self.qb.recheck_torrent(torrent_hash)
                        if recheck_response and recheck_response.status_code == 200:
                            logger.info(f"种子 {torrent_hash}: 已触发重新校验")
                        else:
                            logger.warning(f"种子 {torrent_hash}: 重新校验请求失败")
                    except Exception as e:
                        logger.error(f"种子 {torrent_hash}: 触发重新校验失败: {e}")
                        result["errors"].append(f"触发重新校验失败: {str(e)}")

                result["message"] = f"清理完成，删除了 {deleted_count} 个文件"
            else:
                result["message"] = (
                    f"模拟运行完成，将删除 {len(files_to_delete)} 个文件，释放 {result['deleted_size_mb']}MB"
                )

            result["success"] = True

        except Exception as e:
            logger.error(f"清理种子文件时出错: {e}")
            result["message"] = f"清理时发生错误: {str(e)}"
            result["errors"].append(str(e))

        return result

    def cleanup_all_torrents(self, category: str = None, dry_run: bool = True) -> Dict:
        """
        清理所有种子（或指定分类）中不需要的文件

        Args:
            category: 种子分类，如果为None则处理所有种子
            dry_run: 是否为模拟运行模式，True时仅返回将被删除的文件列表，不实际删除

        Returns:
            Dict: 汇总清理结果
        """
        result = {
            "success": False,
            "message": "",
            "dry_run": dry_run,
            "category": category,
            "total_torrents": 0,
            "processed_torrents": 0,
            "failed_torrents": 0,
            "total_deleted_files": 0,
            "total_deleted_size_bytes": 0,
            "total_deleted_size_mb": 0,
            "total_deleted_size_gb": 0,
            "torrent_results": [],
            "errors": [],
        }

        try:
            # 获取种子列表
            torrents_response = self.qb.get_torrents(category=category)
            if not torrents_response or torrents_response.status_code != 200:
                result["message"] = "无法获取种子列表"
                logger.error("cleanup_all_torrents: 无法获取种子列表")
                return result

            torrents = torrents_response.json()
            result["total_torrents"] = len(torrents)

            logger.info(
                f"开始清理种子文件: 总数={len(torrents)}, 分类={category}, dry_run={dry_run}"
            )

            # 遍历每个种子进行清理
            for torrent in torrents:
                torrent_hash = torrent.get("hash", "")
                torrent_name = torrent.get("name", "")

                if not torrent_hash:
                    logger.warning(f"跳过无效种子: {torrent_name}")
                    continue

                try:
                    cleanup_result = self.cleanup_torrent_files(
                        torrent_hash, dry_run=dry_run
                    )

                    # 汇总结果
                    if cleanup_result["success"]:
                        result["processed_torrents"] += 1
                        result["total_deleted_files"] += cleanup_result["deleted_files"]
                        result["total_deleted_size_bytes"] += cleanup_result[
                            "deleted_size_bytes"
                        ]
                    else:
                        result["failed_torrents"] += 1
                        result["errors"].append(
                            f"种子 {torrent_name}: {cleanup_result['message']}"
                        )

                    # 保存每个种子的详细结果
                    result["torrent_results"].append(
                        {
                            "hash": torrent_hash,
                            "name": torrent_name,
                            "success": cleanup_result["success"],
                            "deleted_files": cleanup_result["deleted_files"],
                            "deleted_size_mb": cleanup_result["deleted_size_mb"],
                            "message": cleanup_result["message"],
                        }
                    )

                except Exception as e:
                    result["failed_torrents"] += 1
                    error_msg = f"种子 {torrent_name}: 处理异常 - {str(e)}"
                    logger.error(error_msg)
                    result["errors"].append(error_msg)

            # 计算汇总的大小
            result["total_deleted_size_mb"] = round(
                result["total_deleted_size_bytes"] / (1024 * 1024), 2
            )
            result["total_deleted_size_gb"] = round(
                result["total_deleted_size_bytes"] / (1024 * 1024 * 1024), 2
            )

            result["success"] = True
            result["message"] = (
                f"清理完成: 处理了 {result['processed_torrents']}/{result['total_torrents']} 个种子, "
                f"{'将' if dry_run else '已'}删除 {result['total_deleted_files']} 个文件, "
                f"{'可' if dry_run else '已'}释放 {result['total_deleted_size_gb']}GB"
            )

            logger.info(result["message"])

        except Exception as e:
            logger.error(f"批量清理种子文件时出错: {e}")
            result["message"] = f"批量清理时发生错误: {str(e)}"
            result["errors"].append(str(e))

        return result
