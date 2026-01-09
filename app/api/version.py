"""
版本管理API
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.dependencies.security import get_current_user
from app.utils.version_manager import version_manager
from version import APP_VERSION


router = APIRouter(tags=["版本管理"])


class VersionInfo(BaseModel):
    """版本信息响应模型"""
    current_version: str
    stored_version: str = None
    last_updated: str = None
    migration_success: bool = True
    notes: str = ""
    is_updated: bool = False


class MigrationTrigger(BaseModel):
    """手动触发迁移请求"""
    force_backup: bool = True
    force_migration: bool = False


class ApiResponse(BaseModel):
    """统一API响应格式"""
    success: bool = True
    message: str = "操作成功"
    data: Any = None


@router.get("/info", response_model=VersionInfo, summary="获取版本信息")
async def get_version_info():
    """获取详细版本信息"""
    try:
        version_info = version_manager.get_version_info()
        
        return VersionInfo(
            current_version=version_info['current_version'],
            stored_version=version_info.get('stored_version'),
            last_updated=version_info.get('last_updated'),
            migration_success=version_info.get('migration_success', True),
            notes=version_info.get('notes', ''),
            is_updated=version_info.get('is_updated', False)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取版本信息失败: {str(e)}"
        )


@router.get("/history", response_model=ApiResponse, summary="获取版本历史")
async def get_version_history():
    """获取版本更新历史"""
    try:
        version_info = version_manager.get_version_info()
        history = version_info.get('version_history', [])
        
        return ApiResponse(
            success=True,
            message="获取版本历史成功",
            data={
                'current_version': version_info['current_version'],
                'history': history,
                'total_count': len(history)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取版本历史失败: {str(e)}"
        )


@router.get("/check", response_model=ApiResponse, summary="检查版本更新")
async def check_version_update():
    """检查是否有版本更新"""
    try:
        is_updated = version_manager.is_version_updated()
        stored_version = version_manager.get_stored_version()
        current_version = version_manager.current_version
        
        return ApiResponse(
            success=True,
            message="版本检查完成",
            data={
                'is_updated': is_updated,
                'current_version': current_version,
                'stored_version': stored_version,
                'needs_migration': is_updated
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"版本检查失败: {str(e)}"
        )


@router.post("/migrate", response_model=ApiResponse, summary="手动触发数据库迁移")
async def trigger_migration(request: MigrationTrigger):
    """手动触发数据库迁移"""
    try:
        # 检查迁移前置条件
        requirements = version_manager.check_migration_requirements()
        
        if requirements['errors']:
            return ApiResponse(
                success=False,
                message="迁移前置条件检查失败",
                data={
                    'errors': requirements['errors'],
                    'requirements': requirements
                }
            )
        
        # 执行迁移
        if request.force_migration or version_manager.is_version_updated():
            upgrade_result = version_manager.perform_auto_upgrade(
                force_backup=request.force_backup
            )
            
            return ApiResponse(
                success=upgrade_result['success'],
                message="数据库迁移执行完成" if upgrade_result['success'] else "数据库迁移执行失败",
                data=upgrade_result
            )
        else:
            return ApiResponse(
                success=True,
                message="版本未更新，无需执行迁移",
                data={'version_updated': False}
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"执行数据库迁移失败: {str(e)}"
        )


@router.get("/requirements", response_model=ApiResponse, summary="检查迁移前置条件")
async def check_migration_requirements():
    """检查数据库迁移前置条件"""
    try:
        requirements = version_manager.check_migration_requirements()
        
        all_satisfied = (
            requirements['alembic_available'] and
            requirements['config_exists'] and
            requirements['database_accessible'] and
            requirements['disk_space_sufficient']
        )
        
        return ApiResponse(
            success=all_satisfied,
            message="前置条件检查完成",
            data={
                'all_satisfied': all_satisfied,
                'details': requirements,
                'recommendation': (
                    "所有前置条件都满足，可以安全执行迁移" if all_satisfied 
                    else "存在未满足的前置条件，建议修复后再执行迁移"
                )
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"检查迁移前置条件失败: {str(e)}"
        )


@router.post("/force-save", response_model=ApiResponse, summary="强制保存当前版本信息")
async def force_save_version():
    """强制保存当前版本信息（用于修复版本记录）"""
    try:
        version_manager.save_version_info(
            version=APP_VERSION,
            migration_success=True,
            notes="手动强制保存版本信息"
        )
        
        return ApiResponse(
            success=True,
            message="版本信息已强制保存",
            data={
                'version': APP_VERSION,
                'saved_at': version_manager.get_stored_version()
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"强制保存版本信息失败: {str(e)}"
        )


@router.get("/status", response_model=ApiResponse, summary="获取版本系统状态")
async def get_version_status():
    """获取版本管理系统的整体状态"""
    try:
        version_info = version_manager.get_version_info()
        requirements = version_manager.check_migration_requirements()
        
        # 计算系统健康状态
        health_score = 0
        health_checks = [
            ('version_consistent', not version_info.get('is_updated', True)),
            ('migration_success', version_info.get('migration_success', True)),
            ('alembic_available', requirements['alembic_available']),
            ('config_exists', requirements['config_exists']),
            ('database_accessible', requirements['database_accessible']),
            ('disk_space_sufficient', requirements['disk_space_sufficient'])
        ]
        
        total_checks = len(health_checks)
        passed_checks = sum(1 for _, passed in health_checks if passed)
        health_score = (passed_checks / total_checks) * 100
        
        # 确定健康状态
        if health_score >= 90:
            health_status = "excellent"
            health_message = "系统状态优秀"
        elif health_score >= 70:
            health_status = "good"
            health_message = "系统状态良好"
        elif health_score >= 50:
            health_status = "warning"
            health_message = "系统状态存在警告"
        else:
            health_status = "critical"
            health_message = "系统状态需要关注"
        
        return ApiResponse(
            success=True,
            message="版本系统状态获取成功",
            data={
                'health_status': health_status,
                'health_score': health_score,
                'health_message': health_message,
                'health_checks': dict(health_checks),
                'version_info': version_info,
                'requirements': requirements,
                'recommendations': _get_recommendations(health_checks, version_info)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取版本系统状态失败: {str(e)}"
        )


def _get_recommendations(health_checks: list, version_info: dict) -> list:
    """根据健康检查结果生成建议"""
    recommendations = []
    
    failed_checks = [name for name, passed in health_checks if not passed]
    
    if 'version_consistent' in failed_checks:
        recommendations.append("检测到版本更新，建议执行数据库迁移")
    
    if 'migration_success' in failed_checks:
        recommendations.append("上次迁移失败，建议检查错误日志并重新执行迁移")
    
    if 'alembic_available' in failed_checks:
        recommendations.append("Alembic不可用，请检查安装和环境配置")
    
    if 'config_exists' in failed_checks:
        recommendations.append("缺少alembic.ini配置文件，请检查项目配置")
    
    if 'database_accessible' in failed_checks:
        recommendations.append("数据库连接失败，请检查数据库服务和连接配置")
    
    if 'disk_space_sufficient' in failed_checks:
        recommendations.append("磁盘空间不足，建议清理空间后再执行迁移")
    
    if not recommendations:
        recommendations.append("系统状态良好，无需特殊操作")
    
    return recommendations