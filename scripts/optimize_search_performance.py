#!/usr/bin/env python3
"""
数据库搜索性能优化脚本
创建搜索相关的索引，优化查询性能
"""
import os
import sys
import sqlite3
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.utils.logger import logger
from app.db import get_session
from sqlalchemy import text


def create_search_indexes():
    """创建搜索相关的数据库索引"""

    # 获取数据库会话
    session = get_session()

    try:
        # 搜索历史表索引
        search_history_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_search_history_query ON search_history(query)",
            "CREATE INDEX IF NOT EXISTS idx_search_history_type ON search_history(search_type)",
            "CREATE INDEX IF NOT EXISTS idx_search_history_created_at ON search_history(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_search_history_query_type ON search_history(query, search_type)",
            "CREATE INDEX IF NOT EXISTS idx_search_history_user_ip ON search_history(user_ip)",
        ]

        # 搜索统计表索引
        search_statistics_indexes = [
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_search_stats_date_query ON search_statistics(date, query)",
            "CREATE INDEX IF NOT EXISTS idx_search_stats_date ON search_statistics(date)",
            "CREATE INDEX IF NOT EXISTS idx_search_stats_query ON search_statistics(query)",
            "CREATE INDEX IF NOT EXISTS idx_search_stats_count ON search_statistics(search_count)",
        ]

        # 热门搜索表索引
        hot_searches_indexes = [
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_hot_searches_query ON hot_searches(query)",
            "CREATE INDEX IF NOT EXISTS idx_hot_searches_count ON hot_searches(search_count)",
            "CREATE INDEX IF NOT EXISTS idx_hot_searches_daily ON hot_searches(daily_count)",
            "CREATE INDEX IF NOT EXISTS idx_hot_searches_weekly ON hot_searches(weekly_count)",
            "CREATE INDEX IF NOT EXISTS idx_hot_searches_monthly ON hot_searches(monthly_count)",
            "CREATE INDEX IF NOT EXISTS idx_hot_searches_trend ON hot_searches(trend_score)",
            "CREATE INDEX IF NOT EXISTS idx_hot_searches_last_search ON hot_searches(last_search_at)",
        ]

        # 搜索建议表索引
        search_suggestions_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_search_suggestions_query ON search_suggestions(query)",
            "CREATE INDEX IF NOT EXISTS idx_search_suggestions_type ON search_suggestions(suggestion_type)",
            "CREATE INDEX IF NOT EXISTS idx_search_suggestions_priority ON search_suggestions(priority)",
            "CREATE INDEX IF NOT EXISTS idx_search_suggestions_active ON search_suggestions(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_search_suggestions_click_count ON search_suggestions(click_count)",
        ]

        # 搜索缓存表索引
        search_cache_indexes = [
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_search_cache_key ON search_cache(cache_key)",
            "CREATE INDEX IF NOT EXISTS idx_search_cache_query ON search_cache(query)",
            "CREATE INDEX IF NOT EXISTS idx_search_cache_expires ON search_cache(expires_at)",
            "CREATE INDEX IF NOT EXISTS idx_search_cache_created ON search_cache(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_search_cache_hit_count ON search_cache(hit_count)",
        ]

        # 历史表相关索引（用于搜索功能）
        history_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_history_num ON history(num)",
            "CREATE INDEX IF NOT EXISTS idx_history_status ON history(status)",
            "CREATE INDEX IF NOT EXISTS idx_history_is_zh ON history(is_zh)",
            "CREATE INDEX IF NOT EXISTS idx_history_is_uncensored ON history(is_uncensored)",
            "CREATE INDEX IF NOT EXISTS idx_history_create_time ON history(create_time)",
        ]

        # 订阅表相关索引
        subscribe_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_subscribe_keywords ON subscribe(keywords)",
            "CREATE INDEX IF NOT EXISTS idx_subscribe_status ON subscribe(status)",
            "CREATE INDEX IF NOT EXISTS idx_subscribe_enable ON subscribe(enable)",
            "CREATE INDEX IF NOT EXISTS idx_subscribe_create_time ON subscribe(create_time)",
        ]

        # 种子表相关索引
        torrent_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_torrent_name ON torrent(name)",
            "CREATE INDEX IF NOT EXISTS idx_torrent_num ON torrent(num)",
            "CREATE INDEX IF NOT EXISTS idx_torrent_is_zh ON torrent(is_zh)",
            "CREATE INDEX IF NOT EXISTS idx_torrent_is_uncensored ON torrent(is_uncensored)",
            "CREATE INDEX IF NOT EXISTS idx_torrent_is_hd ON torrent(is_hd)",
            "CREATE INDEX IF NOT EXISTS idx_torrent_website ON torrent(website)",
            "CREATE INDEX IF NOT EXISTS idx_torrent_publish_date ON torrent(publish_date)",
        ]

        # 全文搜索索引（SQLite FTS5）
        fts_indexes = [
            """CREATE VIRTUAL TABLE IF NOT EXISTS torrent_fts USING fts5(
                name, num, actors, tags, studio, publisher,
                content='torrent', content_rowid='id'
            )""",
            """CREATE TRIGGER IF NOT EXISTS torrent_fts_insert AFTER INSERT ON torrent BEGIN
                INSERT INTO torrent_fts(rowid, name, num, actors, tags, studio, publisher)
                VALUES (new.id, new.name, new.num, new.actors, new.tags, new.studio, new.publisher);
            END""",
            """CREATE TRIGGER IF NOT EXISTS torrent_fts_delete AFTER DELETE ON torrent BEGIN
                INSERT INTO torrent_fts(torrent_fts, rowid, name, num, actors, tags, studio, publisher)
                VALUES('delete', old.id, old.name, old.num, old.actors, old.tags, old.studio, old.publisher);
            END""",
            """CREATE TRIGGER IF NOT EXISTS torrent_fts_update AFTER UPDATE ON torrent BEGIN
                INSERT INTO torrent_fts(torrent_fts, rowid, name, num, actors, tags, studio, publisher)
                VALUES('delete', old.id, old.name, old.num, old.actors, old.tags, old.studio, old.publisher);
                INSERT INTO torrent_fts(rowid, name, num, actors, tags, studio, publisher)
                VALUES (new.id, new.name, new.num, new.actors, new.tags, new.studio, new.publisher);
            END"""
        ]

        # 执行所有索引创建
        all_indexes = (
            search_history_indexes +
            search_statistics_indexes +
            hot_searches_indexes +
            search_suggestions_indexes +
            search_cache_indexes +
            history_indexes +
            subscribe_indexes +
            torrent_indexes +
            fts_indexes
        )

        logger.info("开始创建搜索性能优化索引...")

        for idx, sql in enumerate(all_indexes, 1):
            try:
                session.execute(text(sql))
                logger.info(f"[{idx}/{len(all_indexes)}] 创建索引成功: {sql[:50]}...")
            except Exception as e:
                logger.warning(f"[{idx}/{len(all_indexes)}] 创建索引失败: {e}")
                continue

        session.commit()
        logger.info("搜索性能优化索引创建完成！")

    except Exception as e:
        logger.error(f"创建索引时发生错误: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def analyze_search_performance():
    """分析搜索性能"""

    session = get_session()

    try:
        # 分析表大小和索引使用情况
        performance_queries = [
            "SELECT name, sql FROM sqlite_master WHERE type='index' AND name LIKE '%search%'",
            "SELECT name, sql FROM sqlite_master WHERE type='index' AND name LIKE '%torrent%'",
            "SELECT name, sql FROM sqlite_master WHERE type='index' AND name LIKE '%history%'",
            "SELECT COUNT(*) as torrent_count FROM torrent",
            "SELECT COUNT(*) as history_count FROM history",
            "SELECT COUNT(*) as subscribe_count FROM subscribe",
        ]

        logger.info("=== 搜索性能分析报告 ===")

        for query in performance_queries:
            try:
                result = session.execute(text(query)).fetchall()
                logger.info(f"查询: {query}")
                for row in result:
                    logger.info(f"结果: {row}")
                logger.info("-" * 50)
            except Exception as e:
                logger.warning(f"分析查询失败: {e}")

        # 检查是否存在全文搜索表
        fts_check = session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='torrent_fts'")
        ).fetchone()

        if fts_check:
            fts_count = session.execute(text("SELECT COUNT(*) FROM torrent_fts")).fetchone()
            logger.info(f"全文搜索表记录数: {fts_count[0] if fts_count else 0}")
        else:
            logger.warning("全文搜索表不存在，建议创建以提升搜索性能")

    except Exception as e:
        logger.error(f"性能分析时发生错误: {e}")
    finally:
        session.close()


