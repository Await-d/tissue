"""
站点管理API接口
提供站点配置、监控、故障转移等功能的REST API
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.models.site_management import (
    Site, SiteStatistics, SiteHealthCheck, SiteErrorLog,
    SiteFailoverRule, SiteLoadBalancer, SiteStatus, SiteType
)
from app.schema.site_management import (
    SiteCreate, SiteUpdate, SiteResponse, SiteListResponse,
    SiteStatisticsResponse, SiteHealthResponse, SiteErrorLogResponse,
    FailoverRuleCreate, FailoverRuleUpdate, FailoverRuleResponse,
    LoadBalancerCreate, LoadBalancerUpdate, LoadBalancerResponse
)
from app.db import get_db
from app.utils.logger import logger

router = APIRouter(tags=["站点管理"])


# ========== 站点基础管理 ==========

@router.get("/sites", response_model=SiteListResponse)
async def list_sites(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[SiteStatus] = None,
    site_type: Optional[SiteType] = None,
    enabled_only: bool = False,
    db: Session = Depends(get_db)
):
    """获取站点列表"""
    query = db.query(Site)

    if status:
        query = query.filter(Site.status == status)
    if site_type:
        query = query.filter(Site.site_type == site_type)
    if enabled_only:
        query = query.filter(Site.is_enabled == True)

    total = query.count()
    sites = query.offset(skip).limit(limit).all()

    return SiteListResponse(
        sites=[SiteResponse.from_orm(site) for site in sites],
        total=total,
        skip=skip,
        limit=limit
    )


@router.post("/sites", response_model=SiteResponse, status_code=status.HTTP_201_CREATED)
async def create_site(
    site_data: SiteCreate,
    db: Session = Depends(get_db)
):
    """创建新站点"""
    # 检查站点名称是否已存在
    existing = db.query(Site).filter(Site.name == site_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"站点名称 '{site_data.name}' 已存在"
        )

    # 创建站点
    site = Site(**site_data.dict())
    db.add(site)
    db.commit()
    db.refresh(site)

    # 创建初始统计记录
    stats = SiteStatistics(site_id=site.id)
    db.add(stats)
    db.commit()

    logger.info(f"创建站点: {site.name} (ID: {site.id})")
    return SiteResponse.from_orm(site)


@router.get("/sites/{site_id}", response_model=SiteResponse)
async def get_site(
    site_id: int,
    db: Session = Depends(get_db)
):
    """获取站点详情"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"站点 {site_id} 不存在"
        )
    return SiteResponse.from_orm(site)


@router.put("/sites/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: int,
    site_data: SiteUpdate,
    db: Session = Depends(get_db)
):
    """更新站点配置"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"站点 {site_id} 不存在"
        )

    # 更新站点数据
    update_data = site_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(site, field, value)

    db.commit()
    db.refresh(site)

    logger.info(f"更新站点: {site.name} (ID: {site.id})")
    return SiteResponse.from_orm(site)


@router.delete("/sites/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site(
    site_id: int,
    db: Session = Depends(get_db)
):
    """删除站点"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"站点 {site_id} 不存在"
        )

    db.delete(site)
    db.commit()

    logger.info(f"删除站点: {site.name} (ID: {site.id})")


# ========== 站点状态管理 ==========

@router.post("/sites/{site_id}/enable")
async def enable_site(
    site_id: int,
    db: Session = Depends(get_db)
):
    """启用站点"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"站点 {site_id} 不存在"
        )

    site.is_enabled = True
    site.status = SiteStatus.ACTIVE
    db.commit()

    logger.info(f"启用站点: {site.name} (ID: {site.id})")
    return {"message": f"站点 '{site.name}' 已启用"}


@router.post("/sites/{site_id}/disable")
async def disable_site(
    site_id: int,
    reason: str = None,
    db: Session = Depends(get_db)
):
    """禁用站点"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"站点 {site_id} 不存在"
        )

    site.is_enabled = False
    site.status = SiteStatus.DISABLED
    db.commit()

    # 记录禁用原因
    if reason:
        error_log = SiteErrorLog(
            site_id=site_id,
            error_type="manual_disable",
            error_message=reason,
            operation="disable_site"
        )
        db.add(error_log)
        db.commit()

    logger.info(f"禁用站点: {site.name} (ID: {site.id}), 原因: {reason or '无'}")
    return {"message": f"站点 '{site.name}' 已禁用"}


