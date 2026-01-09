FROM python:3.11.8-slim
LABEL authors="Tissue-Plus Team"
LABEL maintainer="await2719"
LABEL description="Tissue-Plus: Your intelligent JAV library manager"

ENV LANG="C.UTF-8" \
    TZ="Asia/Shanghai" \
    PUID=0 \
    PGID=0 \
    UMASK=000

# 安装系统依赖
RUN apt-get update -y \
    && apt-get -y install nginx locales gosu \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制Nginx配置
COPY ./nginx/app.conf /etc/nginx/sites-available/default
RUN rm -f /etc/nginx/sites-enabled/default && ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default

# 复制所有文件（前端已在CI中构建好，dist/目录已存在）
COPY . /app/

# 安装Python依赖并配置权限
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt \
    && chown -R www-data /app/dist \
    && locale-gen zh_CN.UTF-8 \
    && groupadd -r tissue-plus -g 911 \
    && useradd -r tissue-plus -g tissue-plus -s /bin/bash -u 911 \
    && chmod +x /app/entrypoint \
    && chmod +x /app/startup_check.py \
    && chmod +x /app/start.sh

EXPOSE 9193
VOLUME [ "/app/config" ]

ENTRYPOINT ["./entrypoint"]