def optimize_search_queries():
    """优化搜索查询"""

    session = get_session()

    try:
        # 更新表统计信息
        optimize_queries = [
            "ANALYZE",  # 更新SQLite查询计划器统计信息
            "PRAGMA optimize",  # 自动优化
            "VACUUM",  # 重建数据库文件
        ]

        logger.info("开始优化搜索查询...")

        for query in optimize_queries:
            try:
                logger.info(f"执行优化: {query}")
                session.execute(text(query))
                logger.info(f"优化完成: {query}")
            except Exception as e:
                logger.warning(f"优化失败: {e}")

        session.commit()
        logger.info("搜索查询优化完成！")

    except Exception as e:
        logger.error(f"查询优化时发生错误: {e}")
    finally:
        session.close()


def main():
    """主函数"""
    print("搜索性能优化工具")
    print("=" * 50)

    try:
        # 创建索引
        create_search_indexes()

        # 分析性能
        analyze_search_performance()

        # 优化查询
        optimize_search_queries()

        print("\n✅ 搜索性能优化完成！")
        print("\n优化内容包括:")
        print("1. 创建搜索相关数据库索引")
        print("2. 建立全文搜索索引(FTS5)")
        print("3. 优化查询计划器统计信息")
        print("4. 数据库文件优化")

    except Exception as e:
        print(f"\n❌ 优化过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()