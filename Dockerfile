FROM python:3.11.4-slim-bullseye
LABEL authors="Chris Chen"

ENV LANG="C.UTF-8" \
    TZ="Asia/Shanghai" \
    PUID=0 \
    PGID=0 \
    UMASK=000

# 更换为国内镜像源并安装依赖
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list \
    && sed -i 's/security.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list \
    && apt-get update -y \
    && apt-get -y install nginx locales gosu --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./nginx/ /etc/nginx/conf.d/
COPY . /app/

WORKDIR /app

# 创建必要的目录
RUN mkdir -p /app/dist \
    && echo '<!DOCTYPE html><html><head><meta charset="utf-8"><title>Tissue</title></head><body><h1>Tissue服务正在运行</h1><p>前端资源未构建，请查看文档进行构建。</p></body></html>' > /app/dist/index.html \
    && chown -R www-data /app/dist

# 安装后端依赖
RUN pip install -r requirements.txt \
    && locale-gen zh_CN.UTF-8 \
    && groupadd -r tissue -g 911 \
    && useradd -r tissue -g tissue -s /bin/bash -u 911 \
    && chmod +x /app/entrypoint

EXPOSE 9193
VOLUME [ "/app/config", "/app/dist" ]

ENTRYPOINT ["./entrypoint"]