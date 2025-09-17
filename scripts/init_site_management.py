"""
站点管理初始化脚本
用于创建默认站点配置和故障转移规则
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models.site_management import (
    Site, SiteStatistics, SiteFailoverRule, SiteLoadBalancer,
    SiteStatus, SiteType
)
from app.schema import Setting


def create_default_sites(db_session):
    """创建默认站点配置"""

    # 默认站点配置
    default_sites = [
        {
            'name': 'JavDB',
            'spider_class': 'JavdbSpider',
            'base_url': 'https://javdb.com',
            'mirror_urls': ['https://javdb.com', 'https://javdb36.com', 'https://javdb37.com'],
            'site_type': SiteType.PRIMARY,
            'priority': 10,
            'weight': 1.0,
            'status': SiteStatus.ACTIVE,
            'is_enabled': True,
            'supports_download': True,
            'supports_preview': True,
            'supports_search': True,
            'supports_actor_info': True,
            'supports_ranking': True,
            'config': {
                'search_delay': 2,
                'max_pages': 10,
                'use_proxy': False
            },
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
            },
            'rate_limit': 2,
            'timeout': 30,
            'max_retries': 3,
            'region': 'JP',
            'language': 'zh',
            'description': 'JavDB - 日本成人视频数据库，支持搜索、下载、演员信息等功能',
            'tags': ['japanese', 'adult', 'database', 'comprehensive']
        },
        {
            'name': 'JavBus',
            'spider_class': 'JavbusSpider',
            'base_url': 'https://www.javbus.com',
            'mirror_urls': ['https://www.javbus.com', 'https://www.javbus.one'],
            'site_type': SiteType.PRIMARY,
            'priority': 20,
            'weight': 0.8,
            'status': SiteStatus.ACTIVE,
            'is_enabled': True,
            'supports_download': True,
            'supports_preview': False,
            'supports_search': True,
            'supports_actor_info': True,
            'supports_ranking': False,
            'config': {
                'search_delay': 1,
                'max_pages': 5,
                'use_cloudflare_bypass': True
            },
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.javbus.com'
            },
            'rate_limit': 1,
            'timeout': 25,
            'max_retries': 3,
            'region': 'JP',
            'language': 'zh',
            'description': 'JavBus - 老牌日本成人视频站点，数据量丰富',
            'tags': ['japanese', 'adult', 'established', 'downloads']
        },
        {
            'name': 'JAV321',
            'spider_class': 'Jav321Spider',
            'base_url': 'https://www.jav321.com',
            'mirror_urls': ['https://www.jav321.com'],
            'site_type': SiteType.SECONDARY,
            'priority': 30,
            'weight': 0.6,
            'status': SiteStatus.ACTIVE,
            'is_enabled': True,
            'supports_download': False,
            'supports_preview': True,
            'supports_search': True,
            'supports_actor_info': False,
            'supports_ranking': False,
            'config': {
                'search_delay': 3,
                'max_pages': 3
            },
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            'rate_limit': 3,
            'timeout': 20,
            'max_retries': 2,
            'region': 'JP',
            'language': 'en',
            'description': 'JAV321 - 提供视频预览和基础信息',
            'tags': ['japanese', 'adult', 'preview', 'basic']
        },
        {
            'name': 'DMM',
            'spider_class': 'DmmSpider',
            'base_url': 'https://www.dmm.co.jp',
            'mirror_urls': ['https://www.dmm.co.jp'],
            'site_type': SiteType.BACKUP,
            'priority': 40,
            'weight': 0.4,
            'status': SiteStatus.ACTIVE,
            'is_enabled': True,
            'supports_download': False,
            'supports_preview': False,
            'supports_search': True,
            'supports_actor_info': True,
            'supports_ranking': True,
            'config': {
                'search_delay': 5,
                'max_pages': 2,
                'require_age_verification': True
            },
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept-Language': 'ja,en;q=0.9'
            },
            'rate_limit': 5,
            'timeout': 30,
            'max_retries': 2,
            'region': 'JP',
            'language': 'ja',
            'description': 'DMM - 官方数字媒体市场，数据权威',
            'tags': ['japanese', 'adult', 'official', 'authoritative']
        }
    ]

    created_sites = []

    for site_data in default_sites:
        # 检查是否已存在
        existing = db_session.query(Site).filter(Site.name == site_data['name']).first()
        if existing:
            print(f"站点 '{site_data['name']}' 已存在，跳过创建")
            created_sites.append(existing)
            continue

        # 创建站点
        site = Site(**site_data)
        db_session.add(site)
        db_session.flush()  # 获取ID

        # 创建初始统计记录
        stats = SiteStatistics(
            site_id=site.id,
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            avg_response_time=0.0,
            max_response_time=0.0,
            min_response_time=0.0,
            videos_scraped=0,
            actors_scraped=0,
            downloads_provided=0,
            timeout_errors=0,
            connection_errors=0,
            parse_errors=0,
            rate_limit_errors=0,
            stat_date=datetime.utcnow(),
            last_reset=datetime.utcnow()
        )
        db_session.add(stats)

        created_sites.append(site)
        print(f"创建站点: {site.name}")

    db_session.commit()
    return created_sites


def create_default_failover_rules(db_session, sites):
    """创建默认故障转移规则"""

    # 主站点故障转移规则
    primary_sites = [site for site in sites if site.site_type == SiteType.PRIMARY]
    secondary_sites = [site for site in sites if site.site_type == SiteType.SECONDARY]
    backup_sites = [site for site in sites if site.site_type == SiteType.BACKUP]

    failover_rules = [
        {
            'name': '主站点高错误率故障转移',
            'description': '当主站点错误率超过50%时，转移到次要站点',
            'is_active': True,
            'trigger_error_rate': 0.5,
            'trigger_response_time': 30.0,
            'trigger_consecutive_failures': 3,
            'fallback_strategy': 'priority',
            'fallback_sites': [site.id for site in secondary_sites + backup_sites],
            'recovery_success_rate': 0.8,
            'recovery_check_interval': 300
        },
        {
            'name': '次要站点响应超时故障转移',
            'description': '当次要站点平均响应时间超过60秒时触发故障转移',
            'is_active': True,
            'trigger_error_rate': 0.3,
            'trigger_response_time': 60.0,
            'trigger_consecutive_failures': 5,
            'fallback_strategy': 'round_robin',
            'fallback_sites': [site.id for site in primary_sites + backup_sites],
            'recovery_success_rate': 0.7,
            'recovery_check_interval': 600
        },
        {
            'name': '紧急备用故障转移',
            'description': '当所有主要站点都不可用时使用备用站点',
            'is_active': True,
            'trigger_error_rate': 0.8,
            'trigger_response_time': 120.0,
            'trigger_consecutive_failures': 10,
            'fallback_strategy': 'weighted',
            'fallback_sites': [site.id for site in backup_sites],
            'recovery_success_rate': 0.6,
            'recovery_check_interval': 900
        }
    ]

    for rule_data in failover_rules:
        # 检查是否已存在
        existing = db_session.query(SiteFailoverRule).filter(
            SiteFailoverRule.name == rule_data['name']
        ).first()
        if existing:
            print(f"故障转移规则 '{rule_data['name']}' 已存在，跳过创建")
            continue

        rule = SiteFailoverRule(**rule_data)
        db_session.add(rule)
        print(f"创建故障转移规则: {rule.name}")

    db_session.commit()


def create_default_load_balancers(db_session, sites):
    """创建默认负载均衡器"""

    primary_sites = [site for site in sites if site.site_type == SiteType.PRIMARY]
    download_sites = [site for site in sites if site.supports_download]
    search_sites = [site for site in sites if site.supports_search]

    load_balancers = [
        {
            'name': '下载负载均衡器',
            'strategy': 'weighted',
            'is_active': True,
            'site_ids': [site.id for site in download_sites],
            'weights': {str(site.id): site.weight for site in download_sites},
            'health_check_enabled': True,
            'health_check_interval': 60,
            'total_requests': 0,
            'current_active_sites': [site.id for site in download_sites],
        },
        {
            'name': '搜索负载均衡器',
            'strategy': 'round_robin',
            'is_active': True,
            'site_ids': [site.id for site in search_sites],
            'weights': {},
            'health_check_enabled': True,
            'health_check_interval': 120,
            'total_requests': 0,
            'current_active_sites': [site.id for site in search_sites],
        },
        {
            'name': '主站点负载均衡器',
            'strategy': 'least_connections',
            'is_active': True,
            'site_ids': [site.id for site in primary_sites],
            'weights': {},
            'health_check_enabled': True,
            'health_check_interval': 30,
            'total_requests': 0,
            'current_active_sites': [site.id for site in primary_sites],
        }
    ]

    for balancer_data in load_balancers:
        # 检查是否已存在
        existing = db_session.query(SiteLoadBalancer).filter(
            SiteLoadBalancer.name == balancer_data['name']
        ).first()
        if existing:
            print(f"负载均衡器 '{balancer_data['name']}' 已存在，跳过创建")
            continue

        balancer = SiteLoadBalancer(**balancer_data)
        db_session.add(balancer)
        print(f"创建负载均衡器: {balancer.name}")

    db_session.commit()


def main():
    """主函数"""
    print("开始初始化站点管理系统...")

    # 创建数据库连接
    try:
        setting = Setting().app
        database_url = setting.database_url
        if database_url.startswith('sqlite'):
            # SQLite 需要特殊处理
            engine = create_engine(database_url, echo=False)
        else:
            engine = create_engine(database_url, echo=False)

        SessionLocal = sessionmaker(bind=engine)
        db_session = SessionLocal()

    except Exception as e:
        print(f"数据库连接失败: {e}")
        print("使用默认SQLite数据库...")
        engine = create_engine('sqlite:///./tissue.db', echo=False)
        SessionLocal = sessionmaker(bind=engine)
        db_session = SessionLocal()

    try:
        # 1. 创建默认站点
        print("\n1. 创建默认站点配置...")
        sites = create_default_sites(db_session)

        # 2. 创建故障转移规则
        print("\n2. 创建默认故障转移规则...")
        create_default_failover_rules(db_session, sites)

        # 3. 创建负载均衡器
        print("\n3. 创建默认负载均衡器...")
        create_default_load_balancers(db_session, sites)

        print(f"\n✅ 站点管理系统初始化完成！")
        print(f"📊 创建了 {len(sites)} 个站点")
        print(f"🔄 配置了故障转移和负载均衡")
        print(f"🚀 系统已准备就绪")

    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        db_session.rollback()
        raise

    finally:
        db_session.close()


if __name__ == "__main__":
    main()