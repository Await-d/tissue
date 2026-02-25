"""
多平台爬虫实时连通性测试
用法: python3 scripts/check_spiders_live.py [--num SONE-001]
"""

import argparse
import json
import logging
import sys
import time
from typing import Any, Dict

# 静默非关键日志
logging.basicConfig(level=logging.WARNING)
logging.getLogger("spider").setLevel(logging.INFO)

TEST_NUM_DEFAULT = "SONE-001"


def _check_spider(
    spider_cls, num: str, include_previews: bool = True
) -> Dict[str, Any]:
    result = {
        "spider": spider_cls.__name__,
        "host": getattr(spider_cls, "host", ""),
        "num": num,
        "pass": False,
        "blocked": False,
        "fields": {},
        "error": None,
    }
    try:
        spider = spider_cls()

        # 探测连通性
        host_url = getattr(spider, "host", "") or getattr(spider_cls, "origin_host", "")
        if host_url:
            try:
                probe = spider.session.get(host_url, timeout=15)
                if probe.status_code in (403, 429, 503):
                    result["blocked"] = True
                    result["error"] = f"host_blocked:{probe.status_code}"
                    return result
            except Exception as e:
                result["blocked"] = True
                result["error"] = f"host_unreachable:{e}"
                return result

        detail = spider.get_info(
            num=num,
            url=None,
            include_downloads=True,
            include_previews=include_previews,
            include_comments=False,
        )

        fields = {
            "num": detail.num or "",
            "title": (detail.title or "")[:60],
            "cover": bool(detail.cover),
            "actress_count": len(detail.actors or []),
            "download_count": len(detail.website or []),
            "preview_groups": len(detail.previews or []),
            "preview_items": sum(len(g.items or []) for g in (detail.previews or [])),
            "premiered": detail.premiered or "",
            "studio": detail.studio or "",
        }
        result["fields"] = fields
        result["pass"] = bool(detail.num and detail.title)

    except Exception as exc:
        result["error"] = str(exc)

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="多平台爬虫实时测试")
    parser.add_argument("--num", default=TEST_NUM_DEFAULT, help="测试番号")
    parser.add_argument("--no-previews", action="store_true", help="跳过预览获取")
    args = parser.parse_args()

    from app.utils.spider.javbus import JavbusSpider
    from app.utils.spider.dmm import DmmSpider
    from app.utils.spider.jav321 import Jav321Spider

    spiders = [JavbusSpider, Jav321Spider, DmmSpider]
    results = []

    for cls in spiders:
        print(f"\n{'=' * 50}", flush=True)
        print(f"测试: {cls.__name__}  num={args.num}", flush=True)
        r = _check_spider(cls, args.num, include_previews=not args.no_previews)
        results.append(r)
        print(json.dumps(r, ensure_ascii=False, indent=2), flush=True)
        time.sleep(2)

    # 汇总
    print(f"\n{'=' * 50}")
    print("汇总:")
    all_pass = True
    for r in results:
        status = (
            "✅ PASS" if r["pass"] else ("⚠️  BLOCKED" if r["blocked"] else "❌ FAIL")
        )
        all_pass = all_pass and r["pass"]
        print(f"  {status}  {r['spider']:<20}  {r.get('error') or ''}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
