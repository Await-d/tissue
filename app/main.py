'''
Author: Await
Date: 2025-05-24 17:05:38
LastEditors: Await
LastEditTime: 2025-05-26 18:33:25
Description: 请填写简介
'''
# 初始化兼容性修复
from app.utils.compat import init_compatibility
init_compatibility()

from fastapi import FastAPI

from app import middleware, db, exception
from app.scheduler import scheduler
from app.api import api_router, actor_subscribe
from app.utils.version_manager import version_manager
from app.utils.logger import logger
from version import APP_VERSION

app = FastAPI(
    title="Tissue-Plus",
    description="A tool for scraping and managing JAV metadata. Based on chris-2s/tissue project.",
    version=APP_VERSION
)

middleware.init(app)
exception.init(app)


@app.on_event("startup")
def on_startup():
    # 版本检测和自动迁移
    perform_version_check_and_migration()
    
    # 数据库Schema检查和自动修复
    perform_schema_checks()
    
    # 注册路由
    logger.info("开始注册API路由...")
    try:
        # 打印路由信息
        logger.info(f"API路由器中的路由数: {len(api_router.routes)}")
        
        # 注册主API路由
        app.include_router(api_router, prefix="/api")
        logger.info("API路由注册成功")
        
        # 注册actor-subscribe路由
        app.include_router(
            actor_subscribe.router,
            prefix="/api/actor-subscribe",
            tags=["actor-subscribe"],
        )
        logger.info("actor-subscribe路由注册成功")
        
        # 打印路由注册后的信息
        auto_download_routes = [r for r in app.routes if '/api/auto-download/' in getattr(r, 'path', '')]
        logger.info(f"注册后，自动下载相关路由数量: {len(auto_download_routes)}")
        
    except Exception as e:
        logger.error(f"注册路由时出错: {str(e)}")
    
    # 初始化数据库和调度器
    db.init()
    scheduler.init()


def perform_version_check_and_migration():
    """执行版本检测和自动迁移"""
    try:
        logger.info(f"应用启动 - 当前版本: {APP_VERSION}")
        
        # 执行自动升级
        upgrade_result = version_manager.perform_auto_upgrade(force_backup=True)
        
        if upgrade_result['success']:
            if upgrade_result['version_updated']:
                logger.info("版本升级成功完成")
                
                # 记录升级详情
                if upgrade_result['migration_executed']:
                    logger.info("数据库迁移已执行")
                if upgrade_result['backup_created']:
                    logger.info("数据库备份已创建")
                    
            else:
                logger.info("版本未更新，应用正常启动")
        else:
            logger.error("版本升级过程中出现错误:")
            for error in upgrade_result['errors']:
                logger.error(f"  - {error}")
            
            # 升级失败时的处理策略
            if upgrade_result['version_updated']:
                logger.warning("尽管升级失败，应用将尝试继续启动")
                logger.warning("建议检查错误日志并手动执行数据库迁移")
        
        # 记录警告信息
        for warning in upgrade_result.get('warnings', []):
            logger.warning(warning)
            
    except Exception as e:
        logger.error(f"版本检测和迁移过程中发生异常: {str(e)}")
        logger.warning("应用将继续启动，但可能存在版本不一致的问题")


def perform_schema_checks():
    """执行数据库Schema检查和自动修复"""
    try:
        logger.info("开始执行数据库Schema检查...")
        
        from app.utils.db_schema_checker import schema_checker
        
        # 运行Schema检查
        check_result = schema_checker.run_schema_checks()
        
        if check_result['success']:
            logger.info("数据库Schema检查完成")
            for check in check_result['checks_performed']:
                logger.info(f"  - {check}")
        else:
            logger.error("数据库Schema检查失败:")
            for error in check_result['errors']:
                logger.error(f"  - {error}")
            logger.warning("应用将继续启动，但可能存在数据库结构问题")
            
    except Exception as e:
        logger.error(f"Schema检查过程中发生异常: {str(e)}")
        logger.warning("应用将继续启动，但数据库结构可能不完整")


if __name__ == '__main__':
    pass
