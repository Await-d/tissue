# 最近新增功能 (2024)

## 种子停止做种功能 (2024-07-06)

### 功能概述
添加了种子完成后自动停止做种的控制功能，解决用户反映的种子自动做种问题。

### 技术实现
- **后端配置**: 在 `SettingDownload` 中添加 `stop_seeding: bool = True` 字段
- **qBittorrent 集成**: 新增 `pause_torrent()` 方法调用 `/api/v2/torrents/pause` API
- **下载服务**: 修改 `complete_download()` 方法，在种子整理成功时自动暂停做种
- **前端界面**: 在下载设置页面添加"完成后停止做种"开关

### 核心文件变更
- `app/schema/setting.py`: 添加配置字段
- `app/utils/qbittorent.py`: 添加暂停种子API
- `app/service/download.py`: 集成停止做种逻辑
- `frontend/src/routes/_index/setting/download.tsx`: 前端配置界面

### 使用方法
1. 进入设置 → 下载设置
2. 找到"完成后停止做种"选项（默认开启）
3. 根据需要开启或关闭功能
4. 保存设置后生效

### 技术特点
- **默认启用**: 解决用户痛点
- **智能控制**: 仅在整理成功时触发
- **错误隔离**: 暂停失败不影响主流程
- **用户友好**: 清晰的界面提示

### 提交信息
- Commit: f518473
- 日期: 2024-07-06
- 分支: master