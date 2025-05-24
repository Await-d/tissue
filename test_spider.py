#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app.utils.spider.javbus import JavbusSpider
from app.utils.spider.javdb import JavdbSpider
import traceback
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO)

def dump_page_source(url, filename):
    """获取页面源码并保存到文件"""
    import requests
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        }
        
        # 尝试直接获取页面内容
        print(f"获取页面: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"页面源码已保存到: {filename}")
            print(f"页面内容长度: {len(response.text)} 字节")
            print(f"页面内容前50个字符: {response.text[:50]}")
            
            # 分析
            if "请验证" in response.text or "验证码" in response.text:
                print("警告: 页面可能包含验证码或需要登录")
        else:
            print(f"获取页面失败: {response.status_code}")
    except Exception as e:
        print(f"获取页面时出错: {e}")

def test_javbus():
    print("===== 测试 JavBus 爬虫 =====")
    spider = JavbusSpider()
    
    # 首先直接获取页面源码
    print("\n直接获取页面源码...")
    javbus_url = "https://www.javbus.com/searchstar/新ありな"
    dump_page_source(javbus_url, "javbus_page.html")
    
    try:
        print("\n1. 测试搜索演员: 新ありな")
        actors = spider.search_actor("新ありな")
        print(f"找到 {len(actors)} 名演员:")
        for i, actor in enumerate(actors, 1):
            print(f"  {i}. 名称: {actor.name}, 头像: {actor.thumb}")
        
        if actors:
            print("\n2. 测试获取演员视频")
            videos = spider.get_actor_videos(actors[0].name)
            print(f"找到 {len(videos)} 个视频:")
            for i, video in enumerate(videos[:5], 1):  # 只显示前5个
                print(f"  {i}. 番号: {video.num}, 标题: {video.title}")
            if len(videos) > 5:
                print(f"  ... 以及更多 {len(videos) - 5} 个视频")
    except Exception as e:
        print(f"JavBus测试出错: {e}")
        traceback.print_exc()

def test_javdb():
    print("\n===== 测试 JavDB 爬虫 =====")
    spider = JavdbSpider()
    
    # 首先直接获取页面源码
    print("\n直接获取页面源码...")
    javdb_url = "https://javdb.com/search?q=新ありな&f=actor"
    dump_page_source(javdb_url, "javdb_page.html")
    
    try:
        print("\n1. 测试搜索演员: 新ありな")
        actors = spider.search_actor("新ありな")
        print(f"找到 {len(actors)} 名演员:")
        for i, actor in enumerate(actors, 1):
            print(f"  {i}. 名称: {actor.name}, 头像: {actor.thumb}")
        
        # 单独测试获取特定演员视频
        print("\n2. 测试获取特定演员视频: 新有菜")
        specific_actor = "新有菜"  # 测试用特定演员名
        videos = spider.get_actor_videos(specific_actor)
        print(f"找到 {len(videos)} 个视频:")
        for i, video in enumerate(videos[:5], 1):  # 只显示前5个
            print(f"  {i}. 番号: {video.num}, 标题: {video.title}")
        if len(videos) > 5:
            print(f"  ... 以及更多 {len(videos) - 5} 个视频")
            
    except Exception as e:
        print(f"JavDB测试出错: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_javbus()
    test_javdb() 