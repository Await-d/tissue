# 代码规范和约定

## 通用约定
- 项目使用中文注释，特别是文件头部的作者信息
- 文件头部包含：Author、Date、LastEditors、LastEditTime、Description
- 项目名称统一为 "Tissue-Plus"

## Python 后端规范
- 使用 Python 3.11.8
- 遵循 PEP 8 代码风格
- 使用 Type Hints 进行类型标注
- 使用 Pydantic 进行数据验证
- 文件结构按功能模块组织：
  - `app/api/`: API 路由
  - `app/service/`: 业务逻辑
  - `app/db/`: 数据库模型
  - `app/schema/`: 数据模式
  - `app/utils/`: 工具函数

## 前端规范
- 使用 TypeScript 而非 JavaScript
- 使用 React 函数组件和 Hooks
- 使用 Ant Design 组件库
- CSS 使用 Tailwind CSS 和 CSS Modules
- 文件命名使用 kebab-case
- 组件名使用 PascalCase

## ESLint 规则
- 基于 `eslint:recommended`
- 使用 `@typescript-eslint/recommended`
- 启用 `react-hooks/recommended`
- 启用 `react-refresh/only-export-components` 警告

## 数据库约定
- 使用 SQLAlchemy 2.0 语法
- 使用 Alembic 进行数据库迁移
- 模型类继承自 Base 类
- 使用中文注释描述表和字段含义

## 项目结构约定
- 前后端分离架构
- 使用 Docker 多阶段构建
- Nginx 作为反向代理
- 配置文件存储在 `/app/config` 目录