@router.post("/sites/{site_id}/health-check")
async def perform_health_check(
    site_id: int,
    db: Session = Depends(get_db)
):
    """执行站点健康检查"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"站点 {site_id} 不存在"
        )

    # 这里应该调用实际的健康检查逻辑
    # 为了示例，我们创建一个基本的检查记录
    from app.services.site_health_checker import SiteHealthChecker

    checker = SiteHealthChecker()
    check_result = await checker.check_site_health(site)

    health_check = SiteHealthCheck(
        site_id=site_id,
        is_healthy=check_result.is_healthy,
        response_time=check_result.response_time,
        status_code=check_result.status_code,
        error_message=check_result.error_message,
        check_url=site.current_url
    )
    db.add(health_check)
    db.commit()

    return {
        "message": f"站点 '{site.name}' 健康检查完成",
        "is_healthy": check_result.is_healthy,
        "response_time": check_result.response_time
    }


# ========== 站点统计信息 ==========

@router.get("/sites/{site_id}/statistics", response_model=SiteStatisticsResponse)
async def get_site_statistics(
    site_id: int,
    db: Session = Depends(get_db)
):
    """获取站点统计信息"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"站点 {site_id} 不存在"
        )

    stats = db.query(SiteStatistics).filter(SiteStatistics.site_id == site_id).first()
    if not stats:
        # 创建初始统计记录
        stats = SiteStatistics(site_id=site_id)
        db.add(stats)
        db.commit()
        db.refresh(stats)

    return SiteStatisticsResponse.from_orm(stats)


@router.post("/sites/{site_id}/statistics/reset")
async def reset_site_statistics(
    site_id: int,
    db: Session = Depends(get_db)
):
    """重置站点统计信息"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"站点 {site_id} 不存在"
        )

    stats = db.query(SiteStatistics).filter(SiteStatistics.site_id == site_id).first()
    if stats:
        # 重置所有计数器
        stats.total_requests = 0
        stats.successful_requests = 0
        stats.failed_requests = 0
        stats.avg_response_time = 0.0
        stats.max_response_time = 0.0
        stats.min_response_time = 0.0
        stats.videos_scraped = 0
        stats.actors_scraped = 0
        stats.downloads_provided = 0
        stats.timeout_errors = 0
        stats.connection_errors = 0
        stats.parse_errors = 0
        stats.rate_limit_errors = 0
        stats.last_reset = datetime.utcnow()

        db.commit()

    logger.info(f"重置站点统计: {site.name} (ID: {site.id})")
    return {"message": f"站点 '{site.name}' 统计信息已重置"}


# ========== 错误日志管理 ==========

@router.get("/sites/{site_id}/errors", response_model=List[SiteErrorLogResponse])
async def get_site_errors(
    site_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    error_type: Optional[str] = None,
    unresolved_only: bool = False,
    db: Session = Depends(get_db)
):
    """获取站点错误日志"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"站点 {site_id} 不存在"
        )

    query = db.query(SiteErrorLog).filter(SiteErrorLog.site_id == site_id)

    if error_type:
        query = query.filter(SiteErrorLog.error_type == error_type)
    if unresolved_only:
        query = query.filter(SiteErrorLog.is_resolved == False)

    errors = query.order_by(SiteErrorLog.occurred_at.desc()).offset(skip).limit(limit).all()

    return [SiteErrorLogResponse.from_orm(error) for error in errors]


@router.post("/sites/{site_id}/errors/{error_id}/resolve")
async def resolve_error(
    site_id: int,
    error_id: int,
    resolution_note: str,
    db: Session = Depends(get_db)
):
    """标记错误为已解决"""
    error_log = db.query(SiteErrorLog).filter(
        SiteErrorLog.id == error_id,
        SiteErrorLog.site_id == site_id
    ).first()

    if not error_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"错误记录 {error_id} 不存在"
        )

    error_log.is_resolved = True
    error_log.resolution_note = resolution_note
    error_log.resolved_at = datetime.utcnow()

    db.commit()

    return {"message": "错误已标记为已解决"}


# ========== 故障转移规则管理 ==========

@router.get("/failover-rules", response_model=List[FailoverRuleResponse])
async def list_failover_rules(
    db: Session = Depends(get_db)
):
    """获取所有故障转移规则"""
    rules = db.query(SiteFailoverRule).all()
    return [FailoverRuleResponse.from_orm(rule) for rule in rules]


