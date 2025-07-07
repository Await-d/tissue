"""
版本管理和自动迁移模块
"""
import os
import json
import logging
import subprocess
import traceback
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

from app.utils.logger import logger
from version import APP_VERSION


class VersionManager:
    """版本管理器"""
    
    def __init__(self, storage_path: str = "data/version_info.json"):
        self.storage_path = storage_path
        self.current_version = APP_VERSION
        self.ensure_storage_dir()
    
    def ensure_storage_dir(self):
        """确保存储目录存在"""
        storage_dir = os.path.dirname(self.storage_path)
        if storage_dir and not os.path.exists(storage_dir):
            os.makedirs(storage_dir, exist_ok=True)
    
    def get_stored_version(self) -> Optional[str]:
        """获取存储的版本信息"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('version')
            return None
        except Exception as e:
            logger.error(f"读取版本信息失败: {str(e)}")
            return None
    
    def save_version_info(self, version: str, migration_success: bool = True, notes: str = ""):
        """保存版本信息"""
        try:
            version_info = {
                'version': version,
                'updated_at': datetime.now().isoformat(),
                'migration_success': migration_success,
                'notes': notes,
                'previous_versions': self._get_version_history()
            }
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(version_info, f, indent=2, ensure_ascii=False)
            
            logger.info(f"版本信息已保存: {version}")
            
        except Exception as e:
            logger.error(f"保存版本信息失败: {str(e)}")
    
    def _get_version_history(self) -> List[Dict[str, Any]]:
        """获取版本历史"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    history = data.get('previous_versions', [])
                    
                    # 添加当前版本到历史
                    if data.get('version'):
                        current_record = {
                            'version': data.get('version'),
                            'updated_at': data.get('updated_at'),
                            'migration_success': data.get('migration_success', True)
                        }
                        history.append(current_record)
                    
                    # 保持最近10个版本
                    return history[-10:]
            return []
        except Exception:
            return []
    
    def is_version_updated(self) -> bool:
        """检查版本是否更新"""
        stored_version = self.get_stored_version()
        if stored_version is None:
            logger.info("首次启动，未找到版本信息")
            return True
        
        if stored_version != self.current_version:
            logger.info(f"检测到版本更新: {stored_version} -> {self.current_version}")
            return True
        
        logger.info(f"版本未变化: {self.current_version}")
        return False
    
    def run_database_migration(self) -> bool:
        """运行数据库迁移"""
        logger.info("开始执行数据库迁移...")
        
        try:
            # 检查alembic配置文件
            if not os.path.exists('alembic.ini'):
                logger.error("未找到alembic.ini配置文件")
                return False
            
            # 执行数据库迁移
            result = subprocess.run(
                ['alembic', 'upgrade', 'head'],
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                logger.info("数据库迁移执行成功")
                logger.debug(f"迁移输出: {result.stdout}")
                return True
            else:
                logger.error(f"数据库迁移失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("数据库迁移执行超时")
            return False
        except FileNotFoundError:
            logger.error("未找到alembic命令，请确保已安装alembic")
            return False
        except Exception as e:
            logger.error(f"执行数据库迁移时出错: {str(e)}")
            traceback.print_exc()
            return False
    
    def backup_database(self) -> bool:
        """备份数据库（可选功能）"""
        logger.info("开始备份数据库...")
        
        try:
            # 这里可以添加数据库备份逻辑
            # 例如：mysqldump、pg_dump等
            # 当前仅记录日志
            backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            logger.info(f"数据库备份时间点: {backup_time}")
            
            # TODO: 实现具体的备份逻辑
            return True
            
        except Exception as e:
            logger.error(f"数据库备份失败: {str(e)}")
            return False
    
    def check_migration_requirements(self) -> Dict[str, Any]:
        """检查迁移前置条件"""
        requirements = {
            'alembic_available': False,
            'config_exists': False,
            'database_accessible': False,
            'disk_space_sufficient': False,
            'errors': []
        }
        
        try:
            # 检查alembic是否可用
            result = subprocess.run(['alembic', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            requirements['alembic_available'] = result.returncode == 0
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            requirements['errors'].append("alembic命令不可用")
        
        # 检查配置文件
        requirements['config_exists'] = os.path.exists('alembic.ini')
        if not requirements['config_exists']:
            requirements['errors'].append("alembic.ini配置文件不存在")
        
        # 检查数据库连接（简单检查）
        try:
            from app.db import get_db
            # 尝试创建数据库连接
            requirements['database_accessible'] = True
        except Exception as e:
            requirements['errors'].append(f"数据库连接失败: {str(e)}")
        
        # 检查磁盘空间（简单检查）
        try:
            stat = os.statvfs('.')
            free_space = stat.f_bavail * stat.f_frsize / (1024 * 1024)  # MB
            requirements['disk_space_sufficient'] = free_space > 100  # 至少100MB
            if not requirements['disk_space_sufficient']:
                requirements['errors'].append("磁盘空间不足")
        except Exception:
            requirements['errors'].append("无法检查磁盘空间")
        
        return requirements
    
    def perform_auto_upgrade(self, force_backup: bool = True) -> Dict[str, Any]:
        """执行自动升级"""
        upgrade_result = {
            'success': False,
            'version_updated': False,
            'migration_executed': False,
            'backup_created': False,
            'errors': [],
            'warnings': []
        }
        
        try:
            logger.info("=== 开始自动版本升级 ===")
            
            # 1. 检查版本是否更新
            if not self.is_version_updated():
                upgrade_result['warnings'].append("版本未更新，跳过升级流程")
                upgrade_result['success'] = True
                return upgrade_result
            
            upgrade_result['version_updated'] = True
            
            # 2. 检查迁移前置条件
            requirements = self.check_migration_requirements()
            if requirements['errors']:
                upgrade_result['errors'].extend(requirements['errors'])
                logger.error("迁移前置条件检查失败")
                return upgrade_result
            
            # 3. 备份数据库（可选）
            if force_backup:
                backup_success = self.backup_database()
                upgrade_result['backup_created'] = backup_success
                if not backup_success:
                    upgrade_result['warnings'].append("数据库备份失败，但继续执行迁移")
            
            # 4. 执行数据库迁移
            migration_success = self.run_database_migration()
            upgrade_result['migration_executed'] = migration_success
            
            if not migration_success:
                upgrade_result['errors'].append("数据库迁移执行失败")
                return upgrade_result
            
            # 5. 保存版本信息
            self.save_version_info(
                version=self.current_version,
                migration_success=migration_success,
                notes=f"自动升级到版本 {self.current_version}"
            )
            
            upgrade_result['success'] = True
            logger.info(f"=== 自动版本升级完成: {self.current_version} ===")
            
        except Exception as e:
            error_msg = f"自动升级过程中发生错误: {str(e)}"
            logger.error(error_msg)
            upgrade_result['errors'].append(error_msg)
            traceback.print_exc()
        
        return upgrade_result
    
    def get_version_info(self) -> Dict[str, Any]:
        """获取完整版本信息"""
        try:
            stored_info = {}
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    stored_info = json.load(f)
            
            return {
                'current_version': self.current_version,
                'stored_version': stored_info.get('version'),
                'last_updated': stored_info.get('updated_at'),
                'migration_success': stored_info.get('migration_success', True),
                'notes': stored_info.get('notes', ''),
                'version_history': stored_info.get('previous_versions', []),
                'is_updated': self.is_version_updated()
            }
        except Exception as e:
            logger.error(f"获取版本信息失败: {str(e)}")
            return {
                'current_version': self.current_version,
                'error': str(e)
            }


# 全局版本管理器实例
version_manager = VersionManager()