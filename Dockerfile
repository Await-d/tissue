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
    && apt-get -y install --no-install-recommends nginx locales gosu curl gnupg ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装Node.js (使用国内镜像)
RUN curl -fsSL https://npmmirror.com/mirrors/node/v18.18.2/node-v18.18.2-linux-x64.tar.gz -o /tmp/node.tar.gz \
    && mkdir -p /usr/local/lib/nodejs \
    && tar -xzf /tmp/node.tar.gz -C /usr/local/lib/nodejs \
    && mv /usr/local/lib/nodejs/node-v18.18.2-linux-x64 /usr/local/lib/nodejs/node \
    && ln -s /usr/local/lib/nodejs/node/bin/node /usr/bin/node \
    && ln -s /usr/local/lib/nodejs/node/bin/npm /usr/bin/npm \
    && ln -s /usr/local/lib/nodejs/node/bin/npx /usr/bin/npx \
    && rm /tmp/node.tar.gz \
    && npm config set registry https://registry.npmmirror.com \
    && npm install -g pnpm \
    && pnpm config set registry https://registry.npmmirror.com

COPY ./nginx/ /etc/nginx/conf.d/
COPY . /app/

WORKDIR /app

# 构建前端
RUN mkdir -p /app/dist \
    && cd /app/frontend \
    && pnpm install --network-timeout 100000 \
    && pnpm run build \
    && cp -r /app/frontend/dist/* /app/dist/ \
    && chown -R www-data /app/dist

# 安装后端依赖
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && locale-gen zh_CN.UTF-8 \
    && groupadd -r tissue -g 911 \
    && useradd -r tissue -g tissue -s /bin/bash -u 911 \
    && chmod +x /app/entrypoint

EXPOSE 9193
VOLUME [ "/app/config" ]

ENTRYPOINT ["./entrypoint"]