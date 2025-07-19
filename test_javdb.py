import sys
sys.path.append('/home/await/project/tissue')

from app.utils.spider.javdb import JavDB

# 创建JavDB实例
javdb = JavDB()

# 测试无码排行榜数据提取
print("=== 测试无码排行榜数据提取 ===")
uncensored_videos = javdb.get_ranking_with_details('uncensored', 'daily', 1)
print(f"获取到 {len(uncensored_videos)} 个无码视频")

for i, video in enumerate(uncensored_videos[:3]):
    print(f"视频 {i+1}:")
    print(f"  番号: {video.get('num')}")
    print(f"  评分: {video.get('rating')}")
    print(f"  评论: {video.get('comments')}")
    print(f"  页面类型: {video.get('page_type')}")
    print()

print("=== 测试有码排行榜数据提取 ===")
censored_videos = javdb.get_ranking_with_details('censored', 'daily', 1)
print(f"获取到 {len(censored_videos)} 个有码视频")

for i, video in enumerate(censored_videos[:3]):
    print(f"视频 {i+1}:")
    print(f"  番号: {video.get('num')}")
    print(f"  评分: {video.get('rating')}")
    print(f"  评论: {video.get('comments')}")
    print(f"  页面类型: {video.get('page_type')}")
    print()
