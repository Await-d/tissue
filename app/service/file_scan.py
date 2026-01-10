"""
文件扫描服务

负责扫描本地视频文件夹，识别番号并创建历史记录
"""
import os
from typing import Dict, Optional
from datetime import datetime

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.db.models import History, Torrent, Subscribe, ActorSubscribeDownload
from app.schema import Setting
from app.service.base import BaseService
from app.utils.logger import logger
from app.utils import num_parser


def get_file_scan_service(db: Session = Depends(get_db)):
    """依赖注入：获取文件扫描服务实例"""
    return FileScanService(db=db)


class FileScanService(BaseService):
    """文件扫描服务类"""

    # 支持的视频格式
    SUPPORTED_VIDEO_FORMATS = ['.mp4', '.mkv', '.avi', '.wmv', '.mov', '.flv']

    def __init__(self, db: Session):
        """
        初始化文件扫描服务

        Args:
            db: 数据库会话
        """
        super().__init__(db)
        self.setting = Setting()

    def extract_num_from_filename(self, filename: str) -> Optional[str]:
        """
        从文件名中提取番号

        使用项目现有的 num_parser 模块进行解析

        支持格式：
        - ABC-123
        - abc-123
        - ABC_123
        - abc123
        - ABC-123-C
        - ABC-123-CH
        - xxx.24.02.02

        Args:
            filename: 文件名（包含或不包含扩展名）

        Returns:
            标准化的番号（大写，使用横杠），如果未找到则返回 None
        """
        # 获取文件名（不包含扩展名）
        name_without_ext = os.path.splitext(filename)[0]

        # 使用 num_parser 的 parse_num 函数
        # 需要处理 @ 符号分隔的情况
        parts = name_without_ext.split('@')

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # 使用 num_parser.parse_num 提取番号
            num = num_parser.parse_num(part)
            if num:
                logger.debug(f"从 '{filename}' 提取到番号: {num}")
                return num

        logger.debug(f"无法从 '{filename}' 提取番号")
        return None

    def _num_exists_in_database(self, num: str) -> bool:
        """
        检查番号是否已存在于数据库中

        检查以下表：
        - history
        - torrent
        - subscribe
        - actor_subscribe_download

        Args:
            num: 番号

        Returns:
            如果番号已存在则返回 True，否则返回 False
        """
        try:
            # 检查 history 表
            history_exists = self.db.query(History).filter(
                History.num == num
            ).first() is not None

            if history_exists:
                logger.debug(f"番号 {num} 已存在于 history 表")
                return True

            # 检查 torrent 表
            torrent_exists = self.db.query(Torrent).filter(
                Torrent.num == num
            ).first() is not None

            if torrent_exists:
                logger.debug(f"番号 {num} 已存在于 torrent 表")
                return True

            # 检查 subscribe 表
            subscribe_exists = self.db.query(Subscribe).filter(
                Subscribe.num == num
            ).first() is not None

            if subscribe_exists:
                logger.debug(f"番号 {num} 已存在于 subscribe 表")
                return True

            # 检查 actor_subscribe_download 表
            actor_download_exists = self.db.query(ActorSubscribeDownload).filter(
                ActorSubscribeDownload.num == num
            ).first() is not None

            if actor_download_exists:
                logger.debug(f"番号 {num} 已存在于 actor_subscribe_download 表")
                return True

            return False

        except Exception as e:
            logger.error(f"检查番号 {num} 是否存在时出错: {str(e)}")
            return False

    def scan_local_videos(self, batch_size: int = 100) -> Dict[str, int]:
        """
        扫描本地视频文件夹

        功能：
        1. 递归扫描 video_path 目录
        2. 识别视频文件（mp4, mkv, avi, wmv, mov, flv）
        3. 从文件名提取番号
        4. 检查番号是否已存在于数据库
        5. 为新发现的视频创建 history 记录（批量提交）

        Args:
            batch_size: 批量提交的大小，默认100条

        Returns:
            扫描结果统计：
            {
                'total_files': 扫描到的文件总数,
                'new_videos': 新发现的视频数,
                'existing_videos': 已存在的视频数,
                'failed_to_parse': 无法解析番号的视频数
            }
        """
        logger.info("=" * 80)
        logger.info("开始扫描本地视频文件夹")
        logger.info("=" * 80)

        video_path = self.setting.app.video_path

        if not video_path or not os.path.exists(video_path):
            logger.error(f"视频路径不存在: {video_path}")
            return {
                'total_files': 0,
                'new_videos': 0,
                'existing_videos': 0,
                'failed_to_parse': 0
            }

        logger.info(f"扫描路径: {video_path}")
        logger.info(f"支持的视频格式: {', '.join(self.SUPPORTED_VIDEO_FORMATS)}")

        # 统计信息
        total_files = 0
        new_videos = 0
        existing_videos = 0
        failed_to_parse = 0

        # 收集需要创建的历史记录
        new_history_records = []

        try:
            # 使用 os.walk() 递归扫描目录
            for root, dirs, files in os.walk(video_path):
                for filename in files:
                    # 获取完整路径
                    file_path = os.path.join(root, filename)

                    # 检查文件扩展名
                    _, ext = os.path.splitext(filename)
                    if ext.lower() not in self.SUPPORTED_VIDEO_FORMATS:
                        continue

                    total_files += 1

                    # 检查文件大小（避免处理过小的文件）
                    try:
                        file_size = os.path.getsize(file_path)
                        min_size = self.setting.app.video_size_minimum * 1024 * 1024  # MB to bytes

                        if file_size < min_size:
                            logger.debug(f"跳过过小的文件: {filename} ({file_size / (1024 * 1024):.2f} MB)")
                            continue
                    except OSError as e:
                        logger.warning(f"无法获取文件大小: {filename}, 错误: {str(e)}")
                        continue

                    # 从文件名提取番号
                    num = self.extract_num_from_filename(filename)

                    if not num:
                        logger.warning(f"无法从文件名提取番号: {filename}")
                        failed_to_parse += 1
                        continue

                    # 检查番号是否已存在
                    if self._num_exists_in_database(num):
                        logger.info(f"番号已存在，跳过: {num} ({filename})")
                        existing_videos += 1
                        continue

                    # 创建新的历史记录
                    logger.info(f"发现新视频: {num} ({filename})")
                    new_history_records.append({
                        'num': num,
                        'source_path': file_path,
                        'dest_path': file_path,
                        'filename': filename
                    })
                    new_videos += 1

            # 批量创建历史记录（分批提交以优化性能）
            if new_history_records:
                logger.info(f"开始创建 {len(new_history_records)} 条历史记录（分批大小：{batch_size}）...")

                total_created = 0
                failed_count = 0

                try:
                    # 分批处理
                    for i in range(0, len(new_history_records), batch_size):
                        batch = new_history_records[i:i + batch_size]
                        batch_num = i // batch_size + 1
                        total_batches = (len(new_history_records) + batch_size - 1) // batch_size

                        logger.info(f"处理批次 {batch_num}/{total_batches}，共 {len(batch)} 条记录")

                        try:
                            # 使用 bulk_insert_mappings 提高性能
                            history_mappings = [
                                {
                                    'status': 1,  # 状态：1 表示成功
                                    'num': record['num'],
                                    'is_zh': False,  # 默认值，后续可以通过刮削更新
                                    'is_uncensored': False,  # 默认值，后续可以通过刮削更新
                                    'source_path': record['source_path'],
                                    'dest_path': record['dest_path'],
                                    'trans_method': 'local_scan',  # 标记来源为本地扫描
                                    'created_at': datetime.now(),
                                    'updated_at': datetime.now()
                                }
                                for record in batch
                            ]

                            self.db.bulk_insert_mappings(History, history_mappings)
                            self.db.commit()

                            total_created += len(batch)
                            logger.info(f"批次 {batch_num} 成功创建 {len(batch)} 条记录，累计 {total_created}/{len(new_history_records)}")

                        except Exception as batch_error:
                            self.db.rollback()
                            failed_count += len(batch)
                            logger.error(f"批次 {batch_num} 创建失败: {str(batch_error)}")
                            logger.error(f"失败的记录数: {len(batch)}")

                    if total_created > 0:
                        logger.info(f"成功创建 {total_created} 条历史记录")
                    if failed_count > 0:
                        logger.warning(f"失败的记录数: {failed_count}")
                        # 调整统计数据
                        new_videos = total_created
                        existing_videos += failed_count

                except Exception as e:
                    self.db.rollback()
                    logger.error(f"批量创建历史记录失败: {str(e)}")
                    # 重置新视频计数
                    new_videos = 0
                    existing_videos += len(new_history_records)

        except Exception as e:
            logger.error(f"扫描过程中出错: {str(e)}")
            import traceback
            logger.error(f"详细错误信息:\n{traceback.format_exc()}")

        # 输出统计信息
        logger.info("=" * 80)
        logger.info("扫描完成！统计信息：")
        logger.info(f"  扫描文件总数: {total_files}")
        logger.info(f"  新发现视频数: {new_videos}")
        logger.info(f"  已存在视频数: {existing_videos}")
        logger.info(f"  无法解析番号: {failed_to_parse}")
        logger.info("=" * 80)

        return {
            'total_files': total_files,
            'new_videos': new_videos,
            'existing_videos': existing_videos,
            'failed_to_parse': failed_to_parse
        }

    def scan_and_report(self) -> str:
        """
        扫描并生成报告

        Returns:
            格式化的扫描报告字符串
        """
        result = self.scan_local_videos()

        report = f"""
本地视频扫描报告
{'=' * 50}
扫描路径: {self.setting.app.video_path}
扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

扫描结果:
  - 扫描文件总数: {result['total_files']}
  - 新发现视频数: {result['new_videos']}
  - 已存在视频数: {result['existing_videos']}
  - 无法解析番号: {result['failed_to_parse']}

{'=' * 50}
"""
        return report


# 便捷函数：用于定时任务或命令行调用
def run_scan_task():
    """
    运行扫描任务（用于定时任务）
    """
    from app.db import SessionFactory

    try:
        with SessionFactory() as db:
            service = FileScanService(db=db)
            result = service.scan_local_videos()
            logger.info(f"定时扫描任务完成: {result}")
            return result
    except Exception as e:
        logger.error(f"定时扫描任务失败: {str(e)}")
        import traceback
        logger.error(f"详细错误信息:\n{traceback.format_exc()}")
        return None
