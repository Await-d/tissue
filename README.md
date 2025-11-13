<!--
 * @Author: Await
 * @Date: 2025-05-24 17:05:38
 * @LastEditors: Await
 * @LastEditTime: 2025-05-27 04:30:00
 * @Description: Tissue-Plus 项目，您的智能教材管家！
-->
# Tissue-Plus ✨

![GitHub License](https://img.shields.io/github/license/Await-d/tissue)
![Docker Image Version](https://img.shields.io/docker/v/await2719/tissue-plus/latest)
![Docker Image Size](https://img.shields.io/docker/image-size/await2719/tissue-plus/latest)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/Await-d/tissue/auto-release-pipeline.yml)

**Tissue-Plus：您的智能教材管家，让学习资料整理从未如此轻松高效！** 📚🚀

还在为散落各处的学习视频、文档、笔记而烦恼吗？Tissue-Plus 专为解决这一痛点而生！它不仅能帮您**智能刮削教材信息**，自动下载精美海报、匹配元数据，还能将您的所有学习资料在 Jellyfin、Emby、Kodi 等媒体服务器中**优雅地装订成册**，如同拥有一个私人定制的数字图书馆。

> 本项目基于备受好评的 [chris-2s/tissue](https://github.com/chris-2s/tissue) 项目深度进化，感谢原作者的卓越贡献！我们在此基础上，注入了更多强大、便捷的功能，致力于打造终极学习资料管理体验。

[效果图传送阵](#talk-is-cheap-show-me-the-view) | [版本更新记录](CHANGELOG.md) | [点我看前端日志效果](#前端日志展示)

## 🌟 Tissue-Plus 核心亮点

* **🎬 智能元数据刮削**：告别手动整理！自动识别视频文件，从各大知名站点（JavBus, JavDB等）拉取封面、演员、标签、发行日期等详细信息。
* **🖼️ 精美海报生成**：让您的媒体库焕然一新！自动下载高清海报，影片信息一目了然。
* **👤 演员订阅系统**：再也不会错过老师的新作品！一键订阅您关注的演员，新教材发布自动提醒并下载。
  * **智能筛选**：支持按高清、中文字幕、无码等偏好筛选资源。
  * **关键字过滤** ⭐：支持包含/排除关键字，精准控制订阅内容（如只下载单体作品、排除VR等）。
  * **订阅历史** ⭐：查看已完成的订阅记录，支持快速重新订阅。
  * **状态管理**：轻松暂停或恢复演员订阅，灵活控制下载。
  * **资源清理**：取消订阅时可选择是否一并删除已下载的视频和种子文件。
* **🔗 qBittorrent 深度集成**：无缝对接qBittorrent下载器，实现从订阅到下载的全自动化流程。
* **🚀 高效任务调度**：定时检查演员更新、自动刮削新入库文件，无需人工干预。
* **🌐 Web用户界面**：现代化、响应式的Web界面，随时随地轻松管理您的教材库。
* **🎯 智能下载过滤**：全新的种子文件过滤系统，智能识别文件类型，按需下载！
  * **媒体文件模式**：只保留视频和字幕文件，过滤无用内容。
  * **大小智能过滤**：设置文件大小范围，避免下载超大或过小文件。
  * **样本文件识别**：自动跳过sample、preview等样本文件。
  * **实时测试**：输入磁力链接即可预览过滤效果。
* **🔍 搜索历史功能** ⭐：自动保存最近10次番号搜索记录，快速重复查询，提升使用效率。
* **🔒 安全性增强** ⭐：Token有效期优化（30天）、正则表达式注入防护、数据库事务回滚保护。
* **🐳 Docker一键部署**：极简部署流程，三分钟即可拥有您的专属教材管家。
* **🛡️ SSL连接优化**：内置重试与容错机制，确保网络请求稳定可靠。
* **🔔 实时通知系统**：支持Telegram、Webhook等多种通知方式，新资源入库、下载完成即时掌握。

## ⚠️ 重要提示

* 🌐 **科学的上网环境**是顺畅使用本项目的基石，请务必确保网络通畅。
* 🚧 本项目仍处于快速迭代阶段，虽然我们努力确保稳定，但仍建议您**定期备份数据**，以防万一。
* 🐞 部分非Tissue-Plus生成的NFO文件可能存在兼容性问题，我们正在持续改进。
* 🤫 为了项目的健康发展，请**避免在国内公开平台讨论本项目**，感谢您的理解与配合。

## 🚀 快速开始：Docker部署

最简单快捷的部署方式，三分钟拥有您的专属教材管家！

### 获取镜像

**官方镜像地址**：[Docker Hub - await2719/tissue-plus](https://hub.docker.com/r/await2719/tissue-plus)

```bash
# 拉取最新版本
docker pull await2719/tissue-plus:latest

# 或拉取指定版本（推荐）
docker pull await2719/tissue-plus:v0.1.4
```

### Docker Run 方式部署

直接运行以下命令 (请根据您的实际环境修改路径和端口):

```bash
docker run \
  -d \
  --name=tissue-plus \
  --restart=unless-stopped \
  -e TZ="Asia/Shanghai" \
  -p 9193:9193 \
  -v /path/to/config:/app/config \
  -v /path/to/video:/data/video \
  -v /path/to/downloads:/downloads \
  await2719/tissue-plus:latest
```

### Docker Compose 方式部署（推荐）

创建 `docker-compose.yml` 文件：

```yaml
version: '3.8'

services:
  tissue-plus:
    image: await2719/tissue-plus:latest
    container_name: tissue-plus
    restart: unless-stopped
    environment:
      - TZ=Asia/Shanghai
      - PUID=1000      # 可选：运行用户ID
      - PGID=1000      # 可选：运行组ID
    ports:
      - "9193:9193"
    volumes:
      - ./config:/app/config                    # 配置文件存储
      - /path/to/your/video:/data/video         # 媒体库路径
      - /path/to/qb/downloads:/downloads        # qBittorrent下载路径
      # - /path/to/pending:/data/file           # 可选：待处理文件路径
    networks:
      - tissue-network

networks:
  tissue-network:
    driver: bridge
```

启动服务：

```bash
# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f tissue-plus

# 停止
docker-compose down
```

### Docker 环境变量 (可选)

| 变量  | 说明           | 是否必填 | 默认值 |
|-------|----------------|----------|--------|
| PUID  | 程序运行用户ID   | 否       | 0      |
| PGID  | 程序运行用户组ID | 否       | 0      |
| UMASK | 文件权限掩码     | 否       | 000    |

### 端口映射

* `9193:9193`：Web界面访问端口。项目采用前后端分离架构，Nginx已内置反向代理，直接访问此端口即可。

### 路径映射详解

合理的路径映射是流畅使用的关键：

| 宿主机路径示例         | 容器内对应路径 | 说明                                                                                                                                                                                             |
|------------------------|----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/your/media/library`  | `/data/video`  | **媒体库路径**：Tissue-Plus会自动扫描此路径下的视频文件进行刮削和管理。                                                                                                                                    |
| `/your/pending/files`  | `/data/file`   | **文件监控路径 (可选)**：未来规划功能，用于自动处理新文件。当前可用于非qBittorrent下载器的场景，将其他下载工具的完成目录映射于此，配合手动导入或未来功能使用。                                                                  |
| `/your/qb/downloads`   | `/downloads`   | **qBittorrent下载路径**：**至关重要！** 请确保此路径与您qBittorrent中设置的"默认保存路径"或分类保存路径的**根目录**一致。如果qBittorrent内的路径与系统实际路径不符（例如Docker内的QB），请在Tissue-Plus设置页面正确配置"下载器路径映射"。 |

## 🎯 使用指南

### 首次启动

1. **访问 Web 界面**：浏览器打开 `http://your-server-ip:9193`
2. **默认登录凭据**：
   - 用户名：`admin`
   - 密码：`password`
   - ⚠️ 首次登录后请立即修改密码！

### 基础配置

#### 1. qBittorrent 连接配置

进入 **设置 → 下载器设置**：

```
qBittorrent 地址: http://your-qb-host:8080
用户名: your-qb-username
密码: your-qb-password
```

#### 2. 路径映射配置

确保以下路径配置正确：

| 配置项 | 说明 | 示例 |
|--------|------|------|
| 媒体库路径 | 刮削后文件的存放位置 | `/data/video` |
| 下载完成路径 | qBittorrent 下载完成的路径 | `/downloads` |
| 路径映射 | qB内路径到实际路径的映射 | `/downloads` → `/downloads` |

#### 3. 刮削源配置

支持多个数据源，可在设置中配置：
- JavBus
- JavDB
- 其他自定义源

### 演员订阅功能

1. **添加订阅**：
   - 进入 **演员管理** 页面
   - 点击 **添加订阅**
   - 输入演员名称或代码
   - 设置筛选条件（高清、字幕、无码等）
   - **关键字过滤** ⭐：
     - **包含关键字**：只下载标题包含指定关键字的影片（如"单体"）
     - **排除关键字**：排除标题包含指定关键字的影片（如"VR|精选"，用`|`分隔多个）
     - 支持正则表达式，实现复杂过滤规则

2. **管理订阅**：
   - 暂停/恢复订阅
   - 修改筛选条件和关键字过滤
   - 查看订阅状态和历史
   - **订阅历史** ⭐：查看已完成的订阅，一键重新订阅

3. **自动下载**：
   - 系统定时检查新作品
   - 符合条件的资源自动下载
   - 下载完成后自动刮削

### 番号搜索功能 ⭐

- **自动记录历史**：最近10次搜索自动保存
- **快速重复查询**：点击历史记录即可快速搜索
- **搜索优化**：记住上次搜索的番号，刷新页面自动恢复

### 关于文件转移

* Tissue-Plus支持**复制**和**移动**两种方式将刮削整理好的文件放入媒体库。
* **注意**：当使用"移动"模式时，如果您的Docker路径映射横跨了不同的宿主机挂载点（即使它们在同一物理磁盘上），Docker的行为可能类似于跨磁盘移动，导致无法实现"秒传"效果。为了最佳性能，建议将源路径和目标路径设置在同一个宿主机挂载卷内，或者将它们的共同父目录映射到容器中。

## 🔧 故障排除

### 常见问题

#### 1. 无法连接到 qBittorrent

**症状**：设置页面显示连接失败

**解决方案**：
```bash
# 检查 qBittorrent 是否运行
docker ps | grep qbittorrent

# 检查网络连通性
docker exec tissue-plus ping qbittorrent-container

# 确认 qBittorrent Web UI 设置
# 进入 qBittorrent 设置 → Web UI → 允许远程连接
```

#### 2. 路径映射问题

**症状**：下载的文件找不到或刮削失败

**解决方案**：
1. 确保 Docker 容器路径映射正确
2. 检查文件权限（PUID/PGID 设置）
3. 验证 qBittorrent 内部路径与实际路径一致

#### 3. 刮削失败

**症状**：无法获取元数据或封面

**解决方案**：
1. 检查网络连接（科学上网）
2. 更换刮削源站点
3. 检查防火墙设置

### 日志查看

```bash
# 查看容器日志
docker logs tissue-plus

# 实时查看日志
docker logs -f tissue-plus

# Docker Compose 方式
docker-compose logs -f tissue-plus
```

### 性能优化

#### 1. 内存优化

```yaml
# docker-compose.yml 中添加内存限制
services:
  tissue-plus:
    # ... 其他配置
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

#### 2. 存储优化

- 使用 SSD 存储提升刮削速度
- 合理设置缓存大小
- 定期清理无用数据

## 🔄 版本更新

### 自动更新（推荐）

使用 Watchtower 自动更新：

```yaml
version: '3.8'
services:
  watchtower:
    image: containrrr/watchtower
    container_name: watchtower
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - WATCHTOWER_CLEANUP=true
      - WATCHTOWER_POLL_INTERVAL=86400  # 24小时检查一次
    command: tissue-plus  # 只监控 tissue-plus 容器
```

### 手动更新

```bash
# Docker Run 方式
docker stop tissue-plus
docker rm tissue-plus
docker pull await2719/tissue-plus:latest
# 重新运行容器...

# Docker Compose 方式
docker-compose pull
docker-compose up -d
```

## ✨ 前端日志展示

一个美观且信息丰富的前端界面，让您对系统状态一目了然！

<!-- 在下方粘贴您的前端日志截图 -->
<!-- 例如: ![前端日志截图](https://example.com/your-frontend-log-screenshot.png) -->

```
[您的前端日志截图展示区域]

您可以在这里简单描述一下截图内容，例如：
- 实时任务状态监控
- 清晰的错误与成功提示
- 直观的操作反馈
```

## 📸 Talk is cheap, show me the view

<img width="1685" alt="image" src="https://github.com/chris-2s/tissue/assets/159798260/e5707b21-2737-4fb6-839e-a213318eddf3">
<img width="1685" alt="image" src="https://github.com/chris-2s/tissue/assets/159798260/4597df98-87bf-40a6-805f-37dc0b5e02ad">
<img width="1682" alt="image" src="https://github.com/chris-2s/tissue/assets/159798260/ac11e3c0-7631-40cb-bef6-7074fe3bbc2f">

## 🚀 技术架构

### 前后端分离设计

- **后端**：Python FastAPI + SQLAlchemy
- **前端**：React + TypeScript + Vite + Ant Design
- **数据库**：SQLite（轻量化部署）
- **容器化**：Docker 多阶段构建，支持多架构

### CI/CD 自动化

- **GitHub Actions**：自动构建和发布
- **多架构支持**：AMD64 + ARM64
- **版本管理**：自动标签和更新日志
- **代码质量**：ESLint + Prettier 检查

## 🤝 贡献指南

欢迎贡献代码！请遵循以下流程：

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 创建 Pull Request

### 开发环境搭建

```bash
# 克隆仓库
git clone https://github.com/Await-d/tissue.git
cd tissue

# 后端开发
pip install -r requirements.txt
python startup_check.py

# 前端开发
cd frontend
npm install
npm run dev
```

## 📄 许可证

本项目基于 [LICENSE](LICENSE.txt) 许可证开源。

## ⭐ 项目状态

- ✅ **稳定运行**：已在多个生产环境稳定运行
- 🔄 **持续更新**：定期发布新功能和修复
- 📈 **活跃维护**：快速响应 Issues 和 PR
- 🌏 **多语言支持**：计划支持更多语言

---

<p align="center">
  <a href="https://github.com/Await-d/tissue">⭐ 如果这个项目对您有帮助，请给个 Star！</a>
</p>

<p align="center">
  <a href="https://github.com/Await-d/tissue/issues">🐛 报告问题</a> |
  <a href="https://github.com/Await-d/tissue/discussions">💬 讨论交流</a> |
  <a href="https://hub.docker.com/r/await2719/tissue-plus">🐳 Docker Hub</a>
</p>
