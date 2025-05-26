<!--
 * @Author: Await
 * @Date: 2025-05-24 17:05:38
 * @LastEditors: Await
 * @LastEditTime: 2025-05-27 04:30:00
 * @Description: Tissue-Plus 项目，您的智能教材管家！
-->
# Tissue-Plus ✨

![GitHub License](https://img.shields.io/github/license/Await-d/tissue)
![Docker Image Version](https://img.shields.io/docker/v/chris2s/tissue-plus/latest)
![Docker Image Size](https://img.shields.io/docker/image-size/chris2s/tissue-plus/latest)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/Await-d/tissue/build.yml)

**Tissue-Plus：您的智能教材管家，让学习资料整理从未如此轻松高效！** 📚🚀

还在为散落各处的学习视频、文档、笔记而烦恼吗？Tissue-Plus 专为解决这一痛点而生！它不仅能帮您**智能刮削教材信息**，自动下载精美海报、匹配元数据，还能将您的所有学习资料在 Jellyfin、Emby、Kodi 等媒体服务器中**优雅地装订成册**，如同拥有一个私人定制的数字图书馆。

> 本项目基于备受好评的 [chris-2s/tissue](https://github.com/chris-2s/tissue) 项目深度进化，感谢原作者的卓越贡献！我们在此基础上，注入了更多强大、便捷的功能，致力于打造终极学习资料管理体验。

[效果图传送阵](#talk-is-cheap-show-me-the-view) | [版本更新记录](CHANGELOG.md) | [点我看前端日志效果](#前端日志展示)

## 🌟 Tissue-Plus 核心亮点

* **🎬 智能元数据刮削**：告别手动整理！自动识别视频文件，从各大知名站点（JavBus, JavDB等）拉取封面、演员、标签、发行日期等详细信息。
* **🖼️ 精美海报生成**：让您的媒体库焕然一新！自动下载高清海报，影片信息一目了然。
* **👤 演员订阅系统**：再也不会错过老师的新作品！一键订阅您关注的演员，新教材发布自动提醒并下载。
  * **智能筛选**：支持按高清、中文字幕、无码等偏好筛选资源。
  * **状态管理**：轻松暂停或恢复演员订阅，灵活控制下载。
  * **资源清理**：取消订阅时可选择是否一并删除已下载的视频和种子文件。
* **🔗 qBittorrent 深度集成**：无缝对接qBittorrent下载器，实现从订阅到下载的全自动化流程。
* **🚀 高效任务调度**：定时检查演员更新、自动刮削新入库文件，无需人工干预。
* **🌐 Web用户界面**：现代化、响应式的Web界面，随时随地轻松管理您的教材库。
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

[前往Docker Hub获取最新镜像](https://hub.docker.com/r/chris2s/tissue-plus)

或直接运行以下命令 (请根据您的实际环境修改路径和端口):

```shell
docker run \
  -d \
  --name=tissue-plus \
  -e TZ="Asia/Shanghai" \
  -p '9193:9193' \
  -v '/path/for/config':'/app/config'       # 配置文件存储路径
  -v '/path/for/video':'/data/video'         # 您的媒体库（影片存放处）
  -v '/path/for/file':'/data/file'           # 待处理文件监控路径 (可选)
  -v '/path/for/downloads':'/downloads'     # qBittorrent下载路径映射
  'chris2s/tissue-plus:latest'
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

### 默认登录凭据

* **用户名**：`admin`
* **默认密码**：`password` (首次登录后强烈建议修改！)

### 关于文件转移

* Tissue-Plus支持**复制**和**移动**两种方式将刮削整理好的文件放入媒体库。
* **注意**：当使用"移动"模式时，如果您的Docker路径映射横跨了不同的宿主机挂载点（即使它们在同一物理磁盘上），Docker的行为可能类似于跨磁盘移动，导致无法实现"秒传"效果。为了最佳性能，建议将源路径和目标路径设置在同一个宿主机挂载卷内，或者将它们的共同父目录映射到容器中。

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
