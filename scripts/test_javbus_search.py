#!/usr/bin/env python3
"""测试 JavBus 和 JavDB 的搜索功能"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.spider.javbus import JavbusSpider
from app.utils.spider.javdb import JavdbSpider
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_javbus(num):
    """测试 JavBus"""
    print(f"\n{'='*60}")
    print(f"测试 JavBus - 番号: {num}")
    print(f"{'='*60}")
    
    try:
        spider = JavbusSpider()
        # 直接访问 URL
        url = f"https://www.javbus.com/{num}"
        print(f"访问 URL: {url}")
        
        response = spider.session.get(url, allow_redirects=True, timeout=10)
        print(f"响应状态码: {response.status_code}")
        print(f"最终 URL: {response.url}")
        print(f"响应内容长度: {len(response.text)} 字符")
        
        # 保存 HTML 用于调试
        debug_file = f"javbus_{num}_debug.html"
        with open(debug_file, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"已保存响应到: {debug_file}")
        
        # 检查关键元素
        from lxml import etree
        html = etree.HTML(response.text)
        
        h3_elements = html.xpath("//h3")
        print(f"找到 h3 元素: {len(h3_elements)} 个")
        if h3_elements:
            for i, elem in enumerate(h3_elements[:3]):
                print(f"  h3[{i}]: {elem.text}")
        
        # 检查是否是 404 页面
        page_title = html.xpath("//title/text()")
        if page_title:
            print(f"页面标题: {page_title[0]}")
            
        # 检查是否有番号信息
        big_header = html.xpath("//div[@class='container']//h3/text()")
        if big_header:
            print(f"大标题: {big_header[0]}")
            
    except Exception as e:
        print(f"❌ JavBus 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_javdb(num):
    """测试 JavDB"""
    print(f"\n{'='*60}")
    print(f"测试 JavDB - 番号: {num}")
    print(f"{'='*60}")
    
    try:
        spider = JavdbSpider()
        
        # 测试搜索
        print(f"搜索番号: {num}")
        result_url = spider.search(num)
        
        if result_url:
            print(f"✅ 找到结果: {result_url}")
        else:
            print(f"❌ 未找到结果")
            
            # 保存搜索页面用于调试
            search_url = f"https://javdb.com/search?q={num}&f=all"
            response = spider._get(search_url)
            debug_file = f"javdb_search_{num}_debug.html"
            with open(debug_file, "wb") as f:
                f.write(response.content)
            print(f"已保存搜索页面到: {debug_file}")
            
            # 分析搜索结果
            from lxml import etree
            html = etree.HTML(response.content)
            video_titles = html.xpath("//div[@class='video-title']/strong/text()")
            print(f"搜索页面找到 {len(video_titles)} 个视频标题:")
            for i, title in enumerate(video_titles[:5]):
                print(f"  {i+1}. {title}")
            
    except Exception as e:
        print(f"❌ JavDB 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_nums = ["811", "ipx-811", "IPX-811"]
    
    for num in test_nums:
        test_javbus(num)
        test_javdb(num)
    
    print(f"\n{'='*60}")
    print("测试完成！")
    print(f"{'='*60}")
