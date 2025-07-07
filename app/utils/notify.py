import logging
from app.utils.logger import logger

def send_notify(title, content, image_url=None):
    """
    发送通知
    :param title: 通知标题
    :param content: 通知内容
    :param image_url: 图片URL
    """
    try:
        # 这里可以实现实际的通知发送逻辑，如调用第三方通知服务
        # 例如：钉钉、企业微信、Telegram等
        logger.info(f"发送通知: {title}")
        logger.debug(f"通知内容: {content}")
        logger.debug(f"通知图片: {image_url}")
        
        # 当前仅记录日志，实际项目中可以替换为真实的通知实现
    except Exception as e:
        logger.error(f"发送通知失败: {e}")

def send_subscribe(data):
    """
    发送视频订阅通知
    :param data: 订阅通知数据
    """
    try:
        title = f"订阅下载: {data.num}"
        content = f"""
        标题: {data.title or '未知'}
        演员: {data.actors or '未知'}
        大小: {data.size or '未知'}
        特征: {'高清 ' if data.is_hd else ''}{'中文 ' if data.is_zh else ''}{'无码' if data.is_uncensored else ''}
        """
        send_notify(title, content, data.cover)
    except Exception as e:
        logger.error(f"发送订阅通知失败: {e}")

def send_actor_subscribe(data):
    """
    发送演员订阅通知
    :param data: 通知数据，包含演员名称、视频信息等
    """
    try:
        title = f"演员订阅: {data['actor_name']} 新作品"
        content = f"""
        番号: {data['num']}
        标题: {data['title'] or '未知'}
        大小: {data['size'] or '未知'}
        特征: {'高清 ' if data.get('is_hd') else ''}{'中文 ' if data.get('is_zh') else ''}{'无码' if data.get('is_uncensored') else ''}
        """
        send_notify(title, content, data.get('cover'))
    except Exception as e:
        logger.error(f"发送演员订阅通知失败: {e}") 