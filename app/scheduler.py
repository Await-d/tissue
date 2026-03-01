from datetime import datetime
from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from pydantic import BaseModel

from app.schema import Setting
from app.service.download import DownloadService
from app.service.job import clean_cache
from app.service.subscribe import SubscribeService
from app.utils.logger import logger
from app.service.actor_subscribe import ActorSubscribeService
from app.service.auto_download import AutoDownloadService
from app.service.video_cache import VideoCacheService
from app.service.pending_torrent import PendingTorrentService
from app.service.file_scan import run_scan_task


class Job(BaseModel):
    key: str
    name: str
    job: Callable
    interval: int
    running: int = 0
    jitter: int = 0


class Scheduler:
    jobs = {
        "subscribe": Job(
            key="subscribe",
            name="订阅下载",
            job=SubscribeService.job_subscribe,
            interval=400,
            jitter=30 * 60,
        ),
        "subscribe_meta_update": Job(
            key="subscribe_meta_update",
            name="订阅元数据更新",
            job=SubscribeService.job_subscribe_meta_update,
            interval=100 * 60,
            jitter=6 * 60 * 60,
        ),
        "scrape_download": Job(
            key="scrape_download",
            name="整理已完成下载",
            job=DownloadService.job_scrape_download,
            interval=5,
        ),
        "delete_complete_download": Job(
            key="delete_complete_download",
            name="删除已整理下载",
            job=DownloadService.job_delete_complete_download,
            interval=5,
        ),
        "clean_cache": Job(
            key="clean_cache", name="清理缓存", job=clean_cache, interval=7 * 24 * 60
        ),
        "auto_download": Job(
            key="auto_download",
            name="智能自动下载",
            job=AutoDownloadService.job_auto_download,
            interval=60,
            jitter=10 * 60,
        ),
        "stop_seeding_completed": Job(
            key="stop_seeding_completed",
            name="停止已完成种子做种",
            job=DownloadService.job_stop_seeding_completed,
            interval=10,
            jitter=2 * 60,
        ),
        "refresh_video_cache": Job(
            key="refresh_video_cache",
            name="刷新视频数据缓存",
            job=VideoCacheService.job_refresh_video_cache,
            interval=120,
            jitter=30 * 60,
        ),  # 每2小时执行，抖动30分钟
        "process_pending_torrents": Job(
            key="process_pending_torrents",
            name="处理待处理种子",
            job=PendingTorrentService.job_process_pending_torrents,
            interval=1,  # 每分钟检查一次
            jitter=0,
        ),
    }

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self._initialized = False

    def init(self):
        if self._initialized:
            logger.warning("调度器已初始化，跳过重复初始化")
            return

        self.scheduler.start()

        setting = Setting()
        self.jobs["auto_download"].interval = max(
            1, int(getattr(setting.auto_download, "check_interval", 60) or 60)
        )

        self.add("subscribe")
        self.add("subscribe_meta_update")
        self.add("clean_cache")
        if getattr(setting.auto_download, "enabled", True):
            self.add("auto_download")
        self.add("refresh_video_cache")  # 启动视频缓存刷新任务
        self.add("process_pending_torrents")

        if setting.download.trans_auto:
            self.add("scrape_download")
        if setting.download.delete_auto:
            self.add("delete_complete_download")
        if setting.download.stop_seeding:
            self.add("stop_seeding_completed")

        self.scheduler.add_job(
            ActorSubscribeService.job_actor_subscribe,
            "cron",
            hour="2",
            minute="30",
            id="actor_subscribe",
            replace_existing=True,
        )

        # 添加演员作品数量更新任务（每天早上6点执行）
        self.scheduler.add_job(
            ActorSubscribeService.job_update_works_counts,
            "cron",
            hour="6",
            minute="0",
            id="actor_works_count_update",
            replace_existing=True,
        )

        # 添加待处理种子每日清理任务（每天凌晨3点执行）
        self.scheduler.add_job(
            PendingTorrentService.job_cleanup_pending_torrents,
            "cron",
            hour="3",
            minute="0",
            id="cleanup_pending_torrents",
            replace_existing=True,
        )

        # 添加本地视频扫描任务（每天凌晨2点执行）
        # 根据配置决定是否启用
        if setting.app.enable_scheduled_scan:
            logger.info("启用定时本地视频扫描任务（每天凌晨2点执行）")
            self.scheduler.add_job(
                run_scan_task,
                trigger=CronTrigger(hour=2, minute=0),
                id="file_scan_job",
                name="定期扫描本地视频文件",
                replace_existing=True,
            )
        else:
            logger.info("定时本地视频扫描任务已禁用（可在配置中启用）")

        self._initialized = True

    def list(self):
        return self.scheduler.get_jobs()

    def add(self, key: str):
        job = self.jobs.get(key)
        if job is None:
            logger.warning(f"任务不存在，无法启动: {key}")
            return
        logger.info(f"启动任务，{job.name}")
        self.scheduler.add_job(
            self.do_job,
            trigger=IntervalTrigger(minutes=job.interval, jitter=job.jitter),
            id=job.key,
            name=job.name,
            args=[job.key],
            replace_existing=True,
        )

    def remove(self, key: str):
        job = self.scheduler.get_job(key)
        if job:
            logger.info(f"停止任务，{job.name}")
            self.scheduler.remove_job(key)

    def manually(self, key: str):
        job = self.scheduler.get_job(key)
        if job is None:
            logger.warning(f"任务不存在，无法手动触发: {key}")
            return False
        job.modify(next_run_time=datetime.now())
        return True

    @classmethod
    def do_job(cls, key):
        job = cls.jobs[key]
        if job.running > 0:
            logger.warning(f"任务正在执行中，跳过重入: {job.name}")
            return
        try:
            logger.info(f"执行任务，{job.name}")
            job.running += 1
            job.job()
        finally:
            job.running -= 1


scheduler = Scheduler()
