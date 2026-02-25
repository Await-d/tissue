from urllib.parse import urljoin

import requests
from lxml import etree

from app.schema import VideoDetail, VideoActor
from app.utils.spider.spider import Spider
from app.utils.spider.spider_exception import SpiderException


class Jav321Spider(Spider):
    host = "https://www.jav321.com/"
    name = 'Jav321'
    downloadable = False

    def get_info(self, num: str, url: str = None, include_downloads=False, include_previews=False,
                 include_comments: bool = False):
        response = self.session.post(urljoin(self.host, '/search'), data={'sn': num})
        html = etree.HTML(response.text)

        no = html.xpath("//small")
        if not no or num.lower() not in no[0].text.lower().strip():
            raise SpiderException('未找到番号')

        meta = VideoDetail()
        meta.num = num

        # Title: <h3>Title Text <small>num</small></h3>
        h3 = html.xpath("//h3")
        if h3:
            # Get full text then strip the trailing num in <small>
            h3_el = h3[0]
            title_parts = [h3_el.text or ""]
            for child in h3_el:
                if child.tag != "small":
                    title_parts.append(child.text_content() if hasattr(child, 'text_content') else (child.text or ""))
            meta.title = "".join(title_parts).strip()

        # Cover image
        cover_els = html.xpath("//div[contains(@class,'col-md-3')]//img/@src")
        if cover_els:
            meta.cover = cover_els[0]

        # Metadata from <b> labels
        info_rows = html.xpath("//div[b]")
        if info_rows:
            info_text = etree.tostring(info_rows[0], encoding='unicode', method='text')
            import re
            m = re.search(r'配信開始日[:\s]*([\d\-/]+)', info_text)
            if m:
                meta.premiered = m.group(1).strip()
            m = re.search(r'収録時間[:\s]*([\d]+)', info_text)
            if m:
                meta.runtime = m.group(1).strip()
            m = re.search(r'平均評価[:\s]*([\d.]+)', info_text)
            if m:
                meta.rating = m.group(1).strip()

        # Outline
        outline_element = no[0].xpath("./../../..//div[@class='row']")
        if len(outline_element) > 0:
            outline = outline_element[-1].xpath("./div")
            if outline and outline[0].text:
                meta.outline = outline[0].text.replace("\n", "")
                brs = outline[0].xpath('./br')
                if brs:
                    extra_outline = "".join(i.tail for i in brs if i.tail)
                    hr_index = extra_outline.find("----------------------")
                    if hr_index != -1:
                        meta.outline += (extra_outline[0:hr_index])
                    else:
                        meta.outline += extra_outline

        meta.website.append(response.url)
        return meta