@router.post("/failover-rules", response_model=FailoverRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_failover_rule(
    rule_data: FailoverRuleCreate,
    db: Session = Depends(get_db)
):
    """创建故障转移规则"""
    rule = SiteFailoverRule(**rule_data.dict())
    db.add(rule)
    db.commit()
    db.refresh(rule)

    logger.info(f"创建故障转移规则: {rule.name} (ID: {rule.id})")
    return FailoverRuleResponse.from_orm(rule)


# ========== 负载均衡管理 ==========

@router.get("/load-balancers", response_model=List[LoadBalancerResponse])
async def list_load_balancers(
    db: Session = Depends(get_db)
):
    """获取所有负载均衡器"""
    balancers = db.query(SiteLoadBalancer).all()
    return [LoadBalancerResponse.from_orm(balancer) for balancer in balancers]


@router.post("/load-balancers", response_model=LoadBalancerResponse, status_code=status.HTTP_201_CREATED)
async def create_load_balancer(
    balancer_data: LoadBalancerCreate,
    db: Session = Depends(get_db)
):
    """创建负载均衡器"""
    balancer = SiteLoadBalancer(**balancer_data.dict())
    db.add(balancer)
    db.commit()
    db.refresh(balancer)

    logger.info(f"创建负载均衡器: {balancer.name} (ID: {balancer.id})")
    return LoadBalancerResponse.from_orm(balancer)


# ========== 站点测试接口 ==========

@router.post("/sites/{site_id}/test")
async def test_site(
    site_id: int,
    test_number: str = "SSNI-001",
    db: Session = Depends(get_db)
):
    """测试站点功能"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"站点 {site_id} 不存在"
        )

    from app.services.site_tester import SiteTester

    tester = SiteTester()
    test_result = await tester.test_site_functionality(site, test_number)

    return {
        "site_name": site.name,
        "test_number": test_number,
        "test_results": test_result
    }


# ========== 批量操作接口 ==========

@router.post("/sites/batch/health-check")
async def batch_health_check(
    site_ids: Optional[List[int]] = None,
    db: Session = Depends(get_db)
):
    """批量健康检查"""
    if site_ids:
        sites = db.query(Site).filter(Site.id.in_(site_ids)).all()
    else:
        sites = db.query(Site).filter(Site.is_enabled == True).all()

    from app.services.site_health_checker import SiteHealthChecker

    checker = SiteHealthChecker()
    results = []

    for site in sites:
        check_result = await checker.check_site_health(site)
        results.append({
            "site_id": site.id,
            "site_name": site.name,
            "is_healthy": check_result.is_healthy,
            "response_time": check_result.response_time,
            "error_message": check_result.error_message
        })

        # 保存检查结果
        health_check = SiteHealthCheck(
            site_id=site.id,
            is_healthy=check_result.is_healthy,
            response_time=check_result.response_time,
            status_code=check_result.status_code,
            error_message=check_result.error_message,
            check_url=site.current_url
        )
        db.add(health_check)

    db.commit()

    return {
        "message": f"完成 {len(sites)} 个站点的健康检查",
        "results": results
    }


@router.get("/dashboard/overview")
async def get_dashboard_overview(
    db: Session = Depends(get_db)
):
    """获取站点管理仪表板概览"""
    # 站点总数和状态分布
    total_sites = db.query(Site).count()
    active_sites = db.query(Site).filter(Site.status == SiteStatus.ACTIVE).count()
    disabled_sites = db.query(Site).filter(Site.status == SiteStatus.DISABLED).count()
    degraded_sites = db.query(Site).filter(Site.status == SiteStatus.DEGRADED).count()

    # 错误统计
    total_errors = db.query(SiteErrorLog).count()
    unresolved_errors = db.query(SiteErrorLog).filter(SiteErrorLog.is_resolved == False).count()

    # 最近24小时的错误数
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_errors = db.query(SiteErrorLog).filter(SiteErrorLog.occurred_at >= yesterday).count()

    return {
        "sites": {
            "total": total_sites,
            "active": active_sites,
            "disabled": disabled_sites,
            "degraded": degraded_sites
        },
        "errors": {
            "total": total_errors,
            "unresolved": unresolved_errors,
            "recent_24h": recent_errors
        },
        "timestamp": datetime.utcnow()
    }