"""数据库模型枚举定义

此模块定义了数据库模型中使用的枚举类型，用于替代魔法数字，提高代码可读性和可维护性。
"""

from enum import IntEnum


class SubscribeStatus(IntEnum):
    """订阅状态枚举

    用于 Subscribe 模型的 status 字段。
    """
    PENDING = 1  # 待处理/进行中
    COMPLETED = 2  # 已完成


class HistoryStatus(IntEnum):
    """历史记录状态枚举

    用于 History 模型的 status 字段。
    """
    SUCCESS = 1  # 成功
    FAILED = 0  # 失败（预留）
