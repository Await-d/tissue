import random
import re
import logging
from datetime import datetime

from lxml import etree
from urllib.parse import urljoin, urlparse

from app.schema import VideoDetail, VideoActor, VideoDownload, VideoPreviewItem, VideoPreview
from app.utils.spider.spider import Spider
from app.utils.spider.spider_exception import SpiderException
from app.schema.home import JavDBRanking

logger = logging.getLogger(__name__)


class JavBusSpider(Spider):
    host = "https://www.javbus.com/"
    name = 'JavBus'
    downloadable = True

    def __init__(self, alternate_host: str | None = None):
        # 不使用父类的自定义 Session，改用标准 requests.Session
        import requests as standard_requests

        # 初始化基础属性（不调用super().__init__()以避免使用自定义Session）
        from app.schema import Setting
        self.setting = Setting().app
        self.session = standard_requests.Session()

        # 如果指定了alternate_host，使用它
        if alternate_host:
            self.host = alternate_host

        # 配置 session
        user_agent = getattr(self.setting, 'user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        self.session.headers = {
            'User-Agent': user_agent,
            'Referer': self.host,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        self.session.verify = False
        self.session.timeout = 10

        logger.info(f"初始化爬虫: {self.name}, 域名: {self.host} (使用标准 requests.Session)")

        # 先访问首页建立正常的浏览会话
        self._initialize_session()

    def _initialize_session(self):
        """初始化 session，模拟正常浏览器访问"""
        try:
            # 先访问首页，建立正常session
            logger.info("初始化 JavBus session，访问首页...")
            home_response = self.session.get(self.host, allow_redirects=True)

            # 设置年龄验证 Cookie
            self._set_age_verification_cookies()

            # 等待一小段时间，模拟人类行为
            import time
            time.sleep(0.5)

            logger.info(f"Session 初始化完成，Cookie: {dict(self.session.cookies)}")
        except Exception as e:
            logger.warning(f"Session 初始化失败: {e}，将继续尝试")

    def _cookie_domain(self) -> str:
        """获取 Cookie 域名"""
        netloc = urlparse(self.host).netloc
        return f".{netloc}"

    def _set_age_verification_cookies(self):
        """设置年龄验证 Cookie 以绕过年龄确认页面"""
        try:
            dom = self._cookie_domain()
            # JavBus 使用 age=verified Cookie来标记用户已通过年龄验证
            self.session.cookies.set('age', 'verified', domain=dom)
            self.session.cookies.set('locale', 'zh', domain=dom)
            logger.info(f"已为 {dom} 设置年龄验证 Cookie")
        except Exception as e:
            logger.warning(f"设置年龄验证 Cookie 失败: {e}")

    def _check_and_bypass_verification(self, url: str):
        """检查是否遇到年龄验证页面，如果是则尝试绕过"""
        try:
            response = self.session.get(url, allow_redirects=True)

            # 检查是否被重定向到验证页面
            if 'driver-verify' in response.url or 'Age Verification' in response.text:
                logger.warning("检测到年龄验证页面，尝试重新初始化 session")

                # 清空现有 cookies 并重新设置
                self.session.cookies.clear()
                self._set_age_verification_cookies()

                # 重试请求，不跟随重定向以避免陷入循环
                response = self.session.get(url, allow_redirects=False)

                # 如果仍然重定向，尝试更激进的方法：创建全新session
                if response.status_code in (301, 302, 303, 307, 308):
                    logger.warning("Cookie方法失败，创建新session重试")
                    import requests

                    # 使用标准 requests.Session 而不是自定义 Session
                    new_session = requests.Session()
                    new_session.headers = self.session.headers.copy()
                    new_session.verify = False
                    new_session.cookies.set('age', 'verified', domain=self._cookie_domain())

                    self.session = new_session
                    response = self.session.get(url, allow_redirects=True)

            return response
        except Exception as e:
            logger.error(f"绕过验证时出错: {e}")
            # 如果出错，返回正常请求
            return self.session.get(url, allow_redirects=True)

    def get_info(self, num: str, url: str = None, include_downloads=False, include_previews=False):

        if url is None:
            url = urljoin(self.host, num)
        else:
            # 确保URL是完整的绝对URL
            if not url.startswith('http'):
                url = urljoin(self.host, url)
                
        # 允许重定向，防止302错误
        try:
            response = self.session.get(url, allow_redirects=True)
            
            # 检查响应状态码
            if response.status_code != 200:
                raise SpiderException(f'请求失败，状态码: {response.status_code}')
                
            html = etree.HTML(response.text)
            
            # 检查是否是有效的页面
            title_element = html.xpath("//h3")
            if not title_element:
                raise SpiderException('未找到番号')
                
            meta = VideoDetail()
            meta.num = num
            
            title = title_element[0].text
            meta.title = title

            # 尝试从页面中提取评分信息
            score_element = html.xpath("//div[contains(@class,'score')]")
            if score_element:
                score_text = etree.tostring(score_element[0], method='text', encoding='utf-8').decode('utf-8').strip()
                # 尝试提取评分值
                score_match = re.search(r'★\s*(\d+\.\d+)分', score_text)
                if score_match:
                    try:
                        meta.rating = score_match.group(1)
                    except:
                        pass
                
                # 尝试提取评论数，但VideoDetail没有这个字段，所以不设置

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
            
        except SpiderException as e:
            raise e
        except Exception as e:
            import logging
            logger = logging.getLogger('spider')
            logger.error(f"JavBus获取信息失败: {str(e)}")
            raise SpiderException(f'获取信息失败: {str(e)}')

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

    def get_actor_videos(self, actor_url: str):
        """获取演员的所有视频"""
        from app.schema.home import JavDBRanking  # 复用JavDBRanking模型
        import logging
        import re
        
        logger = logging.getLogger('spider')
        
        # 处理不同形式的actor_url输入
        if not actor_url.startswith(self.host):
            # 检查是否以/actors/开头，这是前端传来的格式
            if actor_url.startswith('/actors/'):
                # 提取演员名称，并进行搜索
                actor_name = actor_url.split('/')[-1]
                logger.info(f"从/actors/路径提取演员名称: {actor_name}")
                # 直接使用演员名称搜索，不尝试提取ID
                return self.get_actor_videos(actor_name)
            
            elif '/star/' not in actor_url and not actor_url.startswith('http'):
                # 如果是演员名称而不是URL，先搜索获取演员详情页URL
                actors = self.search_actor(actor_url)
                if not actors:
                    logger.info(f"未找到演员: {actor_url}")
                    return []
                
                # 从搜索结果中找出最匹配的演员
                best_match = None
                for actor in actors:
                    if actor.name.lower() == actor_url.lower() or actor_url.lower() in actor.name.lower():
                        best_match = actor
                        break
                
                if not best_match:
                    best_match = actors[0]  # 使用第一个结果
                
                # 从演员头像URL中提取演员ID
                thumb_url = best_match.thumb
                actor_id = None
                
                if thumb_url and 'actress' in thumb_url:
                    try:
                        # 处理类似 https://www.javbus.com/pics/actress/2de_a.jpg 的格式
                        actress_id = re.search(r'actress/([^/_]+)', thumb_url).group(1)
                        actor_id = actress_id
                        logger.info(f"从头像URL提取演员ID: {actress_id}")
                    except Exception as e:
                        logger.error(f"无法从头像URL提取演员ID: {thumb_url}, 错误: {str(e)}")
                
                if not actor_id and hasattr(best_match, 'url') and best_match.url:
                    # 尝试从URL获取
                    actor_url_match = re.search(r'/star/([^/]+)', str(best_match.url))
                    if actor_url_match:
                        actor_id = actor_url_match.group(1)
                        logger.info(f"从URL提取演员ID: {actor_id}")
                
                if actor_id:
                    actor_url = urljoin(self.host, f'/star/{actor_id}')
                    logger.info(f"构造演员URL: {actor_url}")
                else:
                    logger.error(f"无法构造演员URL，未找到演员ID: {actor_url}")
                    return []
            elif '/star/' in actor_url and not actor_url.startswith('http'):
                # 如果是相对路径如 /star/xxx
                actor_url = urljoin(self.host, actor_url)
                logger.info(f"构造完整URL: {actor_url}")
        
        logger.info(f"访问演员页面: {actor_url}")
        
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
            response = self.session.get(actor_url)
            html_content = response.text
            
            # 保存页面内容用于调试
            try:
                with open("javbus_actor_debug.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                logger.info("已保存演员详情页HTML文件")
            except Exception as e:
                logger.error(f"保存HTML文件失败: {str(e)}")
            
            result = []
            
            # 使用更可靠的XPath解析方法
            html = etree.HTML(html_content)
            
            # 使用XPath提取影片信息
            movie_boxes = html.xpath('//a[@class="movie-box"]')
            logger.info(f"找到 {len(movie_boxes)} 个视频元素")
            
            for box in movie_boxes:
                try:
                    # 提取链接
                    movie_url = box.get('href')
                    
                    # 提取封面图
                    img_element = box.xpath('.//img')[0]
                    cover_url = img_element.get('src')
                    title = img_element.get('title')
                    
                    # 提取番号
                    date_elements = box.xpath('.//date/text()')
                    if len(date_elements) >= 2:
                        num = date_elements[1]
                    else:
                        # 如果找不到番号，尝试从URL中提取
                        num_match = re.search(r'/([^/]+)$', movie_url)
                        num = num_match.group(1) if num_match else "Unknown"
                    
                    # 尝试从URL中提取实际番号，而不是使用日期作为番号
                    actual_num_match = re.search(r'/([A-Za-z]+-\d+)$', movie_url)
                    if actual_num_match:
                        num = actual_num_match.group(1)
                    # 如果URL中没有提取到番号格式，尝试从标题中提取
                    elif title:
                        title_num_match = re.search(r'([A-Za-z]+-\d+)', title)
                        if title_num_match:
                            num = title_num_match.group(1)
                    
                    # 是否有中文字幕标记
                    is_zh = len(box.xpath('.//button[contains(@class, "btn-primary") and contains(text(), "字幕")]')) > 0
                    
                    # 是否无码
                    is_uncensored = len(box.xpath('.//button[contains(@class, "btn-danger") and contains(text(), "无码")]')) > 0 or '无码' in title
                    
                    item = JavDBRanking()
                    item.cover = cover_url
                    if cover_url and cover_url.startswith('/'):
                        item.cover = urljoin(self.host, cover_url)
                    
                    item.title = title
                    item.num = num
                    
                    # 确保URL是完整的绝对URL
                    if movie_url and not movie_url.startswith('http'):
                        item.url = urljoin(self.host, movie_url)
                    else:
                        item.url = movie_url
                        
                    item.isZh = is_zh
                    item.is_uncensored = is_uncensored
                    
                    # 优化评分和评论数提取 - JavBus演员页面已包含基础信息
                    item.rank = None  # 使用rank字段保持与前端一致
                    item.rank_count = 0
                    
                    # 尝试从页面中提取评分信息，例如"★4.82分"这样的格式
                    score_element = box.xpath('.//div[contains(@class,"score")]')
                    if score_element:
                        score_text = etree.tostring(score_element[0], method='text', encoding='utf-8').decode('utf-8').strip()
                        # 尝试提取评分值
                        score_match = re.search(r'★\s*(\d+\.\d+)分', score_text)
                        if score_match:
                            try:
                                item.rating = score_match.group(1)
                                logger.info(f"从评分元素提取到评分: {item.rating}")
                            except:
                                pass
                        
                        # 尝试提取评论数，如果有类似"(123人评价)"的格式
                        count_match = re.search(r'(\d+)人評價', score_text)
                        if count_match:
                            try:
                                item.rank_count = int(count_match.group(1))
                                logger.info(f"从评分元素提取到评论数: {item.rank_count}")
                            except Exception as e:
                                logger.error(f"评论数解析失败: {score_text}, 错误: {str(e)}")
                    
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
                            logger.error(f"日期解析失败: {date_text}, 错误: {str(e)}")
                    
                    result.append(item)
                    logger.info(f"解析到视频: {num} - {title}")
                    
                except Exception as e:
                    logger.error(f"处理视频时出错: {str(e)}")
            
            return result
        
        except Exception as e:
            logger.error(f"获取演员视频列表失败: {str(e)}")
            return []
            
        finally:
            # 恢复原始头信息
            self.session.headers = original_headers
