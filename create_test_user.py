#!/usr/bin/env python3
"""
创建测试用户脚本
用于API测试
"""
import sys
from sqlalchemy.orm import Session
from app.db import get_db
from app.db.models.user import User
from app.utils.security import get_password_hash

def create_test_user():
    """创建测试用户: test / test123"""
    db = next(get_db())

    try:
        # 检查测试用户是否已存在
        existing_user = db.query(User).filter_by(username='test').first()
        if existing_user:
            print("✓ 测试用户已存在")
            return True

        # 创建测试用户
        test_user = User(
            username='test',
            name='测试用户',
            password=get_password_hash('test123'),
            is_admin=True
        )

        db.add(test_user)
        db.commit()

        print("✓ 测试用户创建成功")
        print("  用户名: test")
        print("  密码: test123")
        return True

    except Exception as e:
        db.rollback()
        print(f"✗ 创建测试用户失败: {e}")
        return False
    finally:
        db.close()

if __name__ == '__main__':
    success = create_test_user()
    sys.exit(0 if success else 1)
