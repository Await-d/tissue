import re
import time
import logging
from datetime import datetime
from random import randint
from urllib.parse import urljoin
from lxml import etree
from app.schema import VideoDetail, VideoActor, VideoDownload, VideoPreviewItem, VideoPreview, VideoCommentItem, \
    VideoComment
from app.schema.home import JavDBRanking
from app.utils.spider.spider import Spider
from app.utils.spider.spider_exception import SpiderException

logger = logging.getLogger('spider')


class JavDBSpider(Spider):
    name = 'JavDB'
    origin_host = "https://javdb.com"
    downloadable = True
    avatar_host = 'https://c0.jdbstatic.com/avatars/'

    def get_info(self, num: str, url: str = None, include_downloads=False, include_previews=False,
                 include_comments=False):

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

        if include_comments:
            meta.comments = self.get_comments(url)

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
            return None
        return None

    def get_previews(self, html: etree.HTML):
        result = []

        videos = html.xpath("//div[contains(@class,'preview-images')]/a[@class='preview-video-container']")
        for video in videos:
            thumb = video.xpath('./img')[0]
            video = html.xpath(f"//video[@id='{video.get('href')[1:]}']/source")
            if video:
                preview = VideoPreviewItem(type='video', thumb=thumb.get('src'), url=video[0].get('src'))
                result.append(preview)

        images = html.xpath("//div[contains(@class,'preview-images')]/a[@class='tile-item']")
        for image in images:
            thumb = image.xpath('./img')[0]
            preview = VideoPreviewItem(type='image', thumb=thumb.get('src'), url=image.get('href'))
            result.append(preview)

        return [VideoPreview(website=self.name, items=result)]

    def get_comments(self, url: str):
        result = []

        code = url.split('/')[-1]
        response = self.session.get(f'{self.host}/v/{code}/reviews/lastest')
        html = etree.HTML(response.content, parser=etree.HTMLParser(encoding='utf-8'))

        items = html.xpath("//dt[@class='review-item']")
        for item in items:
            comment = VideoCommentItem(id=item.get('id'))

            comment.name = ''.join(
                [node.replace(r'\xa0', '').strip() for node in item.xpath('./div[@class="review-title"]/text()')])
            comment.score = len(item.xpath('.//i[@class="icon-star"]'))

            publish_date = item.xpath(".//span[@class='time']")
            if publish_date:
                comment.publish_date = datetime.strptime(publish_date[0].text.strip(), "%Y-%m-%d").date()

            comment.likes = int(item.xpath('.//span[@class="likes-count"]')[0].text)

            content_list = []
            contents = item.xpath('./div[@class="content"]/p')
            for content in contents:
                content_list.append(''.join([text for text in content.itertext()]))
            comment.content = '\n\n'.join(content_list)

            result.append(comment)

        return [VideoComment(website=self.name, items=result)]

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
                if '-U.无码破解' in name[0].text:
                    download.is_uncensored = True
                if '-UC.无码破解' in name[0].text:
                    download.is_zh = True
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
                    #
                # 构造头像URL
                actor_avatar = urljoin(self.avatar_host, f'{actor_code[0:2].lower()}/{actor_code}.jpg')

                actor_info = VideoActor(name=name, thum')
            logger.info(f"从演员页面找到 {len(movie_boxes)} 个作品")

            for box in movie_boxes:
                try:
                    item = JavDBRanking()

                    # 提取视频URL
                    video_url = box.get('href')
                    if not video_url.startswith('http'):
                        video_url = urljoin(self.host, video_url)
                    item.url = video_url

                    # 提取番号和标题
                    title_element = box.xpath('.//div[contains(@class, "video-title")]')
                    if title_element:
                        # 提取番号
                        num_element = title_element[0].xpath('./strong/text()')
                        if num_element:
                            item.num = num_element[0].strip()

 ', score_text)
                        if score_match:
                            try:
                                rating_value = float(score_match.group(1))
                                item.rank = rating_value  # 前端使用
                                item.rating = str(rating_value)  # 演员订阅使用
                            except:
                                pass

                        # 解析评论数
                        count_match = re.search(r'由(\d+)人評價', score_text)
                        if count_match:
                            try:
                                comments_value = int(count_match.group(1))
                                item.rank_count = comments_value
                            except:
                                pass

                    # 检查中文字幕和无码标签
                    cnsub_element = box.xpath('.//span[contains(@class, "cnsub")]')
                    item.isZh = len(cnsub_element) > 0

                    uncensored_element = box.xpath('.//span[contains(@class, "uncensored")]')
                    item.is_uncensored = len(uncensored_element) > 0

                    # 提取发布日期
                    date_element = box.xpath('.//div[contains(@class, "meta")]/text()')
                    if date_element and len(date_element) > 0:
                        date_text = date_element[0].strip()
                        try:
                            # 解析日期格式 YYYY-MM-DD
                            if re.match(r'\d{4}-\d{2}-\d{2}', date_text):
                                item.publish_date = datetime.strptime(date_text, "%Y-%m-%d").date()
                        except:
                            pass

                    # 只有有番号的条目才添加到结果中
                    if item.num:
                        result.append(item)

                except Exception as e:
                    logger.error(f"处理作品条目时出错: {str(e)}")
                    continue

            logger.info(f"成功提取到 {len(result)} 个作品信息，包含评分、评论数、日期等完整信息")
            return result

        finally:
            # 恢复原始头信息
            self.session.headers = original_headers
