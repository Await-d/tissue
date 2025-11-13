# 快速部署指南

## 🚀 5 分钟快速部署

### 1. 数据库迁移

```bash
docker-compose exec backend python << 'EOF'
from sqlalchemy import text
from app.db import SessionFactory

with SessionFactory() as db:
    try:
        db.execute(text("""
            ALTER TABLE actor_subscribe 
            ADD COLUMN IF NOT EXISTS subscribed_works_count INTEGER DEFAULT 0,
            ADD COLUMN IF NOT EXISTS works_count_updated_at DATETIME
        """))
        db.commit()
        print("✅ 迁移完成")
    except:
        print("✅ 字段已存在")
EOF
```

### 2. 重启服务

```bash
docker-compose restart backend
```

### 3. 验证部署

```bash
# 检查服务状态
docker-compose ps backend

# 查看日志
docker-compose logs --tail=20 backend
```

### 4. 测试功能

- 访问演员订阅列表（应该快速加载）
- 创建新的订阅下载（检查日志中的过滤信息）

---

## 完成！

所有修复已部署并生效。
