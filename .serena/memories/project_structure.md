# 项目结构

## 根目录结构
```
tissue/
├── app/                    # 后端应用程序
│   ├── api/               # API 路由
│   ├── db/                # 数据库相关
│   ├── service/           # 业务逻辑服务
│   ├── schema/            # 数据模式
│   ├── utils/             # 工具函数
│   ├── middleware/        # 中间件
│   ├── exception/         # 异常处理
│   ├── dependencies/      # 依赖注入
│   ├── main.py           # 应用入口
│   └── scheduler.py      # 任务调度器
├── frontend/              # 前端应用
│   ├── src/              # 源代码
│   ├── public/           # 静态资源
│   └── dist/             # 构建输出
├── alembic/              # 数据库迁移
├── nginx/                # Nginx 配置
├── .github/              # GitHub Actions
├── requirements.txt      # Python 依赖
├── Dockerfile           # Docker 构建文件
├── entrypoint          # 容器启动脚本
└── version.py          # 版本信息
```

## 后端应用结构
- `app/main.py`: FastAPI 应用入口
- `app/api/`: REST API 路由定义
- `app/service/`: 业务逻辑实现
- `app/db/models/`: 数据库模型
- `app/schema/`: Pydantic 数据模式
- `app/utils/`: 工具函数和帮助类
- `app/scheduler.py`: 后台任务调度

## 前端应用结构
- `frontend/src/routes/`: 页面路由组件
- `frontend/src/components/`: 可复用组件
- `frontend/src/apis/`: API 接口定义
- `frontend/src/utils/`: 工具函数
- `frontend/src/models/`: 数据模型和状态管理

## 配置和部署
- `Dockerfile`: 多阶段构建，包含前端构建和后端部署
- `nginx/`: Nginx 反向代理配置
- `alembic/`: 数据库迁移脚本
- `entrypoint`: 容器启动脚本