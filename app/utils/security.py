from datetime import datetime, timedelta
from typing import Any, Union
import warnings

import jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

# 抑制bcrypt版本兼容性警告
warnings.filterwarnings("ignore", message=".*error reading bcrypt version.*")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/auth/login")

# 配置密码上下文，使用bcrypt并抑制版本检查
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    # 添加bcrypt配置以避免版本检查问题
    bcrypt__min_rounds=12,
    bcrypt__max_rounds=16,
    bcrypt__default_rounds=12
)
secret_key = "ULDFZslsFEzL2pSm"
algorithm = "HS256"


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: Union[str, Any]) -> str:
    expire = datetime.now() + timedelta(minutes=60 * 24 * 8)
    payload = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(payload, secret_key, algorithm=algorithm)
    return encoded_jwt
