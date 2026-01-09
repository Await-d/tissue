"""
搜索建议和自动补全功能
提供智能的搜索建议，包括演员名称、番号、标签等
"""
import re
import jieba
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from difflib import SequenceMatcher

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_

from app.db.models import SearchSuggestion, SearchHistory, HotSearch
from app.service.video import VideoService
from app.utils.logger import logger


class SearchSuggestionService:
    """搜索建议服务"""

    def __init__(self, db: Session):
        self.db = db
        self.video_service = VideoService(db)

    def get_suggestions(self,
                       query: str,
                       limit: int = 10,
                       suggestion_types: List[str] = None) -> List[Dict[str, Any]]:
        """
        获取搜索建议

        Args:
            query: 搜索关键词
            limit: 建议数量
            suggestion_types: 建议类型列表

        Returns:
            建议列表
        """
        if not query.strip() or len(query) < 2:
            return []

        query = query.strip().lower()
        suggestions = []

        # 默认建议类型
        if suggestion_types is None:
            suggestion_types = ["actor", "num", "title", "tag", "series"]

        try:
            # 1. 从数据库中获取预建议
            db_suggestions = self._get_database_suggestions(query, limit // 2)
            suggestions.extend(db_suggestions)

            # 2. 动态生成建议
            if "actor" in suggestion_types:
                actor_suggestions = self._get_actor_suggestions(query, limit // 4)
                suggestions.extend(actor_suggestions)

            if "num" in suggestion_types:
                num_suggestions = self._get_num_suggestions(query, limit // 4)
                suggestions.extend(num_suggestions)

            if "title" in suggestion_types:
                title_suggestions = self._get_title_suggestions(query, limit // 4)
                suggestions.extend(title_suggestions)

            if "tag" in suggestion_types:
                tag_suggestions = self._get_tag_suggestions(query, limit // 4)
                suggestions.extend(tag_suggestions)

            if "series" in suggestion_types:
                series_suggestions = self._get_series_suggestions(query, limit // 4)
                suggestions.extend(series_suggestions)

            # 3. 搜索历史建议
            history_suggestions = self._get_history_suggestions(query, limit // 4)
            suggestions.extend(history_suggestions)

            # 4. 热门搜索建议
            hot_suggestions = self._get_hot_suggestions(query, limit // 4)
            suggestions.extend(hot_suggestions)

            # 去重和排序
            unique_suggestions = self._deduplicate_and_rank(suggestions, query)

            return unique_suggestions[:limit]

        except Exception as e:
            logger.error(f"获取搜索建议失败: {e}")
            return []

    def _get_database_suggestions(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """从数据库获取预建议"""
        try:
            suggestions = self.db.query(SearchSuggestion).filter(
                and_(
                    SearchSuggestion.query.ilike(f"%{query}%"),
                    SearchSuggestion.is_active == True
                )
            ).order_by(desc(SearchSuggestion.priority), desc(SearchSuggestion.click_count)).limit(limit).all()

            return [{
                "value": suggestion.suggestion,
                "type": suggestion.suggestion_type,
                "score": suggestion.priority + suggestion.click_count,
                "source": "database"
            } for suggestion in suggestions]

        except Exception as e:
            logger.warning(f"获取数据库建议失败: {e}")
            return []

    def _get_actor_suggestions(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """获取演员建议"""
        try:
            actors = self.video_service.get_all_actors()
            suggestions = []

            for actor in actors:
                if not actor.name:
                    continue

                # 计算相似度
                similarity = self._calculate_similarity(query, actor.name.lower())
                if similarity > 0.3:  # 相似度阈值
                    suggestions.append({
                        "value": actor.name,
                        "type": "actor",
                        "score": similarity,
                        "source": "local_actor"
                    })

            # 按相似度排序
            suggestions.sort(key=lambda x: x["score"], reverse=True)
            return suggestions[:limit]

        except Exception as e:
            logger.warning(f"获取演员建议失败: {e}")
            return []

    def _get_num_suggestions(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """获取番号建议"""
        try:
            videos = self.video_service.get_videos()
            suggestions = []

            # 番号匹配模式
            num_pattern = re.compile(r'^[A-Za-z]+-?\d*')

            for video in videos:
                if not video.num:
                    continue

                # 检查是否匹配番号模式
                if num_pattern.match(query.upper()):
                    if video.num.upper().startswith(query.upper()):
                        similarity = len(query) / len(video.num)
                        suggestions.append({
                            "value": video.num,
                            "type": "num",
                            "score": similarity,
                            "source": "local_video",
                            "extra": {"title": video.title}
                        })

            # 按相似度排序
            suggestions.sort(key=lambda x: x["score"], reverse=True)
            return suggestions[:limit]

        except Exception as e:
            logger.warning(f"获取番号建议失败: {e}")
            return []

    def _get_title_suggestions(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """获取标题建议"""
        try:
            videos = self.video_service.get_videos()
            suggestions = []

            for video in videos:
                if not video.title:
                    continue

                # 检查标题匹配
                if query in video.title.lower():
                    # 使用关键词匹配度
                    words = jieba.lcut(query)
                    title_words = jieba.lcut(video.title.lower())

                    match_count = sum(1 for word in words if word in title_words)
                    similarity = match_count / len(words) if words else 0

                    if similarity > 0.5:
                        suggestions.append({
                            "value": video.title,
                            "type": "title",
                            "score": similarity,
                            "source": "local_video",
                            "extra": {"num": video.num}
                        })

            # 按相似度排序
            suggestions.sort(key=lambda x: x["score"], reverse=True)
            return suggestions[:limit]

        except Exception as e:
            logger.warning(f"获取标题建议失败: {e}")
            return []

    def _get_tag_suggestions(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """获取标签建议"""
        try:
            # 这里需要从视频数据中提取标签
            # 由于标签可能存储在不同的字段中，需要具体实现
            return []

        except Exception as e:
            logger.warning(f"获取标签建议失败: {e}")
            return []

    def _get_series_suggestions(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """获取系列建议"""
        try:
            # 这里需要从视频数据中提取系列信息
            # 需要具体实现
            return []

        except Exception as e:
            logger.warning(f"获取系列建议失败: {e}")
            return []

    def _get_history_suggestions(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """获取历史搜索建议"""
        try:
            # 获取相似的历史搜索
            histories = self.db.query(SearchHistory.query, func.count(SearchHistory.id).label('count')).filter(
                SearchHistory.query.ilike(f"%{query}%")
            ).group_by(SearchHistory.query).order_by(desc('count')).limit(limit).all()

            suggestions = []
            for history in histories:
                similarity = self._calculate_similarity(query, history.query.lower())
                if similarity > 0.3:
                    suggestions.append({
                        "value": history.query,
                        "type": "history",
                        "score": similarity + (history.count * 0.1),  # 搜索次数加权
                        "source": "search_history",
                        "extra": {"count": history.count}
                    })

            return suggestions

        except Exception as e:
            logger.warning(f"获取历史建议失败: {e}")
            return []

    def _get_hot_suggestions(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """获取热门搜索建议"""
        try:
            hot_searches = self.db.query(HotSearch).filter(
                HotSearch.query.ilike(f"%{query}%")
            ).order_by(desc(HotSearch.trend_score)).limit(limit).all()

            suggestions = []
            for hot in hot_searches:
                similarity = self._calculate_similarity(query, hot.query.lower())
                if similarity > 0.3:
                    suggestions.append({
                        "value": hot.query,
                        "type": "hot",
                        "score": similarity + (hot.trend_score * 0.1),
                        "source": "hot_search",
                        "extra": {"search_count": hot.search_count}
                    })

            return suggestions

        except Exception as e:
            logger.warning(f"获取热门建议失败: {e}")
            return []

    def _calculate_similarity(self, query: str, target: str) -> float:
        """计算相似度"""
        try:
            # 使用多种相似度算法

            # 1. 序列匹配相似度
            seq_similarity = SequenceMatcher(None, query, target).ratio()

            # 2. 包含匹配
            contain_similarity = 0.0
            if query in target:
                contain_similarity = len(query) / len(target)

            # 3. 前缀匹配
            prefix_similarity = 0.0
            if target.startswith(query):
                prefix_similarity = len(query) / len(target)

            # 综合相似度
            final_similarity = max(seq_similarity, contain_similarity, prefix_similarity)

            return final_similarity

        except Exception as e:
            logger.warning(f"计算相似度失败: {e}")
            return 0.0

    def _deduplicate_and_rank(self, suggestions: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """去重和排序"""
        # 按value去重
        seen = set()
        unique_suggestions = []

        for suggestion in suggestions:
            value = suggestion["value"].lower()
            if value not in seen:
                seen.add(value)
                unique_suggestions.append(suggestion)

        # 按分数排序
        unique_suggestions.sort(key=lambda x: x["score"], reverse=True)

        return unique_suggestions

    def add_suggestion(self,
                      query: str,
                      suggestion: str,
                      suggestion_type: str,
                      priority: int = 1) -> bool:
        """添加建议"""
        try:
            # 检查是否已存在
            existing = self.db.query(SearchSuggestion).filter(
                and_(
                    SearchSuggestion.query == query,
                    SearchSuggestion.suggestion == suggestion
                )
            ).first()

            if existing:
                # 更新优先级
                existing.priority = max(existing.priority, priority)
                existing.updated_at = datetime.now()
            else:
                # 创建新建议
                new_suggestion = SearchSuggestion(
                    query=query,
                    suggestion=suggestion,
                    suggestion_type=suggestion_type,
                    priority=priority
                )
                self.db.add(new_suggestion)

            self.db.commit()
            return True

        except Exception as e:
            logger.error(f"添加建议失败: {e}")
            self.db.rollback()
            return False

    def update_suggestion_click(self, suggestion_id: int) -> bool:
        """更新建议点击次数"""
        try:
            suggestion = self.db.query(SearchSuggestion).filter(
                SearchSuggestion.id == suggestion_id
            ).first()

            if suggestion:
                suggestion.click_count += 1
                suggestion.updated_at = datetime.now()
                self.db.commit()
                return True

            return False

        except Exception as e:
            logger.error(f"更新建议点击失败: {e}")
            self.db.rollback()
            return False

    def build_suggestions_from_data(self) -> int:
        """从现有数据构建建议"""
        try:
            count = 0

            # 从演员构建建议
            actors = self.video_service.get_all_actors()
            for actor in actors:
                if actor.name and len(actor.name) >= 2:
                    # 为演员名称的前缀创建建议
                    for i in range(2, min(len(actor.name) + 1, 10)):
                        prefix = actor.name[:i]
                        if self.add_suggestion(prefix, actor.name, "actor", 2):
                            count += 1

            # 从番号构建建议
            videos = self.video_service.get_videos()
            for video in videos:
                if video.num and len(video.num) >= 3:
                    # 为番号的前缀创建建议
                    for i in range(3, min(len(video.num) + 1, 15)):
                        prefix = video.num[:i]
                        if self.add_suggestion(prefix, video.num, "num", 2):
                            count += 1

            logger.info(f"从现有数据构建建议完成，共创建 {count} 条建议")
            return count

        except Exception as e:
            logger.error(f"构建建议失败: {e}")
            return 0


def get_search_suggestion_service(db: Session) -> SearchSuggestionService:
    """获取搜索建议服务"""
    return SearchSuggestionService(db)