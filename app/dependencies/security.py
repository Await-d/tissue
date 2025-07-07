import jwt
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.db.models.user import User
from app.exception import AuthenticationException, AuthorizationException
from app.middleware.requestvars import g
from app.utils.security import oauth2_scheme, secret_key, algorithm


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id = int(payload['sub'])
        g().current_user_id = user_id
        return user_id
    except jwt.ExpiredSignatureError:
        raise AuthenticationException("Token已过期")
    except jwt.InvalidTokenError:
        raise AuthenticationException("无效的Token")
    except (ValueError, KeyError) as e:
        raise AuthenticationException("Token格式错误")
    except Exception as e:
        raise AuthenticationException("认证失败")


def get_current_user_id():
    g_obj = g()
    if not hasattr(g_obj, 'current_user_id') or g_obj.current_user_id is None:
        raise AuthenticationException("用户未认证")
    return g_obj.current_user_id


def get_current_user(db: Session = Depends(get_db)):
    user_id = get_current_user_id()  # 使用安全的获取方法
    user = User.get(db, user_id)
    if not user:
        raise AuthenticationException()
    return user


def get_current_admin_user(db: Session = Depends(get_db)) -> User | None:
    user_id = get_current_user_id()  # 使用安全的获取方法
    user = User.get(db, user_id)
    if not user:
        raise AuthenticationException()
    if user.is_admin:
        return user
    else:
        raise AuthorizationException()
