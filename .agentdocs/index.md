# Agentdocs 索引

## 活动工作流

- 暂无。

## 已完成工作流

- [多渠道数据源集成](workflow/done/260816-multi-source-integration.md)：来源 PoC、榜单能力边界与空结果失败语义已完成；DMM/FANZA、JAVLibrary 因公开访问限制搁置。

## Architecture Decisions

- [2026-08-16] 首页榜单以具备 `ranking` 能力的来源为准，详情/下载来源不得被误用为榜单来源。
- [2026-08-16] 新来源必须复用应用代理与镜像健康探测；Windows 系统代理不会自动传入爬虫会话。

## Known Pitfalls

- HTTP 200 可能是版权限制页或挑战页，来源探测必须验证页面语义而非只验证状态码；DMM/FANZA 的 200 是年龄确认页，JAVLibrary 公开入口是 Cloudflare challenge，未合规可访问前不得排期解析器。
- JavBus 已验证适合详情抓取，但当前未实现排行榜抓取，不能作为首页榜单的后备来源。

## Global Important Memory

- 临时编排产物只能写入 `.agentdocs/runtime/`，该目录不提交；持久化设计写入 `.agentdocs/workflow/`。
