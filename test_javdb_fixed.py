#!/usr/bin/env python3
"""测试修复后的JAVDB数据提取功能"""

import sys
import os
import re
from lxml import etree

# 模拟从HTML文件提取数据来验证逻辑
def test_extraction_logic():
    print("=== 测试修复后的JAVDB数据提取逻辑 ===")
    
    # 测试数据 - 基于实际HTML结构
    test_html = '''
    <div class="movie-list h cols-4 vcols-8">
        <div class="item">
            <a href="/v/pkq1Dk" class="box" title="测试视频标题">
                <div class="cover">
                    <img loading="lazy" src="https://example.com/cover.jpg" />
                </div>
                <div class="video-title"><strong>SONE-785</strong> 新人スポーツキャスターは局から人気スポーツ選手にあてがわれても断れず…</div>
                <div class="score">
                    <span class="value">
                        <span class="score-stars"><i class="icon-star"></i><i class="icon-star"></i><i class="icon-star"></i><i class="icon-star"></i><i class="icon-star gray"></i></span>
                        &nbsp;
                        4.54分, 由346人評價
                    </span>
                </div>
                <div class="meta">2025-07-22</div>
            </a>
        </div>
    </div>
    '''
    
    html = etree.HTML(test_html)
    
    # 测试XPath选择器
    video_elements = html.xpath("//div[@class='movie-list']//div[@class='item']")
    print(f"找到视频元素数量: {len(video_elements)}")
    
    if video_elements:
        element = video_elements[0]
        
        # 测试番号提取
        title_element = element.xpath(".//div[@class='video-title']/strong")
        if title_element:
            num = title_element[0].text.strip()
            print(f"番号: {num}")
        
        # 测试链接提取
        link_element = element.xpath(".//a[@class='box']")
        if link_element:
            url = link_element[0].get('href')
            print(f"链接: {url}")
        
        # 测试标题提取
        title_div = element.xpath(".//div[@class='video-title']")
        if title_div:
            full_title = ''.join(title_div[0].itertext()).strip()
            print(f"完整标题: {full_title}")
        
        # 测试评分和评论数提取
        score_element = element.xpath(".//div[@class='score']/span[@class='value']")
        if score_element:
            score_text = ''.join(score_element[0].itertext()).strip()
            print(f"评分文本: '{score_text}'")
            
            # 提取评分
            rating_match = re.search(r"(\d+\.\d+)分", score_text)
            if rating_match:
                rating = float(rating_match.group(1))
                print(f"提取到评分: {rating}")
            
            # 提取评论数
            comment_match = re.search(r"由(\d+)人評價", score_text)
            if comment_match:
                comments = int(comment_match.group(1))
                print(f"提取到评论数: {comments}")
    
    print("\n=== 测试URL构建逻辑 ===")
    
    # 测试URL构建
    host = "https://javdb.com"
    cycle = "daily"
    page = 1
    
    # 有码排行榜URL
    censored_url = f"{host}/rankings/movies?p={cycle}&t=censored&page={page}"
    print(f"有码排行榜URL: {censored_url}")
    
    # 无码排行榜URL  
    uncensored_url = f"{host}/rankings/movies?p={cycle}&t=uncensored&page={page}"
    print(f"无码排行榜URL: {uncensored_url}")
    
    print("\n=== 测试完成 ===")
    print("修复要点:")
    print("1. URL格式修正为 /rankings/movies?p={cycle}&t={type}")
    print("2. XPath选择器修正为 //div[@class='movie-list']//div[@class='item']")
    print("3. 评分文本提取使用 itertext() 方法处理嵌套HTML")
    print("4. 统一的解析方法处理有码和无码排行榜")

if __name__ == "__main__":
    test_extraction_logic()