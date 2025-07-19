import requests
from lxml import etree
import re
from urllib.parse import urljoin

# 简单测试JAVDB数据提取
def test_javdb_extraction():
    host = "https://javdb.com"
    
    # 测试无码排行榜
    url = urljoin(host, "/rankings/movies?t=daily&v=uncensored&page=1")
    print(f"测试URL: {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        html = etree.HTML(response.content, parser=etree.HTMLParser(encoding='utf-8'))
        
        # 查找视频元素
        video_elements = html.xpath("//div[@class='item']")
        print(f"找到 {len(video_elements)} 个视频元素")
        
        if video_elements:
            element = video_elements[0]
            
            # 测试番号提取
            title_selectors = [
                ".//div[@class='video-title']/strong",
                ".//strong",
                ".//div[contains(@class, 'title')]//strong"
            ]
            
            num = None
            for selector in title_selectors:
                title_element = element.xpath(selector)
                if title_element and title_element[0].text:
                    num = title_element[0].text.strip()
                    print(f"提取到番号: {num} (选择器: {selector})")
                    break
            
            # 测试评分提取
            rating_selectors = [
                ".//div[@class='score']/span[@class='value']",
                ".//span[@class='score']", 
                ".//div[contains(@class, 'score')]//span",
                ".//span[contains(text(), '分')]"
            ]
            
            rating = None
            for selector in rating_selectors:
                rating_elements = element.xpath(selector)
                if rating_elements:
                    rating_text = rating_elements[0].text or ""
                    print(f"评分文本: '{rating_text}' (选择器: {selector})")
                    rating_match = re.search(r"(\d+\.\d+)", rating_text)
                    if rating_match:
                        rating = float(rating_match.group(1))
                        print(f"提取到评分: {rating}")
                        break
            
            # 测试评论数提取  
            comment_selectors = [
                ".//div[@class='score']/span[contains(text(), '人評價')]",
                ".//span[contains(text(), '評論')]",
                ".//div[@class='meta']",
                ".//a[contains(@href, '/reviews')]"
            ]
            
            comments = 0
            for selector in comment_selectors:
                comment_elements = element.xpath(selector)
                if comment_elements:
                    element_text = comment_elements[0].text or ""
                    print(f"评论文本: '{element_text}' (选择器: {selector})")
                    comment_match = re.search(r"由(\d+)人評價|(\d+)\s*評論", element_text)
                    if comment_match:
                        comments = int(comment_match.group(1) or comment_match.group(2))
                        print(f"提取到评论数: {comments}")
                        break
            
            print(f"最终结果 - 番号: {num}, 评分: {rating}, 评论: {comments}")
        
    except Exception as e:
        print(f"测试出错: {str(e)}")

if __name__ == "__main__":
    test_javdb_extraction()
