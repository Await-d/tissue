"""
应用启动初始化脚本
在FastAPI应用启动前执行版本检测和数据库迁移
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.utils.version_manager import version_manager
from app.utils.logger import logger
from version import APP_VERSION


def pre_startup_check():
    """启动前检查"""
    logger.info("=== Tissue-Plus 应用启动前检查 ===")
    logger.info(f"当前版本: {APP_VERSION}")
    
    try:
        # 检查必要的目录和文件
        required_paths = [
            'alembic.ini',
            'app/',
            'version.py'
        ]
        
        missing_paths = []
        for path in required_paths:
            if not os.path.exists(path):
                missing_paths.append(path)
        
        if missing_paths:
            logger.error(f"缺少必要的文件或目录: {missing_paths}")
            return False
        
        # 检查数据目录
        data_dir = Path('data')
        data_dir.mkdir(exist_ok=True)
        logger.info("数据目录检查完成")
        
        return True
        
    except Exception as e:
        logger.error(f"启动前检查失败: {str(e)}")
        return False


def execute_version_migration():
    """执行版本迁移"""
    logger.info("=== 开始版本检测和迁移 ===")
    
    try:
        # 执行自动升级
        upgrade_result = version_manager.perform_auto_upgrade(force_backup=False)
        
        if upgrade_result['success']:
            if upgrade_result['version_updated']:
                logger.info("✅ 版本升级成功完成")
                
                if upgrade_result['migration_executed']:
                    logger.info("✅ 数据库迁移已执行")
                if upgrade_result['backup_created']:
                    logger.info("✅ 数据库备份已创建")
                    
                return True
            else:
                logger.info("ℹ️ 版本未更新，跳过迁移")
                return True
        else:
            logger.error("❌ 版本升级失败:")
            for error in upgrade_result['errors']:
                logger.error(f"  - {error}")
            
            # 根据错误类型决定是否继续启动
            critical_errors = [
                "数据库迁移执行失败",
                "alembic命令不可用",
                "数据库连接失败"
            ]
            
            has_critical_error = any(
                any(critical in error for critical in critical_errors) 
                for error in upgrade_result['errors']
            )
            
            if has_critical_error:
                logger.error("检测到关键错误，建议修复后重新启动")
                return False
            else:
                logger.warning("存在非关键错误，应用将继续启动")
                return True
        
    except Exception as e:
        logger.error(f"版本迁移过程中发生异常: {str(e)}")
        return False


def startup_health_check():
    """启动健康检查"""
    logger.info("=== 执行启动健康检查 ===")
    
    try:
        # 检查版本信息
        version_info = version_manager.get_version_info()
        logger.info(f"当前版本: {version_info['current_version']}")
        logger.info(f"存储版本: {version_info.get('stored_version', 'N/A')}")
        
        # 检查迁移要求
        requirements = version_manager.check_migration_requirements()
        
        issues = []
        if not requirements['alembic_available']:
            issues.append("Alembic不可用")
        if not requirements['config_exists']:
            issues.append("Alembic配置文件不存在")
        if not requirements['database_accessible']:
            issues.append("数据库不可访问")
        if not requirements['disk_space_sufficient']:
            issues.append("磁盘空间不足")
        
        if issues:
            logger.warning(f"健康检查发现问题: {', '.join(issues)}")
            return False
        else:
            logger.info("✅ 健康检查通过")
            return True
            
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return False


def main():
    """主启动流程"""
    logger.info("🚀 Tissue-Plus 应用启动")
    
    # 1. 启动前检查
    if not pre_startup_check():
        logger.error("启动前检查失败，应用退出")
        return False
    
    # 2. 版本迁移
    if not execute_version_migration():
        logger.error("版本迁移失败，应用退出")
        return False
    
    # 3. 健康检查
    health_ok = startup_health_check()
    if not health_ok:
        logger.warning("健康检查未完全通过，但应用将继续启动")
    
    logger.info("✅ 启动初始化完成，应用准备就绪")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)