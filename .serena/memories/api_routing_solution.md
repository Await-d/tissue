# API请求路径问题解决方案

## 问题描述
生产环境中前端登录接口返回405 Not Allowed错误，API请求路径配置存在问题。

## 根本原因
nginx代理配置错误导致API路径被截断：
- 错误配置：`proxy_pass http://127.0.0.1:8000/;`
- 正确配置：`proxy_pass http://127.0.0.1:8000/api/;`

## 完整的API路由结构
1. **后端路由**：所有API都在`/api`前缀下注册
   - 文件：`app/main.py:43`
   - 配置：`app.include_router(api_router, prefix="/api")`
   
2. **前端配置**：
   - 开发环境：`BASE_API: "http://localhost:9193/api"`
   - 生产环境：`BASE_API: document.location.origin + '/api'`

3. **nginx配置**：
   - 位置：`nginx/app.conf`
   - 关键配置：`proxy_pass http://127.0.0.1:8000/api/;`

## 请求流程
前端请求 → nginx代理 → 后端API
- 前端：`/api/auth/login`
- nginx：转发到`http://127.0.0.1:8000/api/auth/login`
- 后端：处理`/api/auth/login`路径

## 修复步骤
1. 修复nginx配置文件中的proxy_pass设置
2. 确保前端配置正确包含`/api`前缀
3. 保持开发环境端口9193不变
4. 重新部署Docker容器应用修复