FROM python:3.11.8-slim
LABEL authors="Tissue-Plus Team"

ENV LANG="C.UTF-8" \
    TZ="Asia/Shanghai" \
    PUID=0 \
    PGID=0 \
    UMASK=000

# 安装Node.js和前端构建所需的工具（使用18.19版本与原版一致）
RUN apt-get update -y \
    && apt-get -y install nginx locales gosu curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm --version

# 复制Nginx配置
COPY ./nginx/ /etc/nginx/conf.d/

# 首先只复制前端部分，提高缓存利用率
COPY ./frontend /app/frontend/

# 构建前端（与GitHub Actions保持一致）
WORKDIR /app/frontend
RUN npm install && CI=false npm run build

# 复制剩余文件
COPY . /app/

# 创建dist目录并复制前端构建文件
WORKDIR /app
RUN mkdir -p /app/dist \
    && cp -r /app/frontend/dist/* /app/dist/ \
    && pip install -r requirements.txt \
    && chown -R www-data /app/dist \
    && locale-gen zh_CN.UTF-8 \
    && groupadd -r tissue-plus -g 911 \
    && useradd -r tissue-plus -g tissue-plus -s /bin/bash -u 911 \
    && chmod +x /app/entrypoint

EXPOSE 9193
VOLUME [ "/app/config" ]

ENTRYPOINT ["./entrypoint"]