import json
import random
import time
import traceback
from typing import Optional, List
from urllib.parse import urljoin

import requests

from app.exception import BizException
from app.schema import Setting
from app.utils.logger import logger


class QBittorent:
    def __init__(self):
        setting = Setting().download
        self.host = setting.host
        self.tracker_subscribe = setting.tracker_subscribe
        self.savepath = setting.savepath
        self.category = setting.category
        self.session = requests.Session()

    def login(self):
        try:
            setting = Setting().download
            
            # 获取带协议头的host
            host = self._get_host_with_scheme()
            logger.info(f"尝试登录qBittorrent: {host}")
            logger.info(f"用户名: {setting.username}")
                
            response = self.session.post(
                url=urljoin(host, "/api/v2/auth/login"),
                data={"username": setting.username, "password": setting.password},
            )
            logger.info(f"登录响应状态码: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"登录失败，响应内容: {response.text}")
                raise BizException(response.text)
            else:
                logger.info("qBittorrent登录成功")
        except Exception as e:
            logger.error(f"下载器连接失败: {str(e)}")
            raise BizException("下载器连接失败")

    def test_connection(self):
        """
        测试qBittorrent连接是否正常
        
        Returns:
            dict: 测试结果，包含状态和详细信息
        """
        try:
            # 首先尝试登录
            setting = Setting().download
            
            if not self.host or not self.host.strip():
                return {"status": False, "message": "下载器地址未配置"}
                
            if not setting.username or not setting.password:
                return {"status": False, "message": "下载器用户名或密码未配置"}
            
            # 获取带协议头的host
            host = self._get_host_with_scheme()
            
            # 尝试登录
            login_response = self.session.post(
                url=urljoin(host, "/api/v2/auth/login"),
                data={"username": setting.username, "password": setting.password},
                timeout=5  # 设置5秒超时
            )
            
            if login_response.status_code != 200:
                return {"status": False, "message": f"登录失败: {login_response.text}"}
            
            # 尝试获取基本信息验证登录状态
            version_response = self.session.get(
                urljoin(host, "/api/v2/app/version"),
                timeout=5
            )
            
            if version_response.status_code != 200:
                return {"status": False, "message": "无法获取版本信息，请检查权限设置"}
            
            # 进一步测试获取种子列表API
            torrents_response = self.session.get(
                urljoin(host, "/api/v2/torrents/info"),
                timeout=5
            )
            
            if torrents_response.status_code != 200:
                return {
                    "status": False, 
                    "message": f"无法获取种子列表，API响应错误: {torrents_response.status_code}"
                }
            
            torrents_count = len(torrents_response.json())
            
            # 检查保存路径是否设置
            save_path_message = ""
            if not self.savepath:
                save_path_message = "（警告：下载保存路径未设置）"
            
            return {
                "status": True, 
                "message": f"连接成功! qBittorrent版本: {version_response.text}, 当前种子数: {torrents_count} {save_path_message}",
                "version": version_response.text,
                "torrents_count": torrents_count
            }
        except requests.exceptions.ConnectionError:
            return {"status": False, "message": "连接错误，请检查下载器地址是否正确"}
        except requests.exceptions.Timeout:
            return {"status": False, "message": "连接超时，请检查下载器是否在线"}
        except Exception as e:
            logger.error(f"测试下载器连接出错: {str(e)}")
            return {"status": False, "message": f"连接测试失败: {str(e)}"}

    def auth(func):
        def wrapper(self, *args, **kwargs):
            try:
                logger.debug(f"执行qBittorrent方法: {func.__name__}")
                response = func(self, *args, **kwargs)
                if response.status_code == 403:
                    logger.info("登录信息失效，将尝试重新登录...")
                    raise Exception()
                logger.debug(f"qBittorrent方法 {func.__name__} 执行成功")
                return response
            except Exception as e:
                logger.info(f"qBittorrent方法 {func.__name__} 执行失败，尝试重新登录: {str(e)}")
                self.login()
                response = func(self, *args, **kwargs)
                logger.debug(f"重新登录后，qBittorrent方法 {func.__name__} 执行成功")
                return response

        return wrapper

    def _get_host_with_scheme(self):
        """
        确保host包含协议头
        
        Returns:
            str: 包含协议头的host地址
        """
        if not self.host:
            return ""
            
        host = self.host
        if not (host.startswith('http://') or host.startswith('https://')):
            host = 'http://' + host
        return host

    @auth
    def get_torrents(
        self, category: Optional[str] = None, include_failed=True, include_success=True
    ):
        host = self._get_host_with_scheme()
        response = self.session.get(
            urljoin(host, "/api/v2/torrents/info"),
            params={"category": category},
        )
        
        if response.status_code != 200:
            return response
            
        result = response.json()

        if not include_failed:
            result = list(filter(lambda item: "整理失败" not in item["tags"], result))

        if not include_success:
            result = list(filter(lambda item: "整理成功" not in item["tags"], result))

        # 将过滤后的结果设置回response对象（作为自定义属性）
        response.filtered_data = result
        return response

    @auth
    def get_torrent_files(self, torrent_hash: str):
        host = self._get_host_with_scheme()
        return self.session.get(
            urljoin(host, "/api/v2/torrents/files"),
            params={
                "hash": torrent_hash,
            },
        )

    @auth
    def add_torrent_tags(self, torrent_hash: str, tags: List[str]):
        host = self._get_host_with_scheme()
        self.session.post(
            urljoin(host, "/api/v2/torrents/addTags"),
            data={"hashes": torrent_hash, "tags": ",".join(tags)},
        )

    @auth
    def remove_torrent_tags(self, torrent_hash: str, tags: List[str]):
        host = self._get_host_with_scheme()
        self.session.post(
            urljoin(host, "/api/v2/torrents/removeTags"),
            data={"hashes": torrent_hash, "tags": ",".join(tags)},
        )

    @auth
    def delete_torrent(self, torrent_hash: str, delete_files: bool = True):
        host = self._get_host_with_scheme()
        return self.session.post(
            urljoin(host, "/api/v2/torrents/delete"),
            data={"hashes": torrent_hash, "deleteFiles": "true" if delete_files else "false"},
        )

    @auth
    def pause_torrent(self, torrent_hash: str):
        """暂停种子"""
        host = self._get_host_with_scheme()
        return self.session.post(
            urljoin(host, "/api/v2/torrents/pause"),
            data={"hashes": torrent_hash},
        )

    @auth
    def resume_torrent(self, torrent_hash: str):
        """恢复/开始种子下载"""
        host = self._get_host_with_scheme()
        return self.session.post(
            urljoin(host, "/api/v2/torrents/resume"),
            data={"hashes": torrent_hash},
        )

    @auth
    def stop_torrent(self, torrent_hash: str):
        """停止种子（停止做种）"""
        host = self._get_host_with_scheme()
        return self.session.post(
            urljoin(host, "/api/v2/torrents/stop"),
            data={"hashes": torrent_hash},
        )

    @auth
    def get_trans_info(self):
        host = self._get_host_with_scheme()
        return self.session.get(urljoin(host, "/api/v2/transfer/info"))

    @auth
    def add_magnet(self, magnet: str, savepath: Optional[str] = None, category: Optional[str] = None, paused: bool = False):
        host = self._get_host_with_scheme()
        nonce = "".join(random.sample("abcdefghijklmnopqrstuvwxyz", 5))
        data = {"urls": magnet, "tags": nonce}
        
        # 设置是否暂停
        if paused:
            data["paused"] = "true"

        if savepath:
            data["savepath"] = savepath
        elif self.savepath:
            data["savepath"] = self.savepath
            
        # 设置分类
        if category:
            data["category"] = category
        elif self.category:
            data["category"] = self.category

        response = self.session.post(
            urljoin(host, "/api/v2/torrents/add"), data=data
        )
        if response.status_code != 200:
            # 设置hash为None以避免AttributeError
            response.hash = None
            return response

        torrent_hash = ""
        for _ in range(5):
            time.sleep(1)
            torrents = self.session.get(
                urljoin(host, "/api/v2/torrents/info"), params={"tag": nonce}
            ).json()
            if torrents:
                torrent_hash = torrents[0]["hash"]
                break
        
        # 设置hash属性，即使为空也要设置以避免AttributeError
        response.hash = torrent_hash

        if self.tracker_subscribe and torrent_hash:
            trackers_text = requests.get(self.tracker_subscribe).text
            trackers = "\n".join(filter(lambda item: item, trackers_text.split("\n")))
            self.session.post(
                urljoin(host, "/api/v2/torrents/addTrackers"),
                data={"hash": torrent_hash, "urls": trackers},
            )

        self.remove_torrent_tags(torrent_hash, [nonce])
        return response
    
    @auth
    def set_file_priority(self, torrent_hash: str, file_ids: List[int], priority: int):
        """
        设置种子文件下载优先级
        
        Args:
            torrent_hash: 种子hash
            file_ids: 文件ID列表
            priority: 优先级 (0=不下载, 1=普通, 6=高, 7=最高)
        """
        host = self._get_host_with_scheme()
        return self.session.post(
            urljoin(host, "/api/v2/torrents/filePrio"),
            data={
                "hash": torrent_hash, 
                "id": "|".join(map(str, file_ids)), 
                "priority": priority
            }
        )
    
    @auth
    def set_files_priority_bulk(self, torrent_hash: str, priorities: List[int]):
        """
        批量设置种子所有文件的下载优先级
        
        Args:
            torrent_hash: 种子hash
            priorities: 优先级列表，按文件索引顺序 (0=不下载, 1=普通, 6=高, 7=最高)
        """
        host = self._get_host_with_scheme()
        return self.session.post(
            urljoin(host, "/api/v2/torrents/filePrio"),
            data={
                "hash": torrent_hash, 
                "id": "|".join(map(str, range(len(priorities)))), 
                "priority": "|".join(map(str, priorities))
            }
        )

    @auth
    def get_all_torrents(self):
        """获取所有种子信息，不过滤"""
        host = self._get_host_with_scheme()
        logger.info(f"正在向qBittorrent请求种子列表: {host}/api/v2/torrents/info")
        
        response = self.session.get(
            urljoin(host, "/api/v2/torrents/info"),
            timeout=10
        )
        
        logger.info(f"qBittorrent响应状态码: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"qBittorrent API响应错误: {response.status_code} - {response.text}")
            return response  # 让装饰器处理错误响应
        
        torrents = response.json()
        logger.info(f"成功获取到 {len(torrents)} 个种子")
        
        # 打印前几个种子的详细信息用于调试
        if len(torrents) > 0:
            logger.info("前3个种子信息:")
            for i, torrent in enumerate(torrents[:3]):
                logger.info(f"  种子{i+1}: 名称={torrent.get('name', 'N/A')}, 状态={torrent.get('state', 'N/A')}, 进度={torrent.get('progress', 0):.2%}, 标签={torrent.get('tags', 'N/A')}")
        
        return response  # 返回response对象，而不是种子列表
    
    def extract_hash_from_magnet(self, magnet: str) -> Optional[str]:
        """从磁力链接中提取hash值
        
        Args:
            magnet: 磁力链接
            
        Returns:
            str: 提取的hash值，如果提取失败则返回None
        """
        try:
            import re
            hash_match = re.search(r'btih:([a-fA-F0-9]{40})', magnet)
            if not hash_match:
                hash_match = re.search(r'btih:([a-fA-F0-9]{32})', magnet)
            
            if hash_match:
                return hash_match.group(1).lower()
            return None
        except Exception as e:
            logger.error(f"从磁力链接提取hash失败: {e}")
            return None
            
    def is_magnet_exists(self, magnet: str) -> bool:
        """检查磁力链接是否已在qBittorrent中下载
        
        Args:
            magnet: 磁力链接
            
        Returns:
            bool: 如果已存在则返回True，否则返回False
        """
        try:
            # 从磁力链接中提取hash
            torrent_hash = self.extract_hash_from_magnet(magnet)
            if not torrent_hash:
                logger.warning(f"无法从磁力链接中提取hash: {magnet}")
                return False
                
            # 获取所有种子
            all_torrents = self.get_all_torrents()
            
            # 检查是否有匹配的hash
            for torrent in all_torrents:
                if torrent["hash"].lower() == torrent_hash:
                    logger.info(f"种子已存在于qBittorrent中: {torrent_hash}")
                    return True
                    
            return False
        except Exception as e:
            logger.error(f"检查种子是否存在时出错: {e}")
            return False

    def _delete_torrent_by_magnet(self, magnet: str):
        """通过magnet链接删除qBittorrent中的种子"""
        try:
            # 从magnet链接中提取hash
            torrent_hash = self.extract_hash_from_magnet(magnet)
            
            if torrent_hash:
                # 调用qBittorrent API删除种子（包括文件）
                response = self.delete_torrent(torrent_hash, delete_files=True)
                if response.status_code == 200:
                    logger.info(f"成功删除种子: {torrent_hash}")
                else:
                    logger.warning(f"删除种子失败: {torrent_hash}, 状态码: {response.status_code}")
            else:
                logger.warning(f"无法从magnet链接中提取hash: {magnet}")
        except Exception as e:
            logger.error(f"删除种子时发生错误: {e}")


qbittorent = QBittorent()
