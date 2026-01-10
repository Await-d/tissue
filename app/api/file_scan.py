"""
Author: Await
Date: 2026-01-11
Description: 文件扫描管理 API 路由

提供以下功能：
1. 手动触发文件扫描任务
2. 查询扫描历史记录（分页）
3. 获取最近一次扫描结果
4. 获取当前扫描任务状态
"""
import asyncio
import time
import traceback
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app import schema
from app.db import get_db
from app.db.models import ScanRecord
from app.db.models.user import User
from app.dependencies.security import get_current_user
from app.schema.r import R
from app.service.file_scan import get_file_scan_service, FileScanService
from app.utils.logger import logger

router = APIRouter()

# 全局扫描锁 - 防止并发扫描
_scan_lock = asyncio.Lock()
_is_scanning = False
_current_scan_id: Optional[int] = None


@router.post("/trigger", response_model=R[schema.ScanResultResponse])
async def trigger_scan(
    request: schema.ScanTriggerRequest,
    service: FileScanService = Depends(get_file_scan_service),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    手动触发文件扫描任务

    功能说明：
    - 扫描本地视频文件夹，识别番号并创建历史记录
    - 使用锁机制防止并发扫描
    - 扫描结果会保存到 scan_record 表
    - 同步等待扫描完成后返回结果

    Args:
        request: 扫描触发请求参数
            - force_rescan: 是否强制重新扫描（当前未使用，保留用于未来扩展）
        service: 文件扫描服务实例
        db: 数据库会话

    Returns:
        R[ScanResultResponse]: 扫描结果响应
            - scan_id: 扫描记录ID
            - scan_time: 扫描时间
            - total_files: 扫描文件总数
            - new_found: 新发现视频数
            - already_exists: 已存在视频数
            - scan_duration: 扫描耗时（秒）
            - status: 扫描状态（success/failed）
            - error_message: 错误信息（如果失败）

    Raises:
        HTTPException 409: 正在进行扫描，请稍后再试
        HTTPException 500: 扫描过程中发生错误
    """
    global _is_scanning, _current_scan_id

    try:
        # 使用数据库状态检查是否有正在进行的扫描（分布式锁）
        active_scan = db.query(ScanRecord).filter(
            ScanRecord.status == 'running'
        ).first()

        if active_scan:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"正在进行扫描（任务ID: {active_scan.id}），请稍后再试"
            )

        # 获取内存锁（用于单进程内防护）
        if _scan_lock.locked():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="正在进行扫描，请稍后再试"
            )

        async with _scan_lock:
            _is_scanning = True
            _current_scan_id = None

            logger.info(f"收到扫描触发请求，force_rescan={request.force_rescan}")

            # 记录开始时间
            start_time = time.time()
            scan_time = datetime.now()

            # 创建运行中的扫描记录（数据库锁）
            scan_record = ScanRecord(
                scan_time=scan_time,
                total_files=0,
                new_found=0,
                already_exists=0,
                scan_duration=0.0,
                status='running',  # 标记为运行中
                error_message=None
            )
            db.add(scan_record)
            db.commit()
            db.refresh(scan_record)

            _current_scan_id = scan_record.id
            logger.info(f"创建扫描任务，ID={scan_record.id}")

            try:
                # 执行扫描（在线程池中运行，避免阻塞事件循环）
                loop = asyncio.get_event_loop()
                scan_result = await loop.run_in_executor(
                    None,
                    service.scan_local_videos
                )

                # 计算耗时
                scan_duration = time.time() - start_time

                # 更新扫描记录为成功
                scan_record.total_files = scan_result['total_files']
                scan_record.new_found = scan_result['new_videos']
                scan_record.already_exists = scan_result['existing_videos']
                scan_record.scan_duration = scan_duration
                scan_record.status = 'success'
                db.commit()

                logger.info(
                    f"扫描完成！ID={scan_record.id}, "
                    f"总数={scan_result['total_files']}, "
                    f"新增={scan_result['new_videos']}, "
                    f"已存在={scan_result['existing_videos']}, "
                    f"耗时={scan_duration:.2f}秒"
                )

                # 构造响应
                response = schema.ScanResultResponse(
                    scan_id=scan_record.id,
                    scan_time=scan_record.scan_time,
                    total_files=scan_record.total_files,
                    new_found=scan_record.new_found,
                    already_exists=scan_record.already_exists,
                    scan_duration=scan_record.scan_duration,
                    status=scan_record.status,
                    error_message=scan_record.error_message
                )

                return R.ok(data=response)

            except Exception as scan_error:
                # 扫描失败，更新记录
                scan_duration = time.time() - start_time
                scan_record.scan_duration = scan_duration
                scan_record.status = 'failed'
                scan_record.error_message = str(scan_error)
                db.commit()

                error_msg = f"扫描过程中发生错误: {str(scan_error)}"
                logger.error(error_msg)
                logger.error(traceback.format_exc())

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_msg
                )
            finally:
                _is_scanning = False

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"扫描触发失败: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )


@router.get("/records", response_model=R[schema.ScanRecordListResponse])
def get_scan_records(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    status: Optional[str] = Query(None, description="过滤状态: success/failed"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    查询扫描历史记录

    功能说明：
    - 支持分页查询
    - 支持按状态过滤
    - 按扫描时间倒序排列（最新的在前面）

    Args:
        page: 页码，从1开始
        page_size: 每页数量，最大100
        status: 可选的状态过滤（success/failed）
        db: 数据库会话

    Returns:
        R[ScanRecordListResponse]: 扫描记录列表响应
            - records: 扫描记录列表
            - total: 总记录数

    Raises:
        HTTPException 500: 查询过程中发生错误
    """
    try:
        # 构建查询
        query = db.query(ScanRecord)

        # 状态过滤
        if status:
            query = query.filter(ScanRecord.status == status)

        # 获取总数
        total = query.count()

        # 分页查询，按时间倒序
        offset = (page - 1) * page_size
        records = query.order_by(desc(ScanRecord.scan_time)).offset(offset).limit(page_size).all()

        # 转换为响应格式
        record_list = [
            schema.ScanResultResponse(
                scan_id=record.id,
                scan_time=record.scan_time,
                total_files=record.total_files,
                new_found=record.new_found,
                already_exists=record.already_exists,
                scan_duration=record.scan_duration,
                status=record.status,
                error_message=record.error_message
            )
            for record in records
        ]

        response = schema.ScanRecordListResponse(
            records=record_list,
            total=total
        )

        logger.debug(
            f"查询扫描记录: page={page}, page_size={page_size}, "
            f"status={status}, total={total}, returned={len(record_list)}"
        )

        return R.ok(data=response)

    except Exception as e:
        error_msg = f"查询扫描记录失败: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )


@router.get("/latest", response_model=R[schema.ScanResultResponse])
def get_latest_scan(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取最近一次扫描结果

    功能说明：
    - 返回最新的一条扫描记录
    - 如果没有扫描记录则返回404

    Args:
        db: 数据库会话

    Returns:
        R[ScanResultResponse]: 最新的扫描结果

    Raises:
        HTTPException 404: 没有找到扫描记录
        HTTPException 500: 查询过程中发生错误
    """
    try:
        # 查询最新的扫描记录
        latest_record = db.query(ScanRecord).order_by(desc(ScanRecord.scan_time)).first()

        if not latest_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="没有找到扫描记录"
            )

        response = schema.ScanResultResponse(
            scan_id=latest_record.id,
            scan_time=latest_record.scan_time,
            total_files=latest_record.total_files,
            new_found=latest_record.new_found,
            already_exists=latest_record.already_exists,
            scan_duration=latest_record.scan_duration,
            status=latest_record.status,
            error_message=latest_record.error_message
        )

        logger.debug(f"获取最新扫描记录: ID={latest_record.id}, status={latest_record.status}")

        return R.ok(data=response)

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"获取最新扫描记录失败: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )


@router.get("/status", response_model=R[dict])
def get_scan_status(current_user: User = Depends(get_current_user)):
    """
    获取当前扫描任务状态

    功能说明：
    - 返回当前是否正在执行扫描任务
    - 返回当前扫描任务的ID（如果存在）

    Returns:
        R[dict]: 扫描状态响应
            - is_scanning: 是否正在扫描
            - current_scan_id: 当前扫描任务ID（如果正在扫描）

    Example:
        {
            "success": true,
            "data": {
                "is_scanning": true,
                "current_scan_id": 123
            }
        }
    """
    global _is_scanning, _current_scan_id

    response_data = {
        "is_scanning": _is_scanning,
        "current_scan_id": _current_scan_id
    }

    logger.debug(f"获取扫描状态: is_scanning={_is_scanning}, current_scan_id={_current_scan_id}")

    return R.ok(data=response_data)
