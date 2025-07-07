# 启动检查脚本使用说明

## 概述
`startup_check.py` 是一个用于检测和修复生产环境问题的自动化脚本，专门解决数据库迁移、枚举值格式等常见问题。

## 功能特性

### 🔍 检查项目
- **数据库连接**: 验证SQLite数据库是否可访问
- **迁移状态**: 检查Alembic迁移是否为最新版本
- **枚举值格式**: 检查time_range_type和status字段是否使用正确的小写格式
- **表结构**: 验证必需的基类字段(create_by, create_time, update_by, update_time)是否存在

### 🔧 自动修复
- 自动运行数据库迁移(`alembic upgrade head`)
- 修复枚举值大小写问题
- 添加缺失的表字段
- 生成详细的检查和修复报告

## 使用方法

### 本地开发环境
```bash
# 在项目根目录运行
python startup_check.py

# 或者使用可执行权限
./startup_check.py
```

### 生产环境(Docker)
```bash
# 复制脚本到容器
docker cp startup_check.py tissue_container:/app/

# 在容器内运行
docker exec -it tissue_container python /app/startup_check.py

# 或者直接运行
docker exec -it tissue_container /app/startup_check.py
```

### 生产环境(直接部署)
```bash
# 在项目目录运行
cd /path/to/tissue
python startup_check.py
```

## 输出说明

### 检查结果示例
```
==================================================
启动检查报告
==================================================

📊 检查结果:
  ✅ database_connection: 通过
  ✅ migration_status: 通过
  ✅ enum_values: 通过
  ✅ required_columns: 通过

📋 总结: 所有检查通过
```

### 问题发现示例
```
==================================================
启动检查报告
==================================================

📊 检查结果:
  ✅ database_connection: 通过
  ❌ migration_status: 失败
  ❌ enum_values: 失败
  ❌ required_columns: 失败

⚠️ 发现的问题:
  - 数据库迁移不是最新版本
  - 发现 5 条旧格式枚举值记录
  - 缺少必需的列: ['create_by', 'create_time']

🔧 应用的修复:
  - 数据库迁移修复成功

📋 总结: 存在问题需要手动处理
```

## 文件输出
- 检查报告自动保存到 `startup_check_report.txt`
- 日志信息实时显示在控制台

## 退出码
- `0`: 所有检查通过
- `1`: 存在问题需要处理

## 常见问题解决

### 1. 枚举值格式错误
**问题**: `'week' is not among the defined enum values`
**解决**: 脚本会自动运行迁移修复枚举值大小写

### 2. 缺少表字段
**问题**: 表结构不完整
**解决**: 脚本会自动添加缺失的基类字段

### 3. 迁移状态异常
**问题**: 数据库版本不匹配
**解决**: 自动运行`alembic upgrade head`

## 集成到部署流程

### 1. 启动脚本集成
```bash
#!/bin/bash
# 在应用启动前运行检查
python startup_check.py
if [ $? -ne 0 ]; then
    echo "启动检查失败，请检查日志"
    exit 1
fi

# 启动应用
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Docker集成
```dockerfile
# 在Dockerfile中添加
COPY startup_check.py /app/
RUN chmod +x /app/startup_check.py

# 在entrypoint中使用
ENTRYPOINT ["/app/startup_check.py && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

### 3. 定时检查
```bash
# 添加到crontab进行定期检查
0 2 * * * cd /path/to/tissue && python startup_check.py
```

## 注意事项
- 确保在项目根目录(包含alembic.ini)中运行
- 生产环境建议先备份数据库
- 脚本会自动修复常见问题，但复杂问题可能需要手动处理
- 检查日志文件以获取详细的错误信息