#!/usr/bin/env python3
"""
站点管理初始化脚本 - 简化版本
创建默认的站点配置，基于当前项目的爬虫配置
"""
import sys
import os
from datetime import datetime

from app.db import SessionFactory
from app.utils.logger import logger
from sqlalchemy import text


def init_default_sites():
    """初始化默认站点配置"""
    try:
        logger.info("开始初始化站点管理系统...")

        # 由于数据库表已经通过alembic创建，我们只需要插入初始数据
        with SessionFactory() as db:
            # 检查是否已有站点配置
            result = db.execute(text("SELECT COUNT(*) FROM sites")).fetchone()
            existing_sites = result[0] if result else 0

            if existing_sites > 0:
                logger.info(f"已存在 {existing_sites} 个站点配置，跳过初始化")
                return True

            # 插入默认站点配置
            default_sites = [
                {
                    "name": "JavBus",
                    "spider_class": "JavbusSpider",
                    "base_url": "https://www.javbus.com",
                    "mirror_urls": '["https://www.javbus.org", "https://www.javbus.tv"]',
                    "site_type": "primary",
                    "priority": 1,
                    "weight": 1.0,
                    "status": "active",
                    "is_enabled": 1,
                    "supports_download": 1,
                    "supports_preview": 1,
                    "supports_search": 1,
                    "supports_actor_info": 1,
                    "supports_ranking": 0,
                    "rate_limit": 2,
                    "timeout": 30,
                    "max_retries": 3,
                    "region": "JP",
                    "language": "ja",
                    "description": "主要的JAV信息站点，提供详细的影片信息和下载链接",
                    "tags": '["primary", "japanese", "popular"]',
                    "create_time": datetime.utcnow().isoformat(),
                    "update_time": datetime.utcnow().isoformat()
                },
                {
                    "name": "JavDB",
                    "spider_class": "JavdbSpider",
                    "base_url": "https://javdb.com",
                    "mirror_urls": '["https://javdb36.com", "https://javdb47.com"]',
                    "site_type": "primary",
                    "priority": 2,
                    "weight": 0.8,
                    "status": "active",
                    "is_enabled": 1,
                    "supports_download": 1,
                    "supports_preview": 1,
                    "supports_search": 1,
                    "supports_actor_info": 1,
                    "supports_ranking": 1,
                    "rate_limit": 3,
                    "timeout": 30,
                    "max_retries": 3,
                    "region": "CN",
                    "language": "zh",
                    "description": "支持中文的JAV数据库，提供排行榜功能",
                    "tags": '["primary", "chinese", "ranking"]',
                    "create_time": datetime.utcnow().isoformat(),
                    "update_time": datetime.utcnow().isoformat()
                },
                {
                    "name": "Jav321",
                    "spider_class": "Jav321Spider",
                    "base_url": "https://www.jav321.com",
                    "mirror_urls": '[]',
                    "site_type": "secondary",
                    "priority": 3,
                    "weight": 0.6,
                    "status": "active",
                    "is_enabled": 1,
                    "supports_download": 1,
                    "supports_preview": 0,
                    "supports_search": 1,
                    "supports_actor_info": 1,
                    "supports_ranking": 0,
                    "rate_limit": 2,
                    "timeout": 30,
                    "max_retries": 3,
                    "region": "JP",
                    "language": "ja",
                    "description": "备用JAV信息站点，提供补充数据",
                    "tags": '["secondary", "backup"]',
                    "create_time": datetime.utcnow().isoformat(),
                    "update_time": datetime.utcnow().isoformat()
                },
                {
                    "name": "DMM",
                    "spider_class": "DmmSpider",
                    "base_url": "https://www.dmm.co.jp",
                    "mirror_urls": '[]',
                    "site_type": "secondary",
                    "priority": 4,
                    "weight": 0.5,
                    "status": "active",
                    "is_enabled": 1,
                    "supports_download": 0,
                    "supports_preview": 1,
                    "supports_search": 1,
                    "supports_actor_info": 1,
                    "supports_ranking": 0,
                    "rate_limit": 3,
                    "timeout": 30,
                    "max_retries": 3,
                    "region": "JP",
                    "language": "ja",
                    "description": "官方DMM站点，提供权威的影片信息",
                    "tags": '["official", "authoritative"]',
                    "create_time": datetime.utcnow().isoformat(),
                    "update_time": datetime.utcnow().isoformat()
                }
            ]

            created_sites = []
            site_ids = []

            for site_data in default_sites:
                # 插入站点记录
                columns = ', '.join(site_data.keys())
                values = ', '.join([f":{k}" for k in site_data.keys()])
                sql = f"INSERT INTO sites ({columns}) VALUES ({values})"

                result = db.execute(text(sql), site_data)
                site_id = result.lastrowid
                site_ids.append(site_id)
                created_sites.append(site_data['name'])

                # 为每个站点创建初始统计记录
                stats_data = {
                    "site_id": site_id,
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "stat_date": datetime.utcnow().isoformat(),
                    "last_reset": datetime.utcnow().isoformat(),
                    "create_time": datetime.utcnow().isoformat(),
                    "update_time": datetime.utcnow().isoformat()
                }

                stats_sql = """
                INSERT INTO site_statistics
                (site_id, total_requests, successful_requests, failed_requests, stat_date, last_reset, create_time, update_time)
                VALUES (:site_id, :total_requests, :successful_requests, :failed_requests, :stat_date, :last_reset, :create_time, :update_time)
                """
                db.execute(text(stats_sql), stats_data)

            # 创建默认故障转移规则
            rule_data = {
                "name": "默认故障转移",
                "description": "当主站点不可用时自动切换到备用站点",
                "is_active": 1,
                "trigger_error_rate": 0.6,
                "trigger_response_time": 15.0,
                "trigger_consecutive_failures": 3,
                "fallback_strategy": "priority",
                "fallback_sites": "[]",
                "recovery_success_rate": 0.8,
                "recovery_check_interval": 300,
                "create_time": datetime.utcnow().isoformat(),
                "update_time": datetime.utcnow().isoformat()
            }

            rule_sql = """
            INSERT INTO site_failover_rules
            (name, description, is_active, trigger_error_rate, trigger_response_time, trigger_consecutive_failures,
             fallback_strategy, fallback_sites, recovery_success_rate, recovery_check_interval, create_time, update_time)
            VALUES (:name, :description, :is_active, :trigger_error_rate, :trigger_response_time, :trigger_consecutive_failures,
                    :fallback_strategy, :fallback_sites, :recovery_success_rate, :recovery_check_interval, :create_time, :update_time)
            """
            db.execute(text(rule_sql), rule_data)

            # 创建默认负载均衡器
            if len(site_ids) >= 2:
                balancer_data = {
                    "name": "主要站点负载均衡",
                    "strategy": "weighted",
                    "is_active": 1,
                    "site_ids": f'[{site_ids[0]}, {site_ids[1]}]',
                    "weights": f'{{"{site_ids[0]}": 1.0, "{site_ids[1]}": 0.8}}',
                    "health_check_enabled": 1,
                    "health_check_interval": 60,
                    "total_requests": 0,
                    "current_active_sites": f'[{site_ids[0]}, {site_ids[1]}]',
                    "create_time": datetime.utcnow().isoformat(),
                    "update_time": datetime.utcnow().isoformat()
                }

                balancer_sql = """
                INSERT INTO site_load_balancers
                (name, strategy, is_active, site_ids, weights, health_check_enabled, health_check_interval,
                 total_requests, current_active_sites, create_time, update_time)
                VALUES (:name, :strategy, :is_active, :site_ids, :weights, :health_check_enabled, :health_check_interval,
                        :total_requests, :current_active_sites, :create_time, :update_time)
                """
                db.execute(text(balancer_sql), balancer_data)

            db.commit()
            logger.info(f"成功创建 {len(created_sites)} 个默认站点配置: {', '.join(created_sites)}")
            logger.info("站点管理系统初始化完成！")
            logger.info("您可以通过以下API端点管理站点：")
            logger.info("  - GET /api/site-management/sites - 获取站点列表")
            logger.info("  - POST /api/site-management/sites - 创建新站点")
            logger.info("  - GET /api/site-management/dashboard/overview - 查看概览")

            return True

    except Exception as e:
        logger.error(f"初始化站点管理失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = init_default_sites()
    sys.exit(0 if success else 1)