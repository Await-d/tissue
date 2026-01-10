# 索引

## 产品文档
- 暂无

## 前端文档
- 暂无

## 后端文档
- 暂无

## 当前任务文档
- 暂无；如遇复杂任务请在 `.agentdocs/workflow/YYMMDD-任务简述.md` 建立并在此登记

## 全局重要记忆
- 遵循 KISS、YAGNI、SOLID、DRY 及测试优先原则，变更需配套必要的 lint/test
- 远端：`origin=https://github.com/Await-d/tissue.git`，`upstream=https://github.com/chris-2s/tissue.git`；合并上游时从 `master` 派生工作分支，先快进到 `origin/master` 再合并 `upstream/main`
- 数据模型：`VideoActor` 增加 `code` 字段，`VideoDetail` 新增 `comments/site_actors`；所有爬虫 `get_info` 需接受 `include_comments` 参数并尽量填充 `site_actors` 以支持前端搜索演员弹窗/评论卡片
