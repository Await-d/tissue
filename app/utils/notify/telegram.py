import os
import requests

from app.schema import VideoNotify, SubscribeNotify
from app.schema.actor_subscribe import ActorSubscribeNotify
from app.utils import cache
from app.utils.notify.base import Base


class Telegram(Base):

    def send_video(self, video: VideoNotify):
        if video.is_success:
            actors = ', '.join(map(lambda i: i.name, video.actors))
            tags = []
            if video.is_zh: tags.append('中文')
            if video.is_uncensored: tags.append('无码')
            content = f'''
<b><tg-spoiler>{video.num}</tg-spoiler>整理成功</b>
演员：<tg-spoiler>{actors}</tg-spoiler>
大小：{video.size}
文件：<tg-spoiler>{video.path}</tg-spoiler>
标签：<tg-spoiler>{', '.join(tags)}</tg-spoiler>
'''
        else:
            content = f'''
<b>影片整理失败</b>
文件：<tg-spoiler>{video.path}</tg-spoiler>
大小：{video.size}
消息: <tg-spoiler>{video.message}</tg-spoiler>
'''
        picture = cache.get_cache_file('cover', video.cover)
        _, ext_name = os.path.splitext(video.cover)
        self.send(content, picture=picture, picture_name=f'cover{ext_name}')

    def send_subscribe(self, subscribe: SubscribeNotify):
        tags = []
        if subscribe.is_hd: tags.append('高清')
        if subscribe.is_zh: tags.append('中文')
        if subscribe.is_uncensored: tags.append('无码')

        content = f'''
<b><tg-spoiler>{subscribe.num}</tg-spoiler>开始下载</b>
演员：<tg-spoiler>{subscribe.actors}</tg-spoiler>
大小：{subscribe.size}
名称：<tg-spoiler>{subscribe.name}</tg-spoiler>
站点：<tg-spoiler>{subscribe.website}</tg-spoiler>
链接：<a href='{subscribe.url}'>点击</a>
日期：{subscribe.publish_date}
标签：<tg-spoiler>{', '.join(tags)}</tg-spoiler>
        '''
        picture = cache.get_cache_file('cover', subscribe.cover)
        _, ext_name = os.path.splitext(subscribe.cover)
        self.send(content, picture=picture, picture_name=f'cover{ext_name}')

    def send_actor_subscribe(self, actor_subscribe: ActorSubscribeNotify):
        tags = []
        if actor_subscribe.is_hd: tags.append('高清')
        if actor_subscribe.is_zh: tags.append('中文')
        if actor_subscribe.is_uncensored: tags.append('无码')

        content = f'''
<b>演员订阅: <tg-spoiler>{actor_subscribe.actor_name}</tg-spoiler>新作品</b>
番号：<tg-spoiler>{actor_subscribe.num}</tg-spoiler>
标题：<tg-spoiler>{actor_subscribe.title or '未知'}</tg-spoiler>
大小：{actor_subscribe.size or '未知'}
标签：<tg-spoiler>{', '.join(tags)}</tg-spoiler>
        '''
        picture = cache.get_cache_file('cover', actor_subscribe.cover) if actor_subscribe.cover else None
        picture_name = None
        if picture and actor_subscribe.cover:
            _, ext_name = os.path.splitext(actor_subscribe.cover)
            picture_name = f'cover{ext_name}'
        
        self.send(content, picture=picture, picture_name=picture_name)

    def send(self, content: str, picture: bytes = None, picture_name: str = None):
        token = self.setting.telegram_token
        chat_id = self.setting.telegram_chat_id

        if picture:
            url = f'https://api.telegram.org/bot{token}/sendPhoto'
            requests.post(url=url, data={
                'chat_id': chat_id,
                'parse_mode': 'HTML',
                'caption': content,
                'has_spoiler': True
            }, files={
                'photo': (picture_name, picture)
            })
        else:
            url = f'https://api.telegram.org/bot{token}/sendMessage'
            requests.post(url=url, data={
                'chat_id': chat_id,
                'parse_mode': 'HTML',
                'text': content,
            })
