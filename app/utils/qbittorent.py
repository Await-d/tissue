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
        self.session = requests.Session()

    def login(self):
        try:
            setting = Setting().download
            
            # 获取带协议头的host
            host = self._get_host_with_scheme()
                
            response = self.session.post(
                url=urljoin(host, "/api/v2/auth/login"),
                data={"username": setting.username, "password": setting.password},
            )
            if response.status_code != 200:
                raise BizException(response.text)
        except:
            logger.info("下载器连接失败")
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
            
            # 检查保存路径是否设置
            save_path_message = ""
            if not self.savepath:
                save_path_message = "（警告：下载保存路径未设置）"
            
            return {
                "status": True, 
                "message": f"连接成功! qBittorrent版本: {version_response.text} {save_path_message}",
                "version": version_response.text
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
                response = func(self, *args, **kwargs)
                if response.status_code == 403:
                    logger.info("登录信息失效，将尝试重新登登录...")
                    raise Exception()
            except:
                self.login()
                response = func(self, *args, **kwargs)
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
        result = self.session.get(
            urljoin(host, "/api/v2/torrents/info"),
            params={"category": category},
        ).json()

        if not include_failed:
            result = filter(lambda item: "整理失败" not in item["tags"], result)

        if not include_success:
            result = filter(lambda item: "整理成功" not in item["tags"], result)

        return result

    @auth
    def get_torrent_files(self, torrent_hash: str):
        host = self._get_host_with_scheme()
        return self.session.get(
            urljoin(host, "/api/v2/torrents/files"),
            params={
                "hash": torrent_hash,
            },
        ).json()

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
    def get_trans_info(self):
        host = self._get_host_with_scheme()
        return self.session.get(urljoin(host, "/api/v2/transfer/info")).json()

    @auth
    def add_magnet(self, magnet: str, savepath: Optional[str] = None):
        host = self._get_host_with_scheme()
        nonce = "".join(random.sample("abcdefghijklmnopqrstuvwxyz", 5))
        data = {"urls": magnet, "tags": nonce}

        if savepath:
            data["savepath"] = savepath
        elif self.savepath:
            data["savepath"] = self.savepath

        response = self.session.post(
            urljoin(host, "/api/v2/torrents/add"), data=data
        )
        if response.status_code != 200:
            return response

        torrent_hash = ""
        for _ in range(5):
            time.sleep(1)
            torrents = self.session.get(
                urljoin(host, "/api/v2/torrents/info"), params={"tag": nonce}
            ).json()
            if torrents:
                torrent_hash = torrents[0]["hash"]
                response.hash = torrent_hash
                break

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
    def get_all_torrents(self):
        """获取所有种子信息，不过滤"""
        host = self._get_host_with_scheme()
        return self.session.get(
            urljoin(host, "/api/v2/torrents/info")
        ).json()
    
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
