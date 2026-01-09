from fastapi import APIRouter

from app import schema
from app.scheduler import scheduler
from app.schema.r import R
from app.service.actor_subscribe import ActorSubscribeService
from app.utils.logger import logger

router = APIRouter()


@router.get("/")
def get_schedules():
    schedules = sorted(scheduler.list(), key=lambda i: i.id)

    result = []
    for schedule in schedules:
        try:
            # 特殊处理actor_subscribe任务，因为它不在scheduler.jobs字典中
            # 处理特殊的cron任务（不在scheduler.jobs字典中）
            if schedule.id == 'actor_subscribe':
                result.append(schema.Schedule(
                    key=schedule.id,
                    name='演员订阅',
                    next_run_time=schedule.next_run_time,
                    status=False  # 无法获取实时运行状态，默认为未运行
                ))
                continue

            if schedule.id == 'actor_works_count_update':
                result.append(schema.Schedule(
                    key=schedule.id,
                    name='更新演员作品数量',
                    next_run_time=schedule.next_run_time,
                    status=False
                ))
                continue

            # 处理普通任务
            job = scheduler.jobs[schedule.id]
            key = schedule.id
            name = schedule.name
            next_run_time = schedule.next_run_time
            status = job.running > 0
            result.append(schema.Schedule(key=key, name=name, next_run_time=next_run_time, status=status))
        except KeyError as e:
            # 记录错误但不中断处理
            logger.error(f"获取任务信息失败: {e}")
            continue

    return R.list(result)


@router.get('/fire')
def fire_schedule(key: str):
    # 特殊处理actor_subscribe任务
    if key == 'actor_subscribe':
        try:
            # 直接调用actor_subscribe任务
            ActorSubscribeService.job_actor_subscribe()
            return R.ok()
        except Exception as e:
            logger.error(f"手动执行演员订阅任务失败: {e}")
            return R.fail(f"手动执行演员订阅任务失败: {str(e)}")

    # 处理普通任务
    scheduler.manually(key)
    return R.ok()
