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
        else:
            # 确保URL是完整的绝对URL
            if not url.startswith('http'):
                url = urljoin(self.host, url)

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

        # 获取评论数
        comments_elements = html.xpath("//a[contains(@href,'/reviews?')]/text()")
        if comments_elements:
            comments_text = comments_elements[0]
            comments_match = re.search(r"(\d+)", comments_text)
            if comments_match:
                meta.comments_count = int(comments_match.group(1))

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

    def get_trending_videos(self, page: int = 1, time_range: str = "week"):
        """获取热门视频列表"""
        try:
            # 添加随机延迟，避免被识别为爬虫
            delay = randint(3, 8)
            logger.info(f"获取热门视频列表前等待 {delay} 秒...")
            time.sleep(delay)
            
            # 构造热门页面URL
            url = urljoin(self.host, f"/rankings/videos?t={time_range}&page={page}")
            logger.info(f"获取热门视频列表: {url}")
            
            # 构建请求头，模拟浏览器
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                "Referer": self.host
            }
            
            response = self.session.get(url, headers=headers)
            html = etree.HTML(response.content, parser=etree.HTMLParser(encoding='utf-8'))
            
            videos = []
            video_elements = html.xpath("//div[@class='item']")
            
            for element in video_elements:
                try:
                    # 获取番号
                    title_element = element.xpath(".//div[@class='video-title']/strong")
                    if not title_element:
                        continue
                    
                    num = title_element[0].text.strip()
                    
                    # 获取链接
                    link_element = element.xpath(".//a[@class='box']")
                    if not link_element:
                        continue
                    
                    video_url = urljoin(self.host, link_element[0].get('href'))
                    
                    # 获取封面
                    cover_element = element.xpath(".//img")
                    cover = cover_element[0].get('src') if cover_element else None
                    
                    # 获取评分
                    rating_element = element.xpath(".//span[@class='score']")
                    rating = None
                    if rating_element:
                        rating_text = rating_element[0].text
                        rating_match = re.search(r"(\d+\.\d+)", rating_text)
                        if rating_match:
                            rating = float(rating_match.group(1))
                    
                    video_info = {
                        'num': num,
                        'title': f"{num} {title_element[0].tail or ''}".strip(),
                        'url': video_url,
                        'cover': cover,
                        'rating': rating,
                        'website': self.name
                    }
                    
                    videos.append(video_info)
                    
                except Exception as e:
                    logger.warning(f"解析视频信息时出错: {str(e)}")
                    continue
            
            return videos
            
        except Exception as e:
            logger.error(f"获取热门视频列表时出错: {str(e)}")
            return []

    def get_latest_videos(self, page: int = 1, date_range: int = 7):
        """获取最新视频列表"""
        try:
            # 添加随机延迟，避免被识别为爬虫
            delay = randint(3, 8)
            logger.info(f"获取最新视频列表前等待 {delay} 秒...")
            time.sleep(delay)
            
            # 构造最新页面URL  
            url = urljoin(self.host, f"/videos?page={page}")
            logger.info(f"获取最新视频列表: {url}")
            
            # 构建请求头，模拟浏览器
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                "Referer": self.host
            }
            
            response = self.session.get(url, headers=headers)
            html = etree.HTML(response.content, parser=etree.HTMLParser(encoding='utf-8'))
            
            videos = []
            video_elements = html.xpath("//div[@class='item']")
            
            for element in video_elements:
                try:
                    # 获取番号
                    title_element = element.xpath(".//div[@class='video-title']/strong")
                    if not title_element:
                        continue
                    
                    num = title_element[0].text.strip()
                    
                    # 获取链接
                    link_element = element.xpath(".//a[@class='box']")
                    if not link_element:
                        continue
                    
                    video_url = urljoin(self.host, link_element[0].get('href'))
                    
                    # 获取发布日期
                    date_element = element.xpath(".//div[@class='meta']/text()")
                    publish_date = None
                    if date_element:
                        date_text = date_element[0].strip()
                        try:
                            publish_date = datetime.strptime(date_text, "%Y-%m-%d").date()
                        except:
                            pass
                    
                    # 检查是否在指定日期范围内
                    if publish_date and date_range > 0:
                        days_ago = (datetime.now().date() - publish_date).days
                        if days_ago > date_range:
                            continue
                    
                    # 获取封面
                    cover_element = element.xpath(".//img")
                    cover = cover_element[0].get('src') if cover_element else None
                    
                    video_info = {
                        'num': num,
                        'title': f"{num} {title_element[0].tail or ''}".strip(),
                        'url': video_url,
                        'cover': cover,
                        'publish_date': publish_date,
                        'website': self.name
                    }
                    
                    videos.append(video_info)
                    
                except Exception as e:
                    logger.warning(f"解析视频信息时出错: {str(e)}")
                    continue
            
            return videos
            
        except Exception as e:
            logger.error(f"获取最新视频列表时出错: {str(e)}")
            return []

    def get_comments_count(self, url: str):
        """获取视频评论数"""
        try:
            # 添加随机延迟，避免被识别为爬虫
            delay = randint(2, 5)
            logger.debug(f"获取评论数前等待 {delay} 秒...")
            time.sleep(delay)
            
            # 构建请求头，模拟浏览器
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                "Referer": self.host
            }
            
            response = self.session.get(url, headers=headers)
            html = etree.HTML(response.content, parser=etree.HTMLParser(encoding='utf-8'))
            
            comments_elements = html.xpath("//a[contains(@href,'/reviews?')]/text()")
            if comments_elements:
                comments_text = comments_elements[0]
                comments_match = re.search(r"(\d+)", comments_text)
                if comments_match:
                    return int(comments_match.group(1))
            
            return 0
            
        except Exception as e:
            logger.error(f"获取评论数时出错: {str(e)}")
            return 0

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

    def get_ranking_with_details(self, video_type: str, cycle: str, max_pages: int = 3):
        """获取排行榜数据，包含评分和评论信息，用于智能下载规则"""
        try:
            all_videos = []
            
            for page in range(1, max_pages + 1):
                # 构造排行榜URL
                url = urljoin(self.host, f'/rankings/movies?p={cycle}&t={video_type}&page={page}')
                logger.info(f"获取排行榜页面: {url}")
                
                # 添加随机延迟，避免被识别为爬虫
                delay = randint(3, 8)
                logger.info(f"等待 {delay} 秒...")
                time.sleep(delay)
                
                # 构建请求头，模拟浏览器
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                    "Cache-Control": "max-age=0",
                    "Connection": "keep-alive",
                    "Referer": self.host
                }
                
                response = self.session.get(url, headers=headers)
                html = etree.HTML(response.content, parser=etree.HTMLParser(encoding='utf-8'))
                
                # 解析排行榜页面中的视频信息
                videos = html.xpath('//div[contains(@class, "movie-list")]/div[@class="item"]/a')
                if not videos:
                    logger.warning(f"第 {page} 页没有找到视频数据")
                    break
                
                for video in videos:
                    try:
                        video_info = {}
                        
                        # 获取番号
                        num_element = video.xpath('./div[@class="video-title"]/strong')
                        if not num_element:
                            continue
                        video_info['num'] = num_element[0].text.strip()
                        
                        # 获取标题
                        video_info['title'] = video.get('title', '').strip()
                        
                        # 获取封面
                        cover_element = video.xpath('./div[contains(@class, "cover")]/img')
                        if cover_element:
                            video_info['cover'] = cover_element[0].get('src')
                        
                        # 获取URL
                        video_info['url'] = urljoin(self.host, video.get('href'))
                        
                        # 获取发布日期
                        date_element = video.xpath('./div[@class="meta"]')
                        if date_element:
                            try:
                                date_str = date_element[0].text.strip()
                                video_info['release_date'] = date_str
                                video_info['publish_date'] = datetime.strptime(date_str, "%Y-%m-%d").date()
                            except Exception as e:
                                logger.warning(f"解析日期失败: {str(e)}")
                        
                        # 获取评分和评论数 - 直接从排行榜页面获取
                        score_element = video.xpath('./div[@class="score"]/span/text()')
                        if score_element:
                            score_text = score_element[0].strip()
                            # 解析评分和评论数：例如 "8.5分, 由123人評價"
                            score_match = re.match(r'(.+?)分, 由(.+?)人評價', score_text)
                            if score_match:
                                video_info['rating'] = float(score_match.group(1))
                                video_info['comments'] = int(score_match.group(2))
                                logger.debug(f"解析到评分: {video_info['rating']}, 评论: {video_info['comments']}")
                        
                        # 获取标签信息 - 直接从排行榜页面获取
                        tag_elements = video.xpath('./div[contains(@class, "tags")]/span')
                        video_info['is_zh'] = False
                        video_info['is_hd'] = False
                        video_info['is_uncensored'] = False
                        
                        for tag in tag_elements:
                            tag_text = tag.text or ''
                            if '中字' in tag_text or '字幕' in tag_text:
                                video_info['is_zh'] = True
                            if '高清' in tag_text or 'HD' in tag_text:
                                video_info['is_hd'] = True
                            if '无码' in tag_text or '無碼' in tag_text or '破解' in tag_text:
                                video_info['is_uncensored'] = True
                        
                        # 根据video_type设置默认的无码状态
                        if video_type == 'uncensored':
                            video_info['is_uncensored'] = True
                        elif video_type == 'censored':
                            video_info['is_uncensored'] = False
                        
                        video_info['website'] = self.name
                        all_videos.append(video_info)
                        
                    except Exception as e:
                        logger.warning(f"解析视频信息时出错: {str(e)}")
                        continue
                
                logger.info(f"第 {page} 页解析完成，获取到 {len(videos)} 个视频")
            
            logger.info(f"总共获取到 {len(all_videos)} 个排行榜视频，包含评分和评论信息")
            return all_videos
            
        except Exception as e:
            logger.error(f"获取排行榜数据时出错: {str(e)}")
            return []

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
                    elif actors:
                        actor_match = actors[0]  # 如果没有过滤结果，使用第一个结果
                    else:
                        # 没有找到任何演员
                        logger.error(f"没有找到任何匹配的演员: {actor_url}")
                        return []
                
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
            
            # 使用lxml解析HTML，比正则表达式更可靠
            html = etree.HTML(response.content, parser=etree.HTMLParser(encoding='utf-8'))
            
            # 保存页面内容用于调试
            try:
                with open("javdb_actor_debug.html", "wb") as f:
                    f.write(response.content)
                logger.info("已保存演员详情页HTML文件")
            except:
                pass
            
            result = []
            
            # 获取所有视频条目
            movie_boxes = html.xpath('//a[@class="box"]')
            logger.info(f"找到 {len(movie_boxes)} 个视频条目")
            
            for box in movie_boxes:
                try:
                    item = JavDBRanking()
                    
                    # 提取视频URL
                    video_url = box.get('href')
                    if not video_url.startswith('http'):
                        video_url = urljoin(self.host, video_url)
                    item.url = video_url
                    
                    # 提取视频标题和番号
                    title_element = box.xpath('.//div[contains(@class, "video-title")]')
                    if title_element:
                        # 提取番号
                        num_element = title_element[0].xpath('./strong/text()')
                        if num_element:
                            item.num = num_element[0].strip()
                        
                        # 提取完整标题
                        full_title = title_element[0].xpath('string(.)')
                        if full_title:
                            item.title = full_title.strip()
                    
                    # 提取封面
                    cover_element = box.xpath('.//img[@loading="lazy"]')
                    if cover_element:
                        cover_url = cover_element[0].get('src')
                        if cover_url and not cover_url.startswith('http'):
                            cover_url = 'https:' + cover_url if cover_url.startswith('//') else urljoin(self.host, cover_url)
                        item.cover = cover_url
                    
                    # 提取评分
                    score_element = box.xpath('.//div[contains(@class, "score")]//span[@class="value"]/text()')
                    if score_element:
                        score_text = score_element[0]
                        score_match = re.search(r'(\d+\.\d+)分', score_text)
                        if score_match:
                            try:
                                item.rank = float(score_match.group(1))
                            except:
                                pass
                        
                        # 提取评论数
                        count_match = re.search(r'由(\d+)人評價', score_text)
                        if count_match:
                            try:
                                item.rank_count = int(count_match.group(1))
                                logger.info(f"解析到评论数: {item.rank_count}")
                            except Exception as e:
                                logger.error(f"评论数解析失败: {score_text}, 错误: {str(e)}")
                    
                    # 检查标签
                    cnsub_element = box.xpath('.//span[contains(@class, "cnsub")]')
                    item.isZh = len(cnsub_element) > 0
                    
                    uncensored_element = box.xpath('.//span[contains(@class, "uncensored")]')
                    item.is_uncensored = len(uncensored_element) > 0
                    
                    # 尝试获取发布日期
                    date_element = box.xpath('.//div[contains(@class, "meta")]/text()')
                    if date_element and len(date_element) > 0:
                        date_text = date_element[0].strip()
                        try:
                            # 尝试解析日期格式 YYYY-MM-DD
                            if re.match(r'\d{4}-\d{2}-\d{2}', date_text):
                                item.publish_date = datetime.strptime(date_text, "%Y-%m-%d").date()
                                logger.info(f"解析到日期: {item.publish_date} 从 {date_text}")
                        except Exception as e:
                            logger.error(f"日期解析失败: {date_text}, 错误: {str(e)}")
                    
                    # 如果没有找到番号，则跳过这个条目
                    if not item.num:
                        continue
                        
                    result.append(item)
                except Exception as e:
                    logger.error(f"处理视频条目时出错: {str(e)}")
            
            return result
            
        finally:
            # 恢复原始头信息
            self.session.headers = original_headers
