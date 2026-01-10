from typing import List

from fastapi import APIRouter, Depends

from app.schema.r import R
from app.service.file import get_file_service

router = APIRouter()


@router.get("/")
def get_files(service=Depends(get_file_service)):
    return R.list(service.get_files())


@router.post("/batch/parse")
def batch_parse_files(paths: List[str], service=Depends(get_file_service)):
    """批量解析文件名中的番号信息"""
    return R.list(service.batch_parse_files(paths))
