'''
Author: Await
Date: 2025-05-24 17:05:38
LastEditors: Await
LastEditTime: 2025-05-27 14:34:00
Description: 请填写简介
'''
from typing import Any, TypeVar, Generic, List, Union, Optional
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

from pydantic import BaseModel

DataT = TypeVar("DataT")


class Response(BaseModel, Generic[DataT]):
    success: bool = True
    details: Optional[str] = None
    data: Optional[DataT] = None
    total: Optional[int] = None


class R(Response):

    @classmethod
    def ok(cls, data: Optional[DataT] = None, message: Optional[str] = None) -> Self:
        return R(success=True, details=message, data=data)

    @classmethod
    def list(cls, data: DataT, total: Optional[int] = None, message: Optional[str] = None) -> Response:
        return R(success=True, details=message, data=data, total=total)

    @classmethod
    def fail(cls, message: Optional[str] = None, data: Optional[DataT] = None) -> Self:
        return R(success=False, details=message, data=data)
