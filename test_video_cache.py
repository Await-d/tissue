"""
测试视频缓存系统
"""
import sys
import asyncio
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.db import SessionFactory
from app.service.video_cache import VideoCacheService


async def test_video_cache():
    """测试视频缓存功能"""
    print("=" * 60)
    print("测试视频缓存系统")
    print("=" * 60)

    with SessionFactory() as db:
        cache_service = VideoCacheService(db)

        # 1. 测试抓取和缓存排行榜数据
        print("\n[1] 测试抓取并缓存排行榜数据...")
        stats = cache_service.fetch_and_cache_rankings(
            sources=['JavDB'],
            video_types=['censored', 'uncensored'],
            cycles=['daily'],
            max_pages=1  # 只测试1页
        )

        print(f"   抓取完成: 总计 {stats['total_fetched']} 个")
        print(f"   新增: {stats['total_new']} 个")
        print(f"   更新: {stats['total_updated']} 个")
        if stats['errors']:
            print(f"   错误: {len(stats['errors'])} 个")
            for error in stats['errors']:
                print(f"      - {error}")

        # 2. 测试查询缓存数据
        print("\n[2] 测试查询缓存数据...")
        videos = cache_service.query_videos(
            min_rating=4.0,
            min_comments=10,
            is_hd=None,
            is_zh=None,
            days=7,
            limit=10
        )

        print(f"   查询到 {len(videos)} 个符合条件的视频（评分>=4.0，评论>=10）")
        if videos:
            print("\n   前5个视频:")
            for i, video in enumerate(videos[:5], 1):
                print(f"   {i}. {video['num']} - {video['title'][:30]}")
                print(f"      评分: {video['rating']}, 评论数: {video['comments_count']}, 来源: {video['source']}")

        # 3. 测试获取特定排行榜
        print("\n[3] 测试获取特定排行榜...")
        ranking_videos = cache_service.get_ranking_videos(
            source='JavDB',
            video_type='censored',
            cycle='daily',
            limit=5
        )

        print(f"   获取到 {len(ranking_videos)} 个排行榜视频")
        if ranking_videos:
            print("\n   排行榜前5:")
            for i, video in enumerate(ranking_videos, 1):
                print(f"   #{i}. {video['num']} - {video['title'][:30]}")
                print(f"      评分: {video['rating']}, 排名: {video.get('rank_position')}")

        # 4. 测试缓存统计
        print("\n[4] 缓存统计信息...")
        cache_stats = cache_service.get_cache_stats()
        print(f"   总视频数: {cache_stats['total_videos']}")
        print(f"   按数据源:")
        for source, count in cache_stats['by_source'].items():
            print(f"      {source}: {count} 个")
        print(f"   按周期:")
        for cycle, count in cache_stats['by_cycle'].items():
            print(f"      {cycle}: {count} 个")
        print(f"   最新抓取时间: {cache_stats['latest_fetch']}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_video_cache())
