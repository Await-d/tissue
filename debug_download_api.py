#!/usr/bin/env python3
"""
调试下载API的脚本，用于检查API是否正常工作
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.service.download import DownloadService
from app.db import SessionFactory
from app.utils.qbittorent import qbittorent

async def debug_download_api():
    """调试下载API"""
    print("=== 调试下载API ===")
    
    try:
        # 测试qBittorrent连接
        print("1. 测试qBittorrent连接...")
        connection_result = qbittorent.test_connection()
        print(f"   连接状态: {connection_result['status']}")
        print(f"   信息: {connection_result['message']}")
        
        if not connection_result['status']:
            print("   ❌ qBittorrent连接失败，请检查配置")
            return
        
        # 测试获取所有种子
        print("\n2. 测试获取所有种子...")
        try:
            all_torrents = qbittorent.get_all_torrents()
            print(f"   获取到 {len(all_torrents)} 个种子")
            
            if all_torrents:
                print("   种子信息样本:")
                for i, torrent in enumerate(all_torrents[:3]):  # 只显示前3个
                    print(f"   [{i+1}] 名称: {torrent.get('name', 'N/A')[:50]}...")
                    print(f"       状态: {torrent.get('state', 'N/A')}")
                    print(f"       标签: {torrent.get('tags', 'N/A')}")
                    print(f"       分类: {torrent.get('category', 'N/A')}")
        except Exception as e:
            print(f"   ❌ 获取种子失败: {e}")
            return
        
        # 测试下载服务
        print("\n3. 测试下载服务...")
        with SessionFactory() as db:
            service = DownloadService(db=db)
            
            # 测试不同参数组合
            test_cases = [
                {"include_success": True, "include_failed": True, "name": "所有下载"},
                {"include_success": True, "include_failed": False, "name": "排除失败"},
                {"include_success": False, "include_failed": True, "name": "排除成功"},
            ]
            
            for case in test_cases:
                try:
                    downloads = service.get_downloads(
                        include_success=case["include_success"],
                        include_failed=case["include_failed"]
                    )
                    print(f"   {case['name']}: {len(downloads)} 个下载任务")
                    
                    # 显示一些详细信息
                    for i, download in enumerate(downloads[:2]):  # 只显示前2个
                        print(f"     [{i+1}] {download.name}")
                        print(f"         标签: {download.tags}")
                        print(f"         文件数: {len(download.files)}")
                        
                except Exception as e:
                    print(f"   ❌ {case['name']} 测试失败: {e}")
        
        print("\n=== 调试完成 ===")
        
    except Exception as e:
        print(f"❌ 调试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_download_api())