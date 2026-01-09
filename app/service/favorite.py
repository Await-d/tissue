"""
Author: Await
Date: 2026-01-09
Description: 收藏功能业务逻辑
"""
from typing import List, Optional
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db import get_db
from app.db.models.favorite import Favorite
from app.schema.favorite import FavoriteCreate, FavoriteResponse, FavoriteListResponse
from app.service.base import BaseService
from app.exception import BizException


class FavoriteService(BaseService):
    """收藏服务类"""

    def add_favorite(self, user_id: int, data: FavoriteCreate) -> FavoriteResponse:
        """添加收藏

        Args:
            user_id: 用户ID
            data: 收藏数据

        Returns:
            FavoriteResponse: 收藏响应

        Raises:
            BizException: 如果已经收藏过
        """
        try:
            favorite = Favorite(
                user_id=user_id,
                video_num=data.video_num,
                video_title=data.video_title,
                video_cover=data.video_cover
            )
            favorite.add(self.db)
            self.db.commit()
            self.db.refresh(favorite)
            return FavoriteResponse.model_validate(favorite)
        except IntegrityError:
            self.db.rollback()
            raise BizException("该视频已经收藏过了")

    def remove_favorite(self, user_id: int, video_num: str) -> bool:
        """取消收藏

        Args:
            user_id: 用户ID
            video_num: 视频番号

        Returns:
            bool: 是否成功删除
        """
        favorite = self.db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.video_num == video_num
        ).first()

        if not favorite:
            raise BizException("收藏不存在")

        favorite.delete(self.db)
        self.db.commit()
        return True

    def get_favorites(self, user_id: int, page: int = 1, size: int = 20) -> FavoriteListResponse:
        """获取收藏列表

        Args:
            user_id: 用户ID
            page: 页码
            size: 每页数量

        Returns:
            FavoriteListResponse: 收藏列表响应
        """
        # 计算偏移量
        offset = (page - 1) * size

        # 查询总数
        total = self.db.query(Favorite).filter(Favorite.user_id == user_id).count()

        # 查询列表
        favorites = self.db.query(Favorite).filter(
            Favorite.user_id == user_id
        ).order_by(
            Favorite.created_at.desc()
        ).offset(offset).limit(size).all()

        items = [FavoriteResponse.model_validate(f) for f in favorites]

        return FavoriteListResponse(
            items=items,
            total=total,
            page=page,
            size=size
        )

    def check_favorite(self, user_id: int, video_num: str) -> bool:
        """检查是否已收藏

        Args:
            user_id: 用户ID
            video_num: 视频番号

        Returns:
            bool: 是否已收藏
        """
        favorite = self.db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.video_num == video_num
        ).first()

        return favorite is not None

    def batch_add_favorites(self, user_id: int, video_nums: List[str]) -> dict:
        """批量添加收藏

        Args:
            user_id: 用户ID
            video_nums: 视频番号列表

        Returns:
            dict: 包含成功和失败数量的字典
        """
        success_count = 0
        failed_count = 0
        failed_nums = []

        for video_num in video_nums:
            try:
                favorite = Favorite(
                    user_id=user_id,
                    video_num=video_num
                )
                self.db.add(favorite)
                self.db.commit()  # 每个单独提交
                success_count += 1
            except IntegrityError:
                self.db.rollback()  # 只回滚当前这个
                failed_count += 1
                failed_nums.append(video_num)

        return {
            "success_count": success_count,
            "failed_count": failed_count,
            "failed_nums": failed_nums
        }

    def batch_remove_favorites(self, user_id: int, video_nums: List[str]) -> dict:
        """批量取消收藏

        Args:
            user_id: 用户ID
            video_nums: 视频番号列表

        Returns:
            dict: 包含成功和失败数量的字典
        """
        success_count = 0
        failed_nums = []

        for video_num in video_nums:
            favorite = self.db.query(Favorite).filter(
                Favorite.user_id == user_id,
                Favorite.video_num == video_num
            ).first()

            if favorite:
                self.db.delete(favorite)
                self.db.commit()  # 每个单独提交
                success_count += 1
            else:
                failed_nums.append(video_num)

        return {
            "success_count": success_count,
            "failed_count": len(failed_nums),
            "failed_nums": failed_nums
        }


def get_favorite_service(db: Session = Depends(get_db)):
    """获取收藏服务实例"""
    return FavoriteService(db)
