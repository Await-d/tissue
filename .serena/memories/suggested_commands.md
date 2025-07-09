# 推荐的开发命令

## 前端开发命令
```bash
# 进入前端目录
cd frontend/

# 安装依赖
npm install

# 开发模式启动（热重载）
npm run dev

# 构建生产版本
npm run build

# 代码检查
npm run lint

# 预览构建结果
npm run preview
```

## 后端开发命令
```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 运行后端开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 9193

# 数据库迁移
alembic upgrade head

# 生成新的数据库迁移
alembic revision --autogenerate -m "描述"

# 查看迁移历史
alembic history
```

## Docker 命令
```bash
# 构建 Docker 镜像
docker build -t tissue-plus .

# 运行容器
docker run -d --name tissue-plus -p 9193:9193 tissue-plus

# 查看容器日志
docker logs tissue-plus

# 进入容器
docker exec -it tissue-plus bash
```

## 通用开发命令
```bash
# 查看项目状态
git status

# 提交代码
git add .
git commit -m "feat: 添加新功能"

# 推送代码
git push origin main

# 查看端口占用
netstat -tlnp | grep :9193

# 查看进程
ps aux | grep uvicorn
```

## 系统工具命令（Linux）
```bash
# 文件操作
ls -la          # 详细列表
find . -name "*.py"  # 查找文件
grep -r "搜索内容" . # 搜索文件内容

# 网络
curl -X GET http://localhost:9193/api/health  # 测试API
wget https://example.com/file.txt             # 下载文件

# 系统信息
df -h           # 磁盘空间
free -h         # 内存使用
htop            # 进程监控
```

## 调试命令
```bash
# 查看 Python 错误
python -c "import app.main"

# 检查端口
lsof -i :9193

# 查看 Nginx 状态
nginx -t        # 测试配置
nginx -s reload # 重载配置
```