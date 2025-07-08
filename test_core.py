import os
import sys
import traceback

# 设置环境变量以启用详细调试
os.environ["PYTHONUNBUFFERED"] = "1"
os.environ["PYTHONFAULTHANDLER"] = "1"

# 创建日志文件
log_file = open("test_core.log", "w")
sys.stdout = log_file
sys.stderr = log_file

try:
    print("1. 导入基础模块")
    import app.utils.compat
    app.utils.compat.init_compatibility()
    print("✓ 成功导入兼容性模块")
    
    print("\n2. 导入数据库模块")
    from app.db import get_db, SessionFactory
    print("✓ 成功导入数据库模块")
    
    print("\n3. 测试数据库连接")
    db = next(get_db())
    print("✓ 成功连接数据库")
    
    print("\n4. 导入模型")
    from app.db.models.auto_download import AutoDownloadRule, AutoDownloadSubscription, DownloadStatus, TimeRangeType
    print("✓ 成功导入自动下载模型")
    
    print("\n5. 导入服务")
    from app.service.auto_download import AutoDownloadService
    print("✓ 成功导入自动下载服务")
    
    print("\n6. 导入视频收集器")
    from app.utils.video_collector import VideoCollector
    print("✓ 成功导入视频收集器")
    
    print("\n7. 导入调度器")
    from app.scheduler import scheduler
    print("✓ 成功导入调度器")
    
    print("\n8. 尝试创建服务实例")
    auto_download_service = AutoDownloadService()
    print("✓ 成功创建自动下载服务实例")
    
    print("\n9. 导入主应用")
    from app import main
    print("✓ 成功导入主应用")
    
    print("\n测试完成，所有核心功能正常！")
    
except Exception as e:
    print(f"\n❌ 错误: {e}", file=sys.stderr)
    print("\n详细错误信息:", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    
finally:
    # 关闭日志文件
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    log_file.close()
    
    # 打印完成信息
    print("测试完成，请查看 test_core.log 文件获取详细信息") 