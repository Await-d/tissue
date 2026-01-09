"""
站点管理服务
负责站点的选择、故障转移、负载均衡等核心逻辑
"""
import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.db.models.site_management import (
    Site, SiteStatistics, SiteHealthCheck, SiteErrorLog,
    SiteStatus, SiteType, SiteFailoverRule, SiteLoadBalancer
)
from app.utils.logger import logger


class SiteManager:
    """站点管理器"""

    def __init__(self, db: Session):
        self.db = db
        self._load_balancer_state = {}

    def get_available_sites(
        self,
        operation: str = "scraping",
        site_type: Optional[SiteType] = None,
        required_features: Optional[List[str]] = None
    ) -> List[Site]:
        """
        获取可用站点列表

        Args:
            operation: 操作类型 (scraping, download, search, etc.)
            site_type: 站点类型过滤
            required_features: 必需功能列表 (download, preview, search, actor_info, ranking)

        Returns:
            按优先级排序的可用站点列表
        """
        query = self.db.query(Site).filter(
            Site.is_enabled == True,
            Site.status.in_([SiteStatus.ACTIVE, SiteStatus.DEGRADED])
        )

        # 按站点类型过滤
        if site_type:
            query = query.filter(Site.site_type == site_type)

        # 按功能需求过滤
        if required_features:
            for feature in required_features:
                if feature == "download":
                    query = query.filter(Site.supports_download == True)
                elif feature == "preview":
                    query = query.filter(Site.supports_preview == True)
                elif feature == "search":
                    query = query.filter(Site.supports_search == True)
                elif feature == "actor_info":
                    query = query.filter(Site.supports_actor_info == True)
                elif feature == "ranking":
                    query = query.filter(Site.supports_ranking == True)

        # 按优先级排序
        sites = query.order_by(Site.priority.asc()).all()

        logger.info(f"找到 {len(sites)} 个可用站点用于操作: {operation}")
        return sites

    def select_best_site(
        self,
        operation: str = "scraping",
        required_features: Optional[List[str]] = None,
        exclude_sites: Optional[List[int]] = None
    ) -> Optional[Site]:
        """
        选择最佳站点

        Args:
            operation: 操作类型
            required_features: 必需功能列表
            exclude_sites: 要排除的站点ID列表

        Returns:
            最佳站点或None
        """
        sites = self.get_available_sites(operation, required_features=required_features)

        if exclude_sites:
            sites = [site for site in sites if site.id not in exclude_sites]

        if not sites:
            logger.warning(f"没有找到可用站点用于操作: {operation}")
            return None

        # 使用加权选择算法
        return self._weighted_selection(sites)

    def _weighted_selection(self, sites: List[Site]) -> Site:
        """
        基于权重和性能统计的站点选择

        Args:
            sites: 候选站点列表

        Returns:
            选中的站点
        """
        if len(sites) == 1:
            return sites[0]

        # 计算每个站点的综合权重
        weighted_sites = []
        for site in sites:
            stats = self.db.query(SiteStatistics).filter(SiteStatistics.site_id == site.id).first()

            # 基础权重
            weight = site.weight

            # 根据成功率调整权重
            if stats and stats.total_requests > 0:
                success_rate = stats.success_rate / 100.0
                weight *= success_rate

                # 根据响应时间调整权重 (响应时间越短权重越高)
                if stats.avg_response_time > 0:
                    # 归一化响应时间 (假设30秒是最大可接受时间)
                    normalized_time = min(stats.avg_response_time / 30.0, 1.0)
                    weight *= (1.0 - normalized_time * 0.5)  # 最多减少50%权重

            # 根据站点状态调整权重
            if site.status == SiteStatus.DEGRADED:
                weight *= 0.5  # 降级站点权重减半

            weighted_sites.append((site, max(weight, 0.01)))  # 确保最小权重

        # 加权随机选择
        total_weight = sum(weight for _, weight in weighted_sites)
        random_value = random.uniform(0, total_weight)

        current_weight = 0
        for site, weight in weighted_sites:
            current_weight += weight
            if random_value <= current_weight:
                logger.info(f"选择站点: {site.name} (权重: {weight:.2f})")
                return site

        # 备用方案：返回第一个站点
        return weighted_sites[0][0]

    def get_fallback_sites(self, failed_site_id: int, operation: str) -> List[Site]:
        """
        获取故障转移站点列表

        Args:
            failed_site_id: 失败的站点ID
            operation: 操作类型

        Returns:
            备用站点列表
        """
        # 检查是否有适用的故障转移规则
        rules = self.db.query(SiteFailoverRule).filter(
            SiteFailoverRule.is_active == True
        ).all()

        fallback_site_ids = []
        for rule in rules:
            if failed_site_id in rule.fallback_sites or not rule.fallback_sites:
                fallback_site_ids.extend(rule.fallback_sites)

        if fallback_site_ids:
            # 根据规则获取备用站点
            fallback_sites = self.db.query(Site).filter(
                Site.id.in_(fallback_site_ids),
                Site.id != failed_site_id,
                Site.is_enabled == True,
                Site.status.in_([SiteStatus.ACTIVE, SiteStatus.DEGRADED])
            ).order_by(Site.priority.asc()).all()
        else:
            # 默认故障转移：获取所有其他可用站点
            fallback_sites = self.db.query(Site).filter(
                Site.id != failed_site_id,
                Site.is_enabled == True,
                Site.status.in_([SiteStatus.ACTIVE, SiteStatus.DEGRADED])
            ).order_by(Site.priority.asc()).all()

        logger.info(f"为失败站点 {failed_site_id} 找到 {len(fallback_sites)} 个备用站点")
        return fallback_sites

    def record_site_performance(
        self,
        site_id: int,
        success: bool,
        response_time: float,
        operation: str = "scraping",
        error_details: Optional[Dict[str, Any]] = None
    ):
        """
        记录站点性能数据

        Args:
            site_id: 站点ID
            success: 是否成功
            response_time: 响应时间(秒)
            operation: 操作类型
            error_details: 错误详情
        """
        # 更新站点统计
        stats = self.db.query(SiteStatistics).filter(SiteStatistics.site_id == site_id).first()
        if not stats:
            stats = SiteStatistics(site_id=site_id)
            self.db.add(stats)

        stats.total_requests += 1
        if success:
            stats.successful_requests += 1
        else:
            stats.failed_requests += 1

        # 更新响应时间统计
        if stats.avg_response_time == 0:
            stats.avg_response_time = response_time
        else:
            # 指数移动平均
            stats.avg_response_time = 0.7 * stats.avg_response_time + 0.3 * response_time

        stats.max_response_time = max(stats.max_response_time, response_time)
        if stats.min_response_time == 0:
            stats.min_response_time = response_time
        else:
            stats.min_response_time = min(stats.min_response_time, response_time)

        # 如果失败，记录错误类型
        if not success and error_details:
            error_type = error_details.get('type', 'unknown')
            if 'timeout' in error_type.lower():
                stats.timeout_errors += 1
            elif 'connection' in error_type.lower():
                stats.connection_errors += 1
            elif 'parse' in error_type.lower():
                stats.parse_errors += 1
            elif 'rate' in error_type.lower():
                stats.rate_limit_errors += 1

            # 记录详细错误日志
            error_log = SiteErrorLog(
                site_id=site_id,
                error_type=error_type,
                error_message=error_details.get('message', ''),
                error_details=error_details,
                operation=operation,
                response_time=response_time
            )
            self.db.add(error_log)

        self.db.commit()

        # 检查是否需要触发故障转移
        self._check_failover_conditions(site_id)

    def _check_failover_conditions(self, site_id: int):
        """
        检查站点是否满足故障转移条件

        Args:
            site_id: 站点ID
        """
        site = self.db.query(Site).filter(Site.id == site_id).first()
        if not site:
            return

        stats = self.db.query(SiteStatistics).filter(SiteStatistics.site_id == site_id).first()
        if not stats or stats.total_requests < 10:  # 需要足够的样本数据
            return

        # 检查故障转移规则
        rules = self.db.query(SiteFailoverRule).filter(SiteFailoverRule.is_active == True).all()

        for rule in rules:
            should_trigger = False

            # 检查错误率
            if stats.error_rate >= rule.trigger_error_rate * 100:
                should_trigger = True
                logger.warning(f"站点 {site.name} 错误率过高: {stats.error_rate:.1f}%")

            # 检查响应时间
            if stats.avg_response_time >= rule.trigger_response_time:
                should_trigger = True
                logger.warning(f"站点 {site.name} 响应时间过长: {stats.avg_response_time:.1f}s")

            # 检查连续失败次数 (简化检查最近的错误记录)
            recent_errors = self.db.query(SiteErrorLog).filter(
                SiteErrorLog.site_id == site_id,
                SiteErrorLog.occurred_at >= datetime.utcnow() - timedelta(minutes=10)
            ).count()

            if recent_errors >= rule.trigger_consecutive_failures:
                should_trigger = True
                logger.warning(f"站点 {site.name} 连续失败次数过多: {recent_errors}")

            if should_trigger:
                self._trigger_failover(site, rule)

    def _trigger_failover(self, site: Site, rule: SiteFailoverRule):
        """
        触发站点故障转移

        Args:
            site: 故障站点
            rule: 故障转移规则
        """
        logger.error(f"触发站点故障转移: {site.name}")

        # 将站点标记为降级状态
        if site.status == SiteStatus.ACTIVE:
            site.status = SiteStatus.DEGRADED
            self.db.commit()

        # 更新规则触发时间
        rule.last_triggered = datetime.utcnow()
        self.db.commit()

        # 记录故障转移事件
        error_log = SiteErrorLog(
            site_id=site.id,
            error_type="failover_triggered",
            error_message=f"根据规则 '{rule.name}' 触发故障转移",
            operation="failover",
            error_details={
                "rule_id": rule.id,
                "rule_name": rule.name,
                "trigger_time": datetime.utcnow().isoformat()
            }
        )
        self.db.add(error_log)
        self.db.commit()

    def get_load_balanced_site(self, balancer_id: int) -> Optional[Site]:
        """
        从负载均衡器获取站点

        Args:
            balancer_id: 负载均衡器ID

        Returns:
            选中的站点或None
        """
        balancer = self.db.query(SiteLoadBalancer).filter(
            SiteLoadBalancer.id == balancer_id,
            SiteLoadBalancer.is_active == True
        ).first()

        if not balancer:
            return None

        # 获取活跃站点
        active_sites = self.db.query(Site).filter(
            Site.id.in_(balancer.site_ids),
            Site.is_enabled == True,
            Site.status.in_([SiteStatus.ACTIVE, SiteStatus.DEGRADED])
        ).all()

        if not active_sites:
            return None

        # 根据策略选择站点
        if balancer.strategy == "round_robin":
            return self._round_robin_selection(balancer, active_sites)
        elif balancer.strategy == "weighted":
            return self._weighted_load_balance(balancer, active_sites)
        elif balancer.strategy == "least_connections":
            return self._least_connections_selection(active_sites)
        else:
            # 默认使用轮询
            return self._round_robin_selection(balancer, active_sites)

    def _round_robin_selection(self, balancer: SiteLoadBalancer, sites: List[Site]) -> Site:
        """轮询选择算法"""
        if balancer.id not in self._load_balancer_state:
            self._load_balancer_state[balancer.id] = 0

        current_index = self._load_balancer_state[balancer.id]
        selected_site = sites[current_index % len(sites)]

        # 更新索引
        self._load_balancer_state[balancer.id] = (current_index + 1) % len(sites)

        # 更新负载均衡器状态
        balancer.total_requests += 1
        balancer.last_request_time = datetime.utcnow()
        self.db.commit()

        return selected_site

    def _weighted_load_balance(self, balancer: SiteLoadBalancer, sites: List[Site]) -> Site:
        """加权负载均衡"""
        weighted_sites = []

        for site in sites:
            weight = balancer.weights.get(str(site.id), 1.0)
            weighted_sites.append((site, weight))

        # 加权随机选择
        total_weight = sum(weight for _, weight in weighted_sites)
        random_value = random.uniform(0, total_weight)

        current_weight = 0
        for site, weight in weighted_sites:
            current_weight += weight
            if random_value <= current_weight:
                # 更新负载均衡器状态
                balancer.total_requests += 1
                balancer.last_request_time = datetime.utcnow()
                self.db.commit()
                return site

        return weighted_sites[0][0]

    def _least_connections_selection(self, sites: List[Site]) -> Site:
        """最少连接数选择算法"""
        # 简化实现：选择最近请求数最少的站点
        site_requests = []

        for site in sites:
            stats = self.db.query(SiteStatistics).filter(SiteStatistics.site_id == site.id).first()
            recent_requests = stats.total_requests if stats else 0
            site_requests.append((site, recent_requests))

        # 选择请求数最少的站点
        site_requests.sort(key=lambda x: x[1])
        return site_requests[0][0]

    async def health_check_all_sites(self) -> Dict[int, bool]:
        """
        对所有启用的站点执行健康检查

        Returns:
            站点ID到健康状态的映射
        """
        sites = self.db.query(Site).filter(Site.is_enabled == True).all()

        health_results = {}
        tasks = []

        for site in sites:
            task = self._health_check_site(site)
            tasks.append((site.id, task))

        # 并发执行健康检查
        for site_id, task in tasks:
            try:
                is_healthy = await task
                health_results[site_id] = is_healthy
            except Exception as e:
                logger.error(f"站点 {site_id} 健康检查失败: {e}")
                health_results[site_id] = False

        return health_results

    async def _health_check_site(self, site: Site) -> bool:
        """
        执行单个站点的健康检查

        Args:
            site: 站点对象

        Returns:
            是否健康
        """
        try:
            # 这里应该实现具体的健康检查逻辑
            # 例如发送HTTP请求检查站点可用性
            import aiohttp

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                start_time = datetime.utcnow()
                async with session.get(site.current_url) as response:
                    response_time = (datetime.utcnow() - start_time).total_seconds()
                    is_healthy = response.status == 200

                    # 记录健康检查结果
                    health_check = SiteHealthCheck(
                        site_id=site.id,
                        is_healthy=is_healthy,
                        response_time=response_time * 1000,  # 转换为毫秒
                        status_code=response.status,
                        check_url=site.current_url
                    )
                    self.db.add(health_check)
                    self.db.commit()

                    return is_healthy

        except Exception as e:
            logger.error(f"站点 {site.name} 健康检查异常: {e}")

            # 记录健康检查失败
            health_check = SiteHealthCheck(
                site_id=site.id,
                is_healthy=False,
                error_message=str(e),
                check_url=site.current_url
            )
            self.db.add(health_check)
            self.db.commit()

            return False