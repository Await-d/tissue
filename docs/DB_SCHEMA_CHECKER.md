# 数据库Schema自动检查和修复工具使用说明

## 概述

`db_schema_checker.py` 是一个自动检查和修复数据库schema的工具。它可以：

1. ✅ 自动检测SQLAlchemy models和实际数据库之间的差异
2. ✅ 自动发现缺失的表和字段
3. ✅ 自动添加缺失的字段（安全操作）
4. ✅ 生成详细的检查报告

## 使用方法

### 1. 只检查不修复

```bash
python db_schema_checker.py --check
```

这将检查数据库schema并生成报告，但不会修改数据库。

### 2. 检查并自动修复

```bash
python db_schema_checker.py --fix
```

这将检查数据库schema，发现缺失的字段后自动添加。

### 3. 模拟运行（Dry Run）

```bash
python db_schema_checker.py --dry-run
```

这将显示将要执行的SQL语句，但不会实际执行。适合用于预览修复操作。

### 4. 指定数据库URL

```bash
python db_schema_checker.py --fix --db-url sqlite:///path/to/your.db
```

## 集成到启动检查

`db_schema_checker.py` 已自动集成到 `startup_check.py` 中。

容器启动时会自动：
1. 检查数据库连接
2. 运行Alembic迁移
3. **检查数据库schema完整性** ⭐
4. **自动修复缺失的字段** ⭐
5. 生成启动检查报告

## 工作原理

### 检测逻辑

1. **读取Model定义**：从 `app/db/models/` 目录读取所有SQLAlchemy model
2. **读取数据库Schema**：使用SQLAlchemy Inspector读取实际数据库结构
3. **比较差异**：找出model中定义但数据库中不存在的表和字段

### 修复逻辑

对于缺失的字段，工具会：

1. 根据字段类型生成合适的 `ALTER TABLE ADD COLUMN` 语句
2. 为 `NOT NULL` 字段自动添加合理的默认值：
   - INTEGER → 0
   - BOOLEAN → 0
   - FLOAT/DECIMAL → 0.0
   - TEXT/VARCHAR → ''
   - DATETIME → CURRENT_TIMESTAMP
3. 安全地执行SQL语句
4. 记录所有修改到日志

## 安全性

✅ **安全操作**：
- ✅ 只添加字段（ADD COLUMN）
- ✅ 不会删除任何数据
- ✅ 不会修改现有字段
- ✅ 支持Dry Run模式预览操作

⚠️ **不支持的操作**：
- ❌ 不会自动创建新表（需要通过Alembic迁移）
- ❌ 不会修改字段类型
- ❌ 不会删除字段或表

## 升级场景

### 场景1：旧版本升级到新版本

当你从旧版本升级到新版本时：

1. 容器启动自动运行 `startup_check.py`
2. 如果发现model中新增了字段但数据库中不存在
3. 自动执行 `db_schema_checker.py --fix`
4. 添加所有缺失的字段
5. 应用正常启动

### 场景2：手动添加了新字段到Model

如果你在model中手动添加了新字段：

```python
# app/db/models/video.py
class Video(Base):
    __tablename__ = "video"

    # ...现有字段
    new_field = Column(String, nullable=True)  # 新增字段
```

运行：
```bash
python db_schema_checker.py --fix
```

字段会自动添加到数据库中，无需手动创建Alembic迁移。

### 场景3：开发环境同步

在团队开发中，如果团队成员A添加了新字段但忘记创建迁移：

团队成员B拉取代码后：
```bash
python db_schema_checker.py --check  # 发现差异
python db_schema_checker.py --fix    # 自动修复
```

## 报告说明

工具会生成两个报告文件：

1. **db_schema_check_report.txt**: Schema检查报告
2. **startup_check_report.txt**: 完整启动检查报告（如果通过startup_check.py运行）

### 报告示例

```
============================================================
数据库Schema检查报告
============================================================

⚠️ 发现的问题:
  - 表 actor_subscribe 缺失列: {'subscribed_works_count', 'works_count_updated_at'}
  - 表 subscribe 缺失列: {'update_time'}

🔧 应用的修复:
  - 添加列: actor_subscribe.subscribed_works_count
  - 添加列: actor_subscribe.works_count_updated_at
  - 添加列: subscribe.update_time
```

## 最佳实践

### 1. 升级前备份

虽然工具只执行安全操作，但建议升级前备份数据库：

```bash
cp app.db app.db.backup.$(date +%Y%m%d_%H%M%S)
```

### 2. 使用Dry Run预览

在生产环境修复前，先用Dry Run模式预览：

```bash
python db_schema_checker.py --dry-run
```

### 3. 定期检查

定期运行检查确保schema同步：

```bash
# 添加到crontab
0 2 * * * cd /app && python db_schema_checker.py --check >> /var/log/schema_check.log 2>&1
```

### 4. 集成到CI/CD

在CI/CD管道中添加schema检查：

```yaml
# .github/workflows/ci.yml
- name: Check Database Schema
  run: python db_schema_checker.py --check
```

## 故障排除

### 问题1：工具报错 "No module named 'app'"

**解决方案**：确保在项目根目录运行
```bash
cd /path/to/project
python db_schema_checker.py --check
```

### 问题2：字段添加失败

**可能原因**：
- 数据库文件权限问题
- 字段定义与数据库引擎不兼容

**解决方案**：
1. 检查数据库文件权限：`ls -la app.db`
2. 查看详细日志了解具体错误
3. 手动执行SQL语句进行修复

### 问题3：Dry Run显示的SQL不符合预期

**解决方案**：
这可能是model定义问题。检查：
1. 字段类型是否正确
2. nullable设置是否合理
3. 是否需要自定义默认值

## 技术细节

### 依赖

- SQLAlchemy >= 1.4
- Python >= 3.8

### 支持的数据库

当前版本针对SQLite优化，但理论上支持所有SQLAlchemy支持的数据库：
- ✅ SQLite
- ✅ PostgreSQL
- ✅ MySQL
- ✅ SQL Server

### 限制

1. **不处理复杂schema变更**：
   - 字段类型修改
   - 约束修改
   - 索引创建/删除
   这些操作应通过Alembic迁移处理

2. **仅添加字段**：
   工具设计为保守，只执行最安全的操作（添加字段）

3. **不处理数据迁移**：
   如果需要数据转换或迁移，应使用Alembic迁移脚本

## 与Alembic的关系

`db_schema_checker.py` 是Alembic的**补充工具**，不是替代品：

| 功能 | Alembic | db_schema_checker.py |
|------|---------|---------------------|
| 创建新表 | ✅ | ❌ |
| 添加新字段 | ✅ | ✅ |
| 修改字段类型 | ✅ | ❌ |
| 数据迁移 | ✅ | ❌ |
| 自动检测差异 | ❌ | ✅ |
| 自动修复 | ❌ | ✅ |
| 版本控制 | ✅ | ❌ |

**推荐工作流**：
1. 重大schema变更（新表、字段类型修改） → 使用Alembic
2. 简单字段添加 → 可以使用db_schema_checker.py快速修复
3. 升级时自动检查和修复 → 集成到startup_check.py

## 更新日志

### v1.0.0 (2025-11-13)
- ✨ 初始版本发布
- ✅ 支持自动检测缺失字段
- ✅ 支持自动添加字段
- ✅ 集成到startup_check.py
- ✅ 支持Dry Run模式
- ✅ 生成详细报告

---

如有问题或建议，请提交Issue或Pull Request。
