#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from urllib.parse import urljoin
from app.utils.spider.javdb import JavdbSpider


def main():
    logging.basicConfig(level=logging.INFO)

    spider = JavdbSpider()
    print("=== JavDB 动态域名选择与访问测试 ===")
    print(f"[INFO] 当前选择的可用域名: {spider.host}")

    test_paths = [
        "/",
        "/videos",
        "/rankings/movies?p=weekly&amp;t=censored",
    ]

    for path in test_paths:
        url = urljoin(spider.host, path)
        try:
            resp = spider._get(url)
            print(f"[TEST] GET {url} - status={resp.status_code}, bytes={len(resp.content)}")
        except Exception as e:
            print(f"[ERROR] 访问失败: {url} - {e}")

    # 打印 cookies 域，确认已按当前 host 设置 over18/locale
    cookie_domains = sorted({c.domain for c in spider.session.cookies})
    print(f"[INFO] 已设置 Cookie 域: {cookie_domains}")

    print("=== 测试完成 ===")


if __name__ == "__main__":
    main()