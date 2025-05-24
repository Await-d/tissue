import re
import time
import logging
from datetime import datetime
from random import randint
from urllib.parse import urljoin
from lxml import etree
from app.schema import VideoDetail, VideoActor, VideoDownload, VideoPreviewItem, VideoPreview
from app.schema.home import JavDBRanking
from app.utils.spider.spider import Spider
from app.utils.spider.spider_exception import SpiderException

# 获取logger
logger = logging.getLogger('spider')

class JavdbSpider(Spider):
    host = "https://javdb.com"
    name = 'JavDB'
    downloadable = True
    avatar_host = 'https://c0.jdbstatic.com/avatars/'

    def get_info(self, num: str, url: str = None, include_downloads=False, include_previews=False):

        searched = False

        if url is None:
            url = self.search(num)
            searched = True

        if not url:
            raise SpiderException('未找到番号')
        else:
            if searched:
                time.sleep(randint(1, 3))

        meta = VideoDetail()
        meta.num = num

        response = self.session.get(url)
        html = etree.HTML(response.content, parser=etree.HTMLParser(encoding='utf-8'))

        title_element = html.xpath("//strong[@class='current-title']")
        if title_element:
            title = title_element[0].text.strip()
            meta.title = f'{num.upper()} {title}'

        premiered_element = html.xpath("//strong[text()='日期:']/../span")
        if premiered_element:
            meta.premiered = premiered_element[0].text

        runtime_element = html.xpath("//strong[text()='時長:']/../span")
        if runtime_element:
            runtime = runtime_element[0].text
            runtime = runtime.replace(" 分鍾", "")
            meta.runtime = runtime

        director_element = html.xpath("//strong[text()='導演:']/../span/a")
        if director_element:
            director = director_element[0].text
            meta.director = director

        studio_element = html.xpath("//strong[text()='片商:']/../span/a")
        if studio_element:
            studio = studio_element[0].text
            meta.studio = studio

        publisher_element = html.xpath("//strong[text()='發行:']/../span/a")
        if publisher_element:
            publisher = publisher_element[0].text
            meta.publisher = publisher

        series_element = html.xpath("//strong[text()='系列:']/../span/a")
        if series_element:
            series = series_element[0].text
            meta.series = series

        tag_elements = html.xpath("//a[contains(@href,'/tags?')]")
        if tag_elements:
            tags = [tag.text for tag in tag_elements]
            meta.tags = tags

        actor_elements = html.xpath("//strong[@class='symbol female']")
        if actor_elements:
            actors = []
            for element in actor_elements:
                actor_element = element.xpath('./preceding-sibling::a[1]')[0]
                actor_url = actor_element.get('href')
                actor_code = actor_url.split("/")[-1]
                actor_avatar = urljoin(self.avatar_host, f'{actor_code[0:2].lower()}/{actor_code}.jpg')
                actor = VideoActor(name=actor_element.text, thumb=actor_avatar)
                actors.append(actor)
            meta.actors = actors

        cover_element = html.xpath("//img[@class='video-cover']")
        if cover_element:
            meta.cover = cover_element[0].get("src")

        score_elements = html.xpath("//span[@class='score-stars']/../text()")
        if score_elements:
            score_text = str(score_elements[0])
            pattern_result = re.search(r"(\d+\.\d+)分", score_text)
            score = pattern_result.group(1)
            meta.rating = score

        meta.website.append(url)

        if include_downloads:
            meta.downloads = self.get_downloads(url, html)

        if include_previews:
            meta.previews = self.get_previews(html)

        return meta

    def search(self, num: str):
        url = urljoin(self.host, f"/search?q={num}&f=all")
        response = self.session.get(url)

        html = etree.HTML(response.content)
        matched_elements = html.xpath(fr"//div[@class='video-title']/strong")
        for matched_element in matched_elements:
            if matched_element.text.lower() == num.lower():
                code = matched_element.xpath('./../..')[0].get('href')
                return urljoin(self.host, code)

    def get_previews(self, html: etree.HTML):
        result = []

        videos = html.xpath("//div[contains(@class,'preview-images')]/a[@class='preview-video-container']")
        for video in videos:
            thumb = video.xpath('./img')[0]
            video = html.xpath(f"//video[@id='{video.get('href')[1:]}']/source")[0]
            preview = VideoPreviewItem(type='video', thumb=thumb.get('src'), url=video.get('src'))
            result.append(preview)

        images = html.xpath("//div[contains(@class,'preview-images')]/a[@class='tile-item']")
        for image in images:
            thumb = image.xpath('./img')[0]
            preview = VideoPreviewItem(type='image', thumb=thumb.get('src'), url=image.get('href'))
            result.append(preview)

        return [VideoPreview(website=self.name, items=result)]

    def get_downloads(self, url: str, html: etree.HTML):
        result = []
        table = html.xpath("//div[@id='magnets-content']/div")
        for item in table:
            download = VideoDownload()

            parts = item.xpath("./div[1]/a")[0]
            download.website = self.name
            download.url = url
            download.name = parts[0].text.strip()
            download.magnet = parts.get('href')

            name = parts.xpath("./span[1]")
            if name:
                if '无码' in name[0].text or '破解' in name[0].text:
                    download.is_uncensored = True

            size = parts.xpath("./span[2]")
            if size:
                download.size = size[0].text.split(',')[0].strip()

            for tag in parts.xpath('./div[@class="tags"]/span'):
                if tag.text == '高清':
                    download.is_hd = True
                if tag.text == '字幕':
                    download.is_zh = True

            publish_date = item.xpath(".//span[@class='time']")
            if publish_date:
                download.publish_date = datetime.strptime(publish_date[0].text.strip(), "%Y-%m-%d").date()

            result.append(download)
        return result

    def get_ranking(self, video_type: str, cycle: str):
        url = urljoin(self.host, f'/rankings/movies?p={cycle}&t={video_type}')
        response = self.session.get(url)
        html = etree.HTML(response.content, parser=etree.HTMLParser(encoding='utf-8'))

        result = []

        videos = html.xpath('//div[contains(@class, "movie-list")]/div[@class="item"]/a')
        for video in videos:
            ranking = JavDBRanking()
            ranking.cover = video.xpath('./div[contains(@class, "cover")]/img')[0].get('src')
            ranking.title = video.get('title')
            ranking.num = video.xpath('./div[@class="video-title"]/strong')[0].text
            ranking.publish_date = datetime.strptime(video.xpath('./div[@class="meta"]')[0].text.strip(),
                                                     "%Y-%m-%d").date()

            rank_str = video.xpath('./div[@class="score"]/span/text()')[0].strip()
            rank_matched = re.match('(.+?)分, 由(.+?)人評價', rank_str)
            ranking.rank = float(rank_matched.group(1))
            ranking.rank_count = int(rank_matched.group(2))

            ranking.url = urljoin(self.host, video.get('href'))

            tag_str = video.xpath('./div[contains(@class, "tags")]/span/text()')[0]
            ranking.isZh = ('中字' in tag_str)

            result.append(ranking)
        return result

    def get_actors(self):
        """获取JavDB网站上的热门演员列表"""
        url = urljoin(self.host, '/actors')
        response = self.session.get(url)
        html_content = response.content
        
        # 保存HTML用于调试
        try:
            with open("javdb_actors_debug.html", "wb") as f:
                f.write(html_content)
            logger.info(f"已保存演员列表页面到javdb_actors_debug.html，页面大小: {len(html_content)}字节")
        except Exception as e:
            logger.error(f"保存调试HTML失败: {str(e)}")
        
        html = etree.HTML(html_content, parser=etree.HTMLParser(encoding='utf-8'))
        
        # 记录XPath查询结果
        actors_list = html.xpath('//div[contains(@class, "actors-list")]')
        logger.info(f"找到actors-list元素: {len(actors_list)}个")
        
        if not actors_list:
            # 网站可能需要登录，或者页面结构变化
            logger.warning("未找到actors-list元素，尝试查找其他可能的演员元素")
            
            # 尝试其他可能的XPath
            alt_actors = html.xpath('//div[contains(@class, "actor-box")]') or html.xpath('//a[contains(@href, "/actors/")]')
            logger.info(f"尝试替代方式找到演员元素: {len(alt_actors)}个")
            
            # 如果没有找到任何元素，可能是网站需要登录
            if not alt_actors:
                logger.error("无法找到任何演员元素，可能需要登录或网站结构已更改")
                
                # 记录一些页面基本信息以帮助调试
                title = html.xpath('//title/text()')
                logger.info(f"页面标题: {title}")
                
                # 检查是否有登录表单
                login_form = html.xpath('//form[contains(@action, "login") or contains(@action, "sign_in")]')
                if login_form:
                    logger.error("检测到登录表单，网站可能需要登录才能访问演员列表")
                
                return []
        
        result = []
        # 先尝试标准路径
        actors = html.xpath('//div[contains(@class, "actors-list")]/div/a')
        
        if not actors:
            # 尝试其他可能的路径
            actors = html.xpath('//a[contains(@href, "/actors/")]')
            logger.info(f"使用替代XPath找到演员: {len(actors)}个")
        
        logger.info(f"找到演员元素: {len(actors)}个")
        
        for actor in actors:
            try:
                actor_url = actor.get('href')
                if not actor_url or 'actors' not in actor_url:
                    continue
                
                actor_code = actor_url.split("/")[-1]
                
                # 尝试不同方式查找演员名称
                name_el = actor.xpath('./div[@class="name"]')
                if name_el:
                    actor_name = name_el[0].text.strip()
                else:
                    # 尝试其他可能的方式获取名称
                    name_el = actor.xpath('.//text()')
                    if name_el and name_el[0].strip():
                        actor_name = name_el[0].strip()
                    else:
                        # 尝试从title属性获取
                        actor_name = actor.get('title')
                        if not actor_name:
                            continue
                
                logger.info(f"找到演员: {actor_name}, URL: {actor_url}")
                
                actor_avatar = urljoin(self.avatar_host, f'{actor_code[0:2].lower()}/{actor_code}.jpg')
                
                actor_info = VideoActor(name=actor_name, thumb=actor_avatar)
                result.append(actor_info)
            except Exception as e:
                logger.error(f"处理演员元素时出错: {str(e)}")
                continue
        
        logger.info(f"总共找到 {len(result)} 个演员")
        return result

    def search_actor(self, actor_name: str):
        """搜索JavDB网站上的演员"""
        url = urljoin(self.host, f'/search?q={actor_name}&f=actor')
        response = self.session.get(url)
        html = etree.HTML(response.content, parser=etree.HTMLParser(encoding='utf-8'))
        
        result = []
        
        # 尝试不同的XPath表达式找到演员列表
        actors = html.xpath('//a[contains(@href, "/actors/")]')
        
        for actor in actors:
            try:
                actor_url = actor.get('href')
                if not actor_url or 'actors' not in actor_url:
                    continue
                    
                actor_code = actor_url.split("/")[-1]
                
                # 查找演员名称
                name = None
                name_el = actor.xpath('./strong') or actor.xpath('.//strong')
                if name_el:
                    name = name_el[0].text.strip()
                else:
                    # 如果找不到标签，尝试使用元素自身的文本
                    name = actor.text.strip() if actor.text else None
                
                if not name:
                    # 如果还找不到名称，可能演员名称在title属性中
                    name = actor.get('title')
                    if name:
                        # 如果title包含多个名称（逗号分隔），取第一个
                        name = name.split(',')[0].strip()
                
                if not name:
                    continue
                
                # 构造头像URL
                actor_avatar = urljoin(self.avatar_host, f'{actor_code[0:2].lower()}/{actor_code}.jpg')
                
                actor_info = VideoActor(name=name, thumb=actor_avatar)
                result.append(actor_info)
            except Exception as e:
                continue
            
        return result
        
    def get_actor_videos(self, actor_url: str):
        """获取演员的所有视频"""
        import logging
        import re
        logger = logging.getLogger('spider')
        
        # 处理不同格式的actor_url输入
        if not actor_url.startswith(self.host):
            if not actor_url.startswith('http'):
                # 如果提供的是演员名称而不是URL
                actors = self.search_actor(actor_url)
                if not actors:
                    logger.info(f"未找到演员: {actor_url}")
                    return []
                    
                # 找到最匹配的演员
                actor_match = None
                for actor in actors:
                    if actor.name.lower() == actor_url.lower() or actor_url.lower() in actor.name.lower():
                        actor_match = actor
                        break
                
                if not actor_match:
                    # 排除掉有碼、無碼、歐美等类别标签
                    filtered_actors = [a for a in actors if a.name not in ['有碼', '無碼', '歐美']]
                    if filtered_actors:
                        actor_match = filtered_actors[0]  # 使用第一个结果
                    else:
                        actor_match = actors[3]  # 跳过前三个类别选项
                
                logger.info(f"选择演员: {actor_match.name}")
                
                # 从thumb中提取actor_id
                thumb_url = actor_match.thumb
                actor_code = thumb_url.split('/')[-1].split('.')[0]
                actor_url = urljoin(self.host, f'/actors/{actor_code}')
            elif '/actors/' not in actor_url:
                # 如果是其他网站的URL，无法处理
                return []
            else:
                # 包含/actors/但不是完整URL
                actor_url = urljoin(self.host, actor_url)
        
        logger.info(f"访问演员详情页: {actor_url}")
        
        # 使用更完整的浏览器请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Referer': self.host,
        }
        
        # 保存原始头信息用于后续恢复
        original_headers = self.session.headers.copy()
        
        # 临时替换会话头信息
        self.session.headers.update(headers)
        
        try:
            # 访问演员详情页
            response = self.session.get(actor_url)
            html_content = response.text
            
            # 保存页面内容用于调试
            try:
                with open("javdb_actor_debug.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                logger.info("已保存演员详情页HTML文件")
            except:
                pass
            
            result = []
            
            # 直接寻找视频标题元素和番号
            title_pattern = r'<div class="video-title"><strong>([^<]+)</strong>([^<]*)</div>'
            title_matches = re.findall(title_pattern, html_content)
            
            logger.info(f"找到 {len(title_matches)} 个视频标题")
            
            for idx, (num, title) in enumerate(title_matches):
                try:
                    item = JavDBRanking()
                    
                    # 清理和格式化标题文本
                    clean_title = re.sub(r'\s+', ' ', title).strip()
                    
                    # 提取番号和标题
                    item.num = num
                    item.title = (num + " " + clean_title).strip()
                    
                    # 尝试匹配这个番号对应的URL和封面
                    url_pattern = rf'<a href="([^"]+)"[^>]*>.*?<div class="video-title"><strong>{re.escape(num)}</strong>'
                    url_match = re.search(url_pattern, html_content, re.DOTALL)
                    
                    if url_match:
                        video_url = url_match.group(1)
                        if not video_url.startswith('http'):
                            video_url = urljoin(self.host, video_url)
                        item.url = video_url
                        
                        # 尝试匹配封面
                        cover_pattern = rf'<a href="{re.escape(video_url)}"[^>]*>.*?<img[^>]*src="([^"]+)"'
                        cover_match = re.search(cover_pattern, html_content, re.DOTALL)
                        if cover_match:
                            cover_url = cover_match.group(1)
                            # 确保封面URL是完整的URL
                            if not cover_url.startswith('http'):
                                item.cover = urljoin(self.host, cover_url)
                            else:
                                item.cover = cover_url
                    
                    # 提取评分
                    score_pattern = r'<div class="video-title"><strong>' + re.escape(num) + r'</strong>.*?<div class="score">.*?<span class="value">.*?([0-9.]+)分'
                    score_match = re.search(score_pattern, html_content, re.DOTALL)
                    if score_match:
                        try:
                            item.rank = float(score_match.group(1))
                        except:
                            pass
                    
                    # 查找番号相关的所有标签
                    card_html = ""
                    card_pattern = r'<a href="[^"]*' + re.escape(num) + r'[^"]*".*?</a>'
                    card_match = re.search(card_pattern, html_content, re.DOTALL)
                    if card_match:
                        card_html = card_match.group(0)
                        
                        # 检查标签
                        item.isZh = '中字' in card_html
                        item.is_uncensored = '無碼' in card_html or '无码' in card_html
                    
                    result.append(item)
                except Exception as e:
                    logger.error(f"处理视频时出错: {e}")
            
            return result
            
        finally:
            # 恢复原始头信息
            self.session.headers = original_headers
