FROM python:3.11.4-slim-bullseye
LABEL authors="Chris Chen"

ENV LANG="C.UTF-8" \
    TZ="Asia/Shanghai" \
    PUID=0 \
    PGID=0 \
    UMASK=000

# 安装依赖和Node.js
RUN apt-get update -y \
    && apt-get -y install nginx locales gosu curl gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g pnpm

COPY ./nginx/ /etc/nginx/conf.d/
COPY . /app/

WORKDIR /app

# 构建前端
RUN cd /app/frontend && pnpm install && pnpm run build \
    && mkdir -p /app/dist \
    && mv /app/frontend/dist/* /app/dist/ \
    && chown -R www-data /app/dist

# 安装后端依赖
RUN pip install -r requirements.txt \
    && locale-gen zh_CN.UTF-8 \
    && groupadd -r tissue -g 911 \
    && useradd -r tissue -g tissue -s /bin/bash -u 911 \
    && chmod +x /app/entrypoint

EXPOSE 9193
VOLUME [ "/app/config" ]

ENTRYPOINT ["./entrypoint"]