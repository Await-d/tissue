import argparse
import json
from typing import Any, Dict, List

from lxml import etree

from app.utils.spider.javdb import JavdbSpider


def _pick_first_valid(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    for item in videos:
        if item.get("num") and item.get("url"):
            return item
    return {}


def run_check(video_type: str, cycle: str, include_previews: bool) -> Dict[str, Any]:
    spider = JavdbSpider()

    probe_url = f"{spider.host}/rankings/movies?p={cycle}&t={video_type}"
    blocked = False
    blocked_reason = ""
    try:
        probe_resp = spider._get(probe_url)
        title = ""
        html = etree.HTML(probe_resp.content, parser=etree.HTMLParser(encoding="utf-8"))
        if html is not None:
            title_nodes = html.xpath("//title/text()")
            title = (title_nodes[0] if title_nodes else "").strip()

        if probe_resp.status_code in (401, 403, 429, 503):
            blocked = True
            blocked_reason = f"http_{probe_resp.status_code}"
        elif "redirecting" in title.lower() or "just a moment" in title.lower():
            blocked = True
            blocked_reason = f"challenge_title:{title}"
    except Exception as exc:
        blocked = True
        blocked_reason = f"probe_error:{exc}"

    if blocked:
        return {
            "pass": False,
            "blocked": True,
            "blocked_reason": blocked_reason,
            "video_type": video_type,
            "cycle": cycle,
            "ranking_count": 0,
            "first_ranking": {},
            "detail": {},
            "error": "network_or_waf_blocked",
        }

    rankings = spider.get_ranking_with_details(
        video_type=video_type, cycle=cycle, max_pages=1
    )
    ranking_count = len(rankings)
    first = _pick_first_valid(rankings) if rankings else {}

    detail_ok = False
    detail_data: Dict[str, Any] = {}
    error = None

    if first:
        try:
            detail = spider.get_info(
                num=str(first.get("num")),
                url=str(first.get("url")),
                include_downloads=False,
                include_previews=include_previews,
                include_comments=False,
            )
            detail_data = {
                "num": detail.num,
                "title": detail.title,
                "cover": detail.cover,
                "website_count": len(detail.website or []),
                "preview_groups": len(detail.previews or []),
                "preview_items": sum(
                    len(group.items or []) for group in (detail.previews or [])
                ),
            }
            detail_ok = bool(detail.num and detail.title)
        except Exception as exc:
            error = f"detail_error: {exc}"
    else:
        error = "ranking_empty_or_missing_num_url"

    pass_ok = ranking_count > 0 and detail_ok

    return {
        "pass": pass_ok,
        "blocked": False,
        "blocked_reason": "",
        "video_type": video_type,
        "cycle": cycle,
        "ranking_count": ranking_count,
        "first_ranking": {
            "num": first.get("num"),
            "title": first.get("title"),
            "url": first.get("url"),
            "rating": first.get("rating"),
            "rank": first.get("rank"),
            "rank_count": first.get("rank_count"),
            "publish_date": first.get("publish_date"),
            "is_zh": first.get("is_zh"),
        }
        if first
        else {},
        "detail": detail_data,
        "error": error,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--video-type", default="censored", choices=["censored", "uncensored"]
    )
    parser.add_argument(
        "--cycle", default="daily", choices=["daily", "weekly", "monthly"]
    )
    parser.add_argument("--include-previews", action="store_true")
    args = parser.parse_args()

    result = run_check(args.video_type, args.cycle, args.include_previews)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
