"""
数据类型转换工具
提供统一的数据类型转换方法
"""
from datetime import datetime, date
from typing import Any, Optional


class DataConverter:
    """数据转换工具类"""
    
    @staticmethod
    def to_float(value: Any, default: float = 0.0) -> float:
        """
        标准化为浮点数
        
        Args:
            value: 任意类型的值
            default: 转换失败时的默认值
            
        Returns:
            float: 转换后的浮点数
        """
        if value is None:
            return default
        
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        
        return default
    
    @staticmethod
    def to_int(value: Any, default: int = 0) -> int:
        """
        标准化为整数
        
        Args:
            value: 任意类型的值
            default: 转换失败时的默认值
            
        Returns:
            int: 转换后的整数
        """
        if value is None:
            return default
        
        if isinstance(value, (int, float)):
            return int(value)
        
        if isinstance(value, str):
            try:
                return int(value)
            except (ValueError, TypeError):
                return default
        
        return default
    
    @staticmethod
    def to_date(value: Any, date_format: str = "%Y-%m-%d") -> Optional[date]:
        """
        标准化为日期对象
        
        Args:
            value: 任意类型的值
            date_format: 日期格式字符串
            
        Returns:
            Optional[date]: 转换后的日期对象，失败返回None
        """
        if value is None:
            return None
        
        # 已经是 date 对象
        if isinstance(value, date):
            return value
        
        # datetime 对象转 date
        if isinstance(value, datetime):
            return value.date()
        
        # 字符串转 date
        if isinstance(value, str):
            try:
                return datetime.strptime(value, date_format).date()
            except (ValueError, TypeError):
                return None
        
        return None
    
    @staticmethod
    def normalize_rating(rating: Any) -> float:
        """
        标准化评分为浮点数（0.0-10.0）
        
        Args:
            rating: 评分值
            
        Returns:
            float: 标准化后的评分
        """
        score = DataConverter.to_float(rating, 0.0)
        # 确保评分在合理范围内
        return max(0.0, min(10.0, score))
    
    @staticmethod
    def normalize_comments_count(comments: Any) -> int:
        """
        标准化评论数为非负整数
        
        Args:
            comments: 评论数
            
        Returns:
            int: 标准化后的评论数
        """
        count = DataConverter.to_int(comments, 0)
        # 确保评论数为非负
        return max(0, count)
    
    @staticmethod
    def safe_divide(numerator: Any, denominator: Any, default: float = 0.0) -> float:
        """
        安全的除法运算
        
        Args:
            numerator: 分子
            denominator: 分母
            default: 除数为0时的默认值
            
        Returns:
            float: 计算结果
        """
        try:
            num = DataConverter.to_float(numerator)
            den = DataConverter.to_float(denominator)
            
            if den == 0:
                return default
            
            return num / den
        except (ValueError, TypeError, ZeroDivisionError):
            return default
