# Nginx配置要点

## 关键配置文件
- 位置：`/home/await/project/tissue/nginx/app.conf`

## 重要配置项
```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## 常见错误
- ❌ `proxy_pass http://127.0.0.1:8000/;` - 会截断API路径
- ✅ `proxy_pass http://127.0.0.1:8000/api/;` - 保持完整路径

## 测试方法
1. 检查nginx配置：`nginx -t`
2. 重启nginx服务
3. 测试API端点是否正常返回