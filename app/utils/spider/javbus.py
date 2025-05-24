import random
import re
from datetime import datetime

from lxml import etree
from urllib.parse import urljoin

from app.schema import VideoDetail, VideoActor, VideoDownload, VideoPreviewItem, VideoPreview
from app.utils.spider.spider import Spider
from app.utils.spider.spider_exception import SpiderException


class JavbusSpider(Spider):
    host = "https://www.javbus.com/"
    name = 'JavBus'
    downloadable = True

    def get_info(self, num: str, url: str = None, include_downloads=False, include_previews=False):

        url = urljoin(self.host, num)
        response = self.session.get(url, allow_redirects=False)

        html = etree.HTML(response.text)

        meta = VideoDetail()
        meta.num = num

        title_element = html.xpath("//h3")
        if title_element:
            title = title_element[0].text
            meta.title = title
        else:
            raise SpiderException('未找到番号')

        premiered_element = html.xpath("//span[text()='發行日期:']")
        if premiered_element:
            meta.premiered = premiered_element[0].tail.strip()

        runtime_element = html.xpath("//span[text()='長度:']")
        if runtime_element:
            runtime = runtime_element[0].tail.strip()
            runtime = runtime.replace("分鐘", "")
            meta.runtime = runtime

        director_element = html.xpath("//span[text()='導演:']/../a")
        if director_element:
            director = director_element[0].text
            meta.director = director

        studio_element = html.xpath("//span[text()='製作商:']/../a")
        if studio_element:
            studio = studio_element[0].text
            meta.studio = studio

        publisher_element = html.xpath("//span[text()='發行商:']/../a")
        if publisher_element:
            publisher = publisher_element[0].text
            meta.publisher = publisher

        series_element = html.xpath("//span[text()='系列:']/../a")
        if series_element:
            series = series_element[0].text
            meta.series = series

        tag_elements = html.xpath("//span[@class='genre']//a[contains(@href,'genre')]")
        if tag_elements:
            tags = [tag.text for tag in tag_elements]
            meta.tags = tags

        actor_elements = html.xpath("//span[@class='genre']//a[contains(@href,'star')]")
        if actor_elements:
            actors = []
            for element in actor_elements:
                actor_url = element.get('href')
                actor_code = actor_url.split("/")[-1]
                actor_avatar = urljoin(self.host, f'/pics/actress/{actor_code}_a.jpg')
                actor = VideoActor(name=element.text, thumb=actor_avatar)
                actors.append(actor)
            meta.actors = actors

        cover_element = html.xpath("//a[@class='bigImage']")
        if cover_element:
            cover = cover_element[0].get("href")
            meta.cover = urljoin(self.host, cover)

        meta.website.append(url)

        if include_downloads:
            meta.downloads = self.get_downloads(url, response.text)

        if include_downloads:
            meta.previews = self.get_previews(html)

        return meta

    def get_previews(self, html: etree.HTML):
        result = []

        images = html.xpath("//a[@class='sample-box']")
        for image in images:
            thumb = image.xpath("./div/img")[0]
            preview = VideoPreviewItem(type='image', thumb=urljoin(self.host, thumb.get('src')), url=image.get('href'))
            result.append(preview)

        return [VideoPreview(website=self.name, items=result)]

    def get_downloads(self, url: str, response: str):
        params = {'lang': 'zh', 'floor': random.Random().randint(100, 1000)}

        gid = re.search(r'var gid = (\w+);', response)
        params['gid'] = gid.group(1)

        uc = re.search(r'var uc = (\w+);', response)
        params['uc'] = uc.group(1)

        img = re.search(r'var img = \'(.+)\';', response)
        params['img'] = img.group(1)

        response = self.session.get(urljoin(self.host, '/ajax/uncledatoolsbyajax.php'), params=params,
                                    allow_redirects=True, headers={'Referer': self.host})
        html = etree.HTML(f'<table>{response.text}</table>', parser=etree.HTMLParser(encoding='utf-8'))

        result = []
        table = html.xpath("//tr")
        for item in table:
            parts = item.xpath("./td[1]/a")
            if not parts:
                continue

            download = VideoDownload()
            download.website = self.name
            download.url = url
            download.name = parts[0].text.strip()
            download.magnet = parts[0].get('href')

            title = parts[0].text.strip()
            if '无码' in title or '破解' in title:
                download.is_uncensored = True

            for tag in parts[1:]:
                if tag.text == '高清':
                    download.is_hd = True
                if tag.text == '字幕':
                    download.is_zh = True

            size_element = item.xpath("./td[2]/a")[0]
            download.size = size_element.text.strip()

            publish_date_element = item.xpath("./td[3]/a")[0]
            download.publish_date = datetime.strptime(publish_date_element.text.strip(), "%Y-%m-%d").date()

            result.append(download)
        return result

    def get_actors(self):
        """获取JavBus网站上的热门演员列表"""
        import logging
        import re
        logger = logging.getLogger('spider')
        
        url = urljoin(self.host, '/actresses')
        
        # 使用更完整的浏览器请求头，避免被网站拦截
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Referer': self.host,
            'sec-ch-ua': '"Google Chrome";v="91", " Not;A Brand";v="99", "Chromium";v="91"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # 保存原始头信息用于后续恢复
        original_headers = self.session.headers.copy()
        
        # 临时替换会话头信息
        self.session.headers.update(headers)
        
        try:
            response = self.session.get(url)
            html_content = response.content
            logger.info(f"响应内容大小: {len(html_content)} 字节")
            
            # 保存页面内容用于调试
            try:
                with open("javbus_actresses_debug.html", "wb") as f:
                    f.write(html_content)
                logger.info("已保存actresses页面HTML文件")
            except Exception as e:
                logger.error(f"保存HTML文件失败: {str(e)}")
            
            html = etree.HTML(html_content, parser=etree.HTMLParser(encoding='utf-8'))
            
            result = []
            
            # 尝试多种方式获取演员列表
            # 1. 先尝试使用XPath选择器
            actresses = html.xpath('//a[@class="avatar-box text-center"]')
            logger.info(f"使用XPath找到演员元素: {len(actresses)}个")
            
            if not actresses:
                # 2. 尝试使用更宽松的选择器
                actresses = html.xpath('//a[contains(@class, "avatar-box")]')
                logger.info(f"使用宽松XPath找到演员元素: {len(actresses)}个")
            
            if not actresses:
                # 3. 尝试查找包含演员照片的元素
                actresses = html.xpath('//div[@id="waterfall"]/div/a') or html.xpath('//div[contains(@class, "item")]/a')
                logger.info(f"使用备用XPath找到演员元素: {len(actresses)}个")
            
            # 如果XPath都失败了，尝试正则表达式
            if not actresses:
                logger.info("XPath失败，尝试使用正则表达式匹配")
                avatar_box_pattern = r'<a[^>]*href="([^"]+)"[^>]*>.*?<img[^>]*src="([^"]+)"[^>]*title="([^"]+)".*?</a>'
                avatar_matches = re.findall(avatar_box_pattern, response.text, re.DOTALL)
                
                logger.info(f"正则表达式匹配到: {len(avatar_matches)}个演员")
                
                for match in avatar_matches:
                    try:
                        actress_url, actress_avatar, actress_name = match
                        
                        # 检查是否是演员页面的URL
                        if '/star/' not in actress_url and '/actresses/' not in actress_url:
                            continue
                        
                        logger.info(f"找到演员: {actress_name}, URL: {actress_url}")
                        
                        # JavBus的图片路径需要特殊处理
                        if actress_avatar.startswith('/'):
                            actress_avatar = urljoin(self.host, actress_avatar)
                        
                        actor_info = VideoActor(name=actress_name, thumb=actress_avatar)
                        result.append(actor_info)
                    except Exception as e:
                        logger.error(f"处理正则匹配时出错: {str(e)}")
                
                return result
            
            # 处理通过XPath找到的演员
            for actress in actresses:
                try:
                    actress_url = actress.get('href')
                    
                    # 尝试不同方式获取演员名称和头像
                    actress_name = None
                    actress_avatar = None
                    
                    # 尝试获取名称
                    name_elements = actress.xpath('./div/img/@title') or actress.xpath('.//img/@title')
                    if name_elements:
                        actress_name = name_elements[0]
                    else:
                        # 尝试其他方法
                        name_elements = actress.xpath('.//span/text()') or actress.xpath('.//text()')
                        if name_elements:
                            for text in name_elements:
                                if text.strip():
                                    actress_name = text.strip()
                                    break
                    
                    # 如果还没找到名称，使用URL的最后部分
                    if not actress_name and actress_url:
                        actress_name = actress_url.split('/')[-1]
                    
                    # 如果没有名称，跳过这个演员
                    if not actress_name:
                        continue
                    
                    # 尝试获取头像
                    avatar_elements = actress.xpath('./div/img/@src') or actress.xpath('.//img/@src')
                    if avatar_elements:
                        actress_avatar = avatar_elements[0]
                        if actress_avatar.startswith('/'):
                            actress_avatar = urljoin(self.host, actress_avatar)
                    else:
                        # 如果找不到图像元素，尝试构造一个URL
                        if '/star/' in actress_url:
                            star_id = actress_url.split('/')[-1]
                            actress_avatar = urljoin(self.host, f'/pics/actress/{star_id}_a.jpg')
                    
                    logger.info(f"找到演员: {actress_name}, URL: {actress_url}, 头像: {actress_avatar}")
                    
                    if actress_name and actress_avatar:
                        actor_info = VideoActor(name=actress_name, thumb=actress_avatar)
                        result.append(actor_info)
                    elif actress_name:
                        # 如果只有名称没有头像，也创建演员，使用一个占位图像
                        logger.warning(f"演员 {actress_name} 没有头像")
                        actor_info = VideoActor(name=actress_name, thumb="")
                        result.append(actor_info)
                        
                except Exception as e:
                    logger.error(f"处理演员元素时出错: {str(e)}")
                    continue
            
            logger.info(f"总共找到 {len(result)} 个演员")
            return result
            
        finally:
            # 恢复原始头信息
            self.session.headers = original_headers

    def search_actor(self, actor_name: str):
        """搜索JavBus网站上的演员"""
        import logging
        import re
        logger = logging.getLogger('spider')
        
        url = urljoin(self.host, f'/searchstar/{actor_name}')
        logger.info(f"搜索演员URL: {url}")
        
        # 使用更完整的浏览器请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Referer': self.host,
            'sec-ch-ua': '"Google Chrome";v="91", " Not;A Brand";v="99", "Chromium";v="91"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # 保存原始头信息用于后续恢复
        original_headers = self.session.headers.copy()
        
        # 临时替换会话头信息
        self.session.headers.update(headers)
        
        try:
            response = self.session.get(url)
            html_content = response.text
            logger.info(f"响应内容大小: {len(html_content)} 字节")
            
            # 保存页面内容用于调试
            try:
                with open("javbus_debug.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                logger.info("已保存调试HTML文件")
            except:
                pass
            
            # 使用正则表达式查找演员信息，更宽松的匹配
            result = []
            
            # 1. 搜索avatar-box包含的演员信息
            avatar_box_pattern = r'<a[^>]*class="avatar-box[^"]*"[^>]*href="([^"]+)"[^>]*>.*?<img src="([^"]+)"[^>]*title="([^"]+)"'
            avatar_matches = re.findall(avatar_box_pattern, html_content, re.DOTALL)
            
            logger.info(f"avatar-box匹配: {len(avatar_matches)} 个")
            
            for match in avatar_matches:
                try:
                    actress_url, actress_avatar, actress_name = match
                    logger.info(f"找到演员: {actress_name}, URL: {actress_url}")
                    
                    # JavBus的图片路径需要特殊处理
                    if actress_avatar and actress_avatar.startswith('/'):
                        actress_avatar = urljoin(self.host, actress_avatar)
                    
                    actor_info = VideoActor(name=actress_name, thumb=actress_avatar)
                    result.append(actor_info)
                except Exception as e:
                    logger.error(f"处理匹配时出错: {e}")
            
            # 2. 如果没有找到，搜索演员名称并构造URL
            if not result:
                actress_pattern = r'<div class="photo-info">\s*<span[^>]*>([^<]+)<'
                actress_matches = re.findall(actress_pattern, html_content)
                
                logger.info(f"演员名称匹配: {len(actress_matches)} 个")
                
                for actress_name in actress_matches:
                    if actor_name.lower() in actress_name.lower() or actress_name.lower() in actor_name.lower():
                        logger.info(f"找到演员名称: {actress_name}")
                        
                        # 查找对应的star ID
                        star_pattern = r'href="[^"]*?/star/([^"]+)"[^>]*>' + re.escape(actress_name)
                        star_matches = re.findall(star_pattern, html_content)
                        
                        if star_matches:
                            star_id = star_matches[0]
                            logger.info(f"找到演员ID: {star_id}")
                            
                            # 构造头像URL
                            actress_avatar = urljoin(self.host, f'/pics/actress/{star_id}_a.jpg')
                            
                            actor_info = VideoActor(name=actress_name, thumb=actress_avatar)
                            result.append(actor_info)
                            break
            
            # 3. 如果还没找到，搜索带有演员名称的图片
            if not result:
                img_pattern = r'<img[^>]*title="' + re.escape(actor_name) + r'"[^>]*src="([^"]+)"'
                img_matches = re.findall(img_pattern, html_content)
                
                logger.info(f"图片匹配: {len(img_matches)} 个")
                
                if img_matches:
                    actress_avatar = img_matches[0]
                    if actress_avatar.startswith('/'):
                        actress_avatar = urljoin(self.host, actress_avatar)
                    
                    actor_info = VideoActor(name=actor_name, thumb=actress_avatar)
                    result.append(actor_info)
            
            return result
            
        finally:
            # 恢复原始头信息
            self.session.headers = original_headers

    def get_actor_videos(self, actor_name):
        """获取演员的所有视频"""
        logger.info(f"获取演员 {actor_name} 的视频列表")
        try:
            search_response = self.session.get(f"{self.host}/searchstar/{actor_name}")
            search_html = etree.HTML(search_response.text)
            actor_box = search_html.xpath('//a[@class="avatar-box text-center"]')
            
            if not actor_box:
                logger.warning(f"未找到演员：{actor_name}")
                return []
            
            # 找到匹配的演员
            actor_url = None
            for actor in actor_box:
                name = actor.xpath('.//span/text()')[0].strip()
                if name == actor_name:
                    actor_url = actor.get('href')
                    break
            
            if not actor_url:
                logger.warning(f"未找到完全匹配的演员：{actor_name}")
                # 尝试使用第一个结果
                if actor_box:
                    actor_url = actor_box[0].get('href')
            
            if not actor_url.startswith('http'):
                actor_url = self.host + actor_url
            
            # 获取演员详情页
            actor_response = self.session.get(actor_url)
            actor_html = etree.HTML(actor_response.text)
            
            videos = []
            boxes = actor_html.xpath('//a[@class="movie-box"]')
            
            for box in boxes:
                try:
                    item = WebVideo()
                    
                    # 获取URL
                    item.url = box.get('href')
                    
                    # 获取标题和番号
                    title_element = box.xpath('.//span[@class="title"]/text()')
                    if title_element:
                        item.title = title_element[0].strip()
                    
                    num_element = box.xpath('.//date[1]/text()')
                    if num_element:
                        item.num = num_element[0].strip()
                    
                    # 获取封面
                    cover_element = box.xpath('.//img/@src')
                    if cover_element:
                        item.cover = cover_element[0]
                    
                    # 检查特征
                    is_zh = box.xpath('.//button[@class="btn btn-primary btn-xs"]')
                    item.isZh = len(is_zh) > 0
                    
                    is_uncensored = box.xpath('.//button[@class="btn btn-danger btn-xs"]')
                    item.is_uncensored = len(is_uncensored) > 0
                    
                    # 尝试获取发布日期 - 修复JavBus特有的日期格式
                    # JavBus网站中日期在第二个<date>标签中
                    date_elements = box.xpath('.//date/text()')
                    if date_elements and len(date_elements) >= 2:
                        date_text = date_elements[1].strip()  # 第二个date元素包含日期
                        try:
                            # 尝试解析日期格式 YYYY-MM-DD
                            if re.match(r'\d{4}-\d{2}-\d{2}', date_text):
                                item.publish_date = datetime.strptime(date_text, "%Y-%m-%d").date()
                                logger.info(f"解析到日期: {item.publish_date} 从 {date_text}")
                            # 尝试解析其他可能的日期格式，如YYYY/MM/DD
                            elif re.match(r'\d{4}/\d{2}/\d{2}', date_text):
                                item.publish_date = datetime.strptime(date_text, "%Y/%m/%d").date()
                                logger.info(f"解析到日期: {item.publish_date} 从 {date_text}")
                        except Exception as e:
                            logger.warning(f"日期解析失败 {date_text}: {str(e)}")
                    
                    # 添加获取磁力链接
                    try:
                        # 打开详情页面获取磁力链接
                        video_response = self.session.get(item.url)
                        video_html = etree.HTML(video_response.text)
                        
                        # 获取第一个磁力链接
                        magnet_element = video_html.xpath("//table[@id='magnet-table']//a[contains(@href, 'magnet:?')]/@href")
                        if magnet_element and len(magnet_element) > 0:
                            item.magnet = magnet_element[0]
                            
                            # 检查是否高清
                            magnet_title = video_html.xpath("//table[@id='magnet-table']//tr[1]/td[1]/a/text()")
                            if magnet_title and '1080' in magnet_title[0]:
                                item.is_hd = True
                    except Exception as e:
                        logger.warning(f"获取磁力链接失败: {str(e)}")
                    
                    videos.append(item)
                    
                except Exception as e:
                    logger.error(f"解析视频元素失败: {str(e)}")
            
            return videos
            
        except Exception as e:
            logger.error(f"获取演员视频列表失败: {str(e)}")
            return []
