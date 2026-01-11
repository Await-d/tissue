"""add site management tables

Revision ID: 20250917_add_site_management_tables
Revises: 20250710_add_error_message_field
Create Date: 2025-09-17 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '20250917_add_site_management_tables'
down_revision = 'ea81650a67f7'
branch_labels = None
depends_on = None


def get_existing_tables():
    """获取数据库中已存在的表列表"""
    bind = op.get_bind()
    inspector = inspect(bind)
    return inspector.get_table_names()


def get_existing_indexes(table_name):
    """获取指定表的索引列表"""
    bind = op.get_bind()
    inspector = inspect(bind)
    try:
        return [idx['name'] for idx in inspector.get_indexes(table_name)]
    except Exception:
        return []


def safe_drop_index(index_name, table_name):
    """安全删除索引（如果存在）"""
    existing_indexes = get_existing_indexes(table_name)
    if index_name in existing_indexes:
        op.drop_index(index_name, table_name=table_name)


def upgrade():
    """Create site management tables"""

    existing_tables = get_existing_tables()

    # 创建站点表（如果不存在）
    if 'sites' not in existing_tables:
        op.create_table('sites',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('create_by', sa.Integer(), nullable=True),
            sa.Column('create_time', sa.DateTime(timezone=True), nullable=True),
            sa.Column('update_by', sa.Integer(), nullable=True),
            sa.Column('update_time', sa.DateTime(timezone=True), nullable=True),

            # 基础信息
            sa.Column('name', sa.String(length=100), nullable=False, comment='站点名称'),
            sa.Column('spider_class', sa.String(length=100), nullable=False, comment='爬虫类名'),
            sa.Column('base_url', sa.String(length=500), nullable=False, comment='站点基础URL'),
            sa.Column('mirror_urls', sa.JSON(), nullable=True, comment='镜像URL列表'),

            # 分类和优先级
            sa.Column('site_type', sa.String(length=20), nullable=True, comment='站点类型'),
            sa.Column('priority', sa.Integer(), nullable=True, comment='优先级'),
            sa.Column('weight', sa.Float(), nullable=True, comment='权重值'),

            # 状态管理
            sa.Column('status', sa.String(length=20), nullable=True, comment='站点状态'),
            sa.Column('is_enabled', sa.Boolean(), nullable=True, comment='是否启用'),

            # 功能支持
            sa.Column('supports_download', sa.Boolean(), nullable=True, comment='是否支持下载'),
            sa.Column('supports_preview', sa.Boolean(), nullable=True, comment='是否支持预览'),
            sa.Column('supports_search', sa.Boolean(), nullable=True, comment='是否支持搜索'),
            sa.Column('supports_actor_info', sa.Boolean(), nullable=True, comment='是否支持演员信息'),
            sa.Column('supports_ranking', sa.Boolean(), nullable=True, comment='是否支持排行榜'),

            # 配置信息
            sa.Column('config', sa.JSON(), nullable=True, comment='站点特定配置'),
            sa.Column('headers', sa.JSON(), nullable=True, comment='自定义请求头'),
            sa.Column('rate_limit', sa.Integer(), nullable=True, comment='请求间隔(秒)'),
            sa.Column('timeout', sa.Integer(), nullable=True, comment='请求超时时间(秒)'),
            sa.Column('max_retries', sa.Integer(), nullable=True, comment='最大重试次数'),

            # 地理位置和语言
            sa.Column('region', sa.String(length=10), nullable=True, comment='地理区域'),
            sa.Column('language', sa.String(length=10), nullable=True, comment='主要语言'),

            # 描述信息
            sa.Column('description', sa.Text(), nullable=True, comment='站点描述'),
            sa.Column('tags', sa.JSON(), nullable=True, comment='站点标签'),

            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )
        op.create_index(op.f('ix_sites_id'), 'sites', ['id'], unique=False)

    # 创建站点统计表（如果不存在）
    if 'site_statistics' not in existing_tables:
        op.create_table('site_statistics',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('create_by', sa.Integer(), nullable=True),
            sa.Column('create_time', sa.DateTime(timezone=True), nullable=True),
            sa.Column('update_by', sa.Integer(), nullable=True),
            sa.Column('update_time', sa.DateTime(timezone=True), nullable=True),

            sa.Column('site_id', sa.Integer(), nullable=False, comment='关联站点ID'),

            # 请求统计
            sa.Column('total_requests', sa.Integer(), nullable=True, comment='总请求数'),
            sa.Column('successful_requests', sa.Integer(), nullable=True, comment='成功请求数'),
            sa.Column('failed_requests', sa.Integer(), nullable=True, comment='失败请求数'),

            # 性能统计
            sa.Column('avg_response_time', sa.Float(), nullable=True, comment='平均响应时间(秒)'),
            sa.Column('max_response_time', sa.Float(), nullable=True, comment='最大响应时间(秒)'),
            sa.Column('min_response_time', sa.Float(), nullable=True, comment='最小响应时间(秒)'),

            # 数据统计
            sa.Column('videos_scraped', sa.Integer(), nullable=True, comment='抓取的视频数量'),
            sa.Column('actors_scraped', sa.Integer(), nullable=True, comment='抓取的演员数量'),
            sa.Column('downloads_provided', sa.Integer(), nullable=True, comment='提供的下载数量'),

            # 错误统计
            sa.Column('timeout_errors', sa.Integer(), nullable=True, comment='超时错误数'),
            sa.Column('connection_errors', sa.Integer(), nullable=True, comment='连接错误数'),
            sa.Column('parse_errors', sa.Integer(), nullable=True, comment='解析错误数'),
            sa.Column('rate_limit_errors', sa.Integer(), nullable=True, comment='频率限制错误数'),

            # 时间范围
            sa.Column('stat_date', sa.DateTime(), nullable=True, comment='统计日期'),
            sa.Column('last_reset', sa.DateTime(), nullable=True, comment='上次重置时间'),

            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ondelete='CASCADE')
        )
        op.create_index(op.f('ix_site_statistics_id'), 'site_statistics', ['id'], unique=False)
        op.create_index(op.f('ix_site_statistics_site_id'), 'site_statistics', ['site_id'], unique=False)

    # 创建站点健康检查表（如果不存在）
    if 'site_health_checks' not in existing_tables:
        op.create_table('site_health_checks',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('create_by', sa.Integer(), nullable=True),
            sa.Column('create_time', sa.DateTime(timezone=True), nullable=True),
            sa.Column('update_by', sa.Integer(), nullable=True),
            sa.Column('update_time', sa.DateTime(timezone=True), nullable=True),

            sa.Column('site_id', sa.Integer(), nullable=False, comment='关联站点ID'),

            # 检查结果
            sa.Column('is_healthy', sa.Boolean(), nullable=True, comment='是否健康'),
            sa.Column('response_time', sa.Float(), nullable=True, comment='响应时间(毫秒)'),
            sa.Column('status_code', sa.Integer(), nullable=True, comment='HTTP状态码'),
            sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),

            # 检查详情
            sa.Column('check_type', sa.String(length=50), nullable=True, comment='检查类型'),
            sa.Column('check_url', sa.String(length=500), nullable=True, comment='检查的URL'),

            # 时间信息
            sa.Column('checked_at', sa.DateTime(), nullable=True, comment='检查时间'),
            sa.Column('next_check', sa.DateTime(), nullable=True, comment='下次检查时间'),

            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ondelete='CASCADE')
        )
        op.create_index(op.f('ix_site_health_checks_id'), 'site_health_checks', ['id'], unique=False)
        op.create_index(op.f('ix_site_health_checks_site_id'), 'site_health_checks', ['site_id'], unique=False)
        op.create_index(op.f('ix_site_health_checks_checked_at'), 'site_health_checks', ['checked_at'], unique=False)

    # 创建站点错误日志表（如果不存在）
    if 'site_error_logs' not in existing_tables:
        op.create_table('site_error_logs',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('create_by', sa.Integer(), nullable=True),
            sa.Column('create_time', sa.DateTime(timezone=True), nullable=True),
            sa.Column('update_by', sa.Integer(), nullable=True),
            sa.Column('update_time', sa.DateTime(timezone=True), nullable=True),

            sa.Column('site_id', sa.Integer(), nullable=False, comment='关联站点ID'),

            # 错误信息
            sa.Column('error_type', sa.String(length=100), nullable=True, comment='错误类型'),
            sa.Column('error_message', sa.Text(), nullable=True, comment='错误消息'),
            sa.Column('error_details', sa.JSON(), nullable=True, comment='错误详情'),

            # 请求信息
            sa.Column('request_url', sa.String(length=500), nullable=True, comment='请求URL'),
            sa.Column('request_method', sa.String(length=10), nullable=True, comment='请求方法'),
            sa.Column('request_headers', sa.JSON(), nullable=True, comment='请求头'),

            # 响应信息
            sa.Column('response_code', sa.Integer(), nullable=True, comment='响应状态码'),
            sa.Column('response_time', sa.Float(), nullable=True, comment='响应时间'),

            # 上下文信息
            sa.Column('operation', sa.String(length=100), nullable=True, comment='操作类型'),
            sa.Column('video_number', sa.String(length=50), nullable=True, comment='相关视频番号'),
            sa.Column('actor_name', sa.String(length=100), nullable=True, comment='相关演员名称'),

            # 处理状态
            sa.Column('is_resolved', sa.Boolean(), nullable=True, comment='是否已解决'),
            sa.Column('resolution_note', sa.Text(), nullable=True, comment='解决方案说明'),

            # 时间信息
            sa.Column('occurred_at', sa.DateTime(), nullable=True, comment='发生时间'),
            sa.Column('resolved_at', sa.DateTime(), nullable=True, comment='解决时间'),

            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ondelete='CASCADE')
        )
        op.create_index(op.f('ix_site_error_logs_id'), 'site_error_logs', ['id'], unique=False)
        op.create_index(op.f('ix_site_error_logs_site_id'), 'site_error_logs', ['site_id'], unique=False)
        op.create_index(op.f('ix_site_error_logs_occurred_at'), 'site_error_logs', ['occurred_at'], unique=False)
        op.create_index(op.f('ix_site_error_logs_error_type'), 'site_error_logs', ['error_type'], unique=False)

    # 创建故障转移规则表（如果不存在）
    if 'site_failover_rules' not in existing_tables:
        op.create_table('site_failover_rules',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('create_by', sa.Integer(), nullable=True),
            sa.Column('create_time', sa.DateTime(timezone=True), nullable=True),
            sa.Column('update_by', sa.Integer(), nullable=True),
            sa.Column('update_time', sa.DateTime(timezone=True), nullable=True),

            # 规则基础信息
            sa.Column('name', sa.String(length=100), nullable=False, comment='规则名称'),
            sa.Column('description', sa.Text(), nullable=True, comment='规则描述'),
            sa.Column('is_active', sa.Boolean(), nullable=True, comment='是否激活'),

            # 触发条件
            sa.Column('trigger_error_rate', sa.Float(), nullable=True, comment='触发的错误率阈值'),
            sa.Column('trigger_response_time', sa.Float(), nullable=True, comment='触发的响应时间阈值(秒)'),
            sa.Column('trigger_consecutive_failures', sa.Integer(), nullable=True, comment='连续失败次数阈值'),

            # 故障转移策略
            sa.Column('fallback_strategy', sa.String(length=50), nullable=True, comment='故障转移策略'),
            sa.Column('fallback_sites', sa.JSON(), nullable=True, comment='备用站点ID列表'),

            # 恢复条件
            sa.Column('recovery_success_rate', sa.Float(), nullable=True, comment='恢复的成功率阈值'),
            sa.Column('recovery_check_interval', sa.Integer(), nullable=True, comment='恢复检查间隔(秒)'),

            # 时间信息
            sa.Column('last_triggered', sa.DateTime(), nullable=True, comment='上次触发时间'),
            sa.Column('last_recovered', sa.DateTime(), nullable=True, comment='上次恢复时间'),

            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_site_failover_rules_id'), 'site_failover_rules', ['id'], unique=False)
        op.create_index(op.f('ix_site_failover_rules_name'), 'site_failover_rules', ['name'], unique=False)

    # 创建负载均衡器表（如果不存在）
    if 'site_load_balancers' not in existing_tables:
        op.create_table('site_load_balancers',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('create_by', sa.Integer(), nullable=True),
            sa.Column('create_time', sa.DateTime(timezone=True), nullable=True),
            sa.Column('update_by', sa.Integer(), nullable=True),
            sa.Column('update_time', sa.DateTime(timezone=True), nullable=True),

            # 负载均衡配置
            sa.Column('name', sa.String(length=100), nullable=False, comment='负载均衡器名称'),
            sa.Column('strategy', sa.String(length=50), nullable=True, comment='负载均衡策略'),
            sa.Column('is_active', sa.Boolean(), nullable=True, comment='是否激活'),

            # 站点组
            sa.Column('site_ids', sa.JSON(), nullable=True, comment='参与负载均衡的站点ID列表'),
            sa.Column('weights', sa.JSON(), nullable=True, comment='站点权重配置'),

            # 健康检查
            sa.Column('health_check_enabled', sa.Boolean(), nullable=True, comment='是否启用健康检查'),
            sa.Column('health_check_interval', sa.Integer(), nullable=True, comment='健康检查间隔(秒)'),

            # 统计信息
            sa.Column('total_requests', sa.Integer(), nullable=True, comment='总分发请求数'),
            sa.Column('last_request_time', sa.DateTime(), nullable=True, comment='上次请求时间'),

            # 当前状态
            sa.Column('current_active_sites', sa.JSON(), nullable=True, comment='当前活跃站点列表'),
            sa.Column('last_rotation_time', sa.DateTime(), nullable=True, comment='上次轮换时间'),

            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_site_load_balancers_id'), 'site_load_balancers', ['id'], unique=False)
        op.create_index(op.f('ix_site_load_balancers_name'), 'site_load_balancers', ['name'], unique=False)


def downgrade():
    """Drop site management tables"""

    existing_tables = get_existing_tables()

    # 删除索引和表（按依赖关系逆序，只删除存在的表）
    if 'site_load_balancers' in existing_tables:
        safe_drop_index(op.f('ix_site_load_balancers_name'), 'site_load_balancers')
        safe_drop_index(op.f('ix_site_load_balancers_id'), 'site_load_balancers')
        op.drop_table('site_load_balancers')

    if 'site_failover_rules' in existing_tables:
        safe_drop_index(op.f('ix_site_failover_rules_name'), 'site_failover_rules')
        safe_drop_index(op.f('ix_site_failover_rules_id'), 'site_failover_rules')
        op.drop_table('site_failover_rules')

    if 'site_error_logs' in existing_tables:
        safe_drop_index(op.f('ix_site_error_logs_error_type'), 'site_error_logs')
        safe_drop_index(op.f('ix_site_error_logs_occurred_at'), 'site_error_logs')
        safe_drop_index(op.f('ix_site_error_logs_site_id'), 'site_error_logs')
        safe_drop_index(op.f('ix_site_error_logs_id'), 'site_error_logs')
        op.drop_table('site_error_logs')

    if 'site_health_checks' in existing_tables:
        safe_drop_index(op.f('ix_site_health_checks_checked_at'), 'site_health_checks')
        safe_drop_index(op.f('ix_site_health_checks_site_id'), 'site_health_checks')
        safe_drop_index(op.f('ix_site_health_checks_id'), 'site_health_checks')
        op.drop_table('site_health_checks')

    if 'site_statistics' in existing_tables:
        safe_drop_index(op.f('ix_site_statistics_site_id'), 'site_statistics')
        safe_drop_index(op.f('ix_site_statistics_id'), 'site_statistics')
        op.drop_table('site_statistics')

    if 'sites' in existing_tables:
        safe_drop_index(op.f('ix_sites_id'), 'sites')
        op.drop_table('sites')
