#!/usr/bin/env python

# 导入必要的模块
import uvicorn
import importlib
import inspect
import json
import pprint

# 手动输出日志
print("\n=== API模块检查 ===")

# 检查模块导入情况
try:
    from app.api import auto_download
    print("✅ app.api.auto_download 模块导入成功")
    
    # 打印模块内容
    router = getattr(auto_download, 'router', None)
    print(f"router存在: {router is not None}")
    
    if router:
        print(f"路由器类型: {type(router).__name__}")
        print(f"路由数量: {len(getattr(router, 'routes', []))}")
        
        # 打印路由详细信息
        print("\n路由详情:")
        for i, route in enumerate(router.routes):
            endpoint = getattr(route, 'endpoint', None)
            endpoint_name = endpoint.__name__ if endpoint else 'Unknown'
            methods = getattr(route, 'methods', set())
            methods_str = ', '.join(methods) if methods else 'N/A'
            path = getattr(route, 'path', 'Unknown')
            
            print(f"路由 {i+1}: {path} [{methods_str}] -> {endpoint_name}")
            
except Exception as e:
    print(f"❌ 导入失败: {str(e)}")
    
# 检查API路由初始化
print("\n=== API路由初始化检查 ===")
try:
    # 重新加载API模块以查看实际执行了什么
    import app.api
    importlib.reload(app.api)
    
    print(f"✅ API路由初始化成功")
    print(f"路由器类型: {type(app.api.api_router).__name__}")
    print(f"路由数量: {len(app.api.api_router.routes)}")
    
    # 检查auto_download路由是否被包含
    included_routers = []
    for route in app.api.api_router.routes:
        if hasattr(route, 'prefix'):
            included_routers.append(route.prefix)
    
    print(f"包含的路由前缀: {included_routers}")
    
    # 检查是否有/auto-download前缀
    if '/auto-download' in included_routers:
        print("✅ /auto-download路由已包含")
    else:
        print("❌ /auto-download路由未包含")
        
except Exception as e:
    print(f"❌ API初始化检查失败: {str(e)}")
    
# 主应用测试
print("\n=== 主应用路由检查 ===")
try:
    from app.main import app
    
    routes = []
    for route in app.routes:
        route_info = {
            'path': getattr(route, 'path', 'Unknown'),
            'methods': list(getattr(route, 'methods', set())),
            'name': getattr(route, 'name', 'Unknown'),
        }
        routes.append(route_info)
    
    # 只打印关键信息
    print(f"主应用路由总数: {len(routes)}")
    
    # 检查是否有auto-download相关路由
    auto_download_routes = [r for r in routes if '/auto-download/' in r['path']]
    print(f"自动下载相关路由数量: {len(auto_download_routes)}")
    
    if auto_download_routes:
        print("\n自动下载路由详情:")
        for route in auto_download_routes:
            print(f"- {route['path']} [{', '.join(route['methods'])}]")
    else:
        print("❌ 未找到自动下载相关路由")
    
    # 检查API路由
    api_routes = [r for r in routes if r['path'].startswith('/api/')]
    print(f"\nAPI路由数量: {len(api_routes)}")
    
    if api_routes:
        api_prefixes = set()
        for route in api_routes:
            parts = route['path'].split('/')
            if len(parts) > 2:
                prefix = parts[2]
                api_prefixes.add(prefix)
        
        print(f"API前缀: {sorted(list(api_prefixes))}")
        
        if 'auto-download' in api_prefixes:
            print("✅ auto-download API前缀已注册")
        else:
            print("❌ auto-download API前缀未注册")
            
except Exception as e:
    print(f"❌ 主应用路由检查失败: {str(e)}")
    
print("\n=== 调试完成 ===") 