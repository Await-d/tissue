# 智能自动下载功能 - 使用指南

## 📋 功能概述

智能自动下载功能已成功集成到Tissue-Plus项目中，提供了基于多种条件（评分、评论数、时间范围等）的自动筛选和下载功能。

## 🚀 部署步骤

### 1. 数据库迁移
```bash
# 运行数据库迁移
alembic upgrade head
```

### 2. 重启应用服务
```bash
# 重启后端服务以加载新的API路由和定时任务
# 具体命令取决于你的部署方式
```

### 3. 前端构建（如需要）
```bash
cd frontend
npm install
npm run build
```

## 🎯 核心功能

### 1. 规则管理
- **位置**: 侧边栏 → 订阅 → 智能下载 → 规则管理
- **功能**: 创建、编辑、删除筛选规则
- **筛选条件**:
  - 最低评分 (0-10分)
  - 最低评论数 (≥0)
  - 时间范围 (天/周/月)
  - 质量要求 (高清/中文/无码)

### 2. 订阅记录
- **位置**: 侧边栏 → 订阅 → 智能下载 → 订阅记录
- **功能**: 查看自动订阅的作品记录
- **状态管理**:
  - 待处理 (pending)
  - 下载中 (downloading)
  - 已完成 (completed)
  - 失败 (failed)

### 3. 系统设置
- **位置**: 侧边栏 → 设置 → 智能下载
- **功能**: 全局配置和系统监控
- **配置项**:
  - 启用/禁用自动下载
  - 检查间隔设置
  - 每日下载限制
  - 通知设置

## 📖 使用流程

### 第一步：创建筛选规则
1. 进入 `智能下载 → 规则管理`
2. 点击 `创建规则` 按钮
3. 设置筛选条件：
   ```
   规则名称: 高质量作品自动下载
   最低评分: 8.5
   最低评论数: 50
   时间范围: 1周
   质量要求: ✅高清 ❌中文 ❌无码
   ```
4. 保存并启用规则

### 第二步：监控执行状态
1. 查看统计信息面板
2. 检查订阅记录页面
3. 关注系统日志

### 第三步：管理订阅记录
1. 定期清理失败记录
2. 重试失败的下载
3. 调整规则参数

## ⚙️ API接口

### 规则管理
```http
GET    /api/auto-download/rules          # 获取规则列表
POST   /api/auto-download/rules          # 创建规则
PUT    /api/auto-download/rules/{id}     # 更新规则
DELETE /api/auto-download/rules/{id}     # 删除规则
```

### 订阅管理
```http
GET    /api/auto-download/subscriptions  # 获取订阅记录
DELETE /api/auto-download/subscriptions/{id}  # 删除记录
POST   /api/auto-download/subscriptions/batch  # 批量操作
```

### 系统管理
```http
GET    /api/auto-download/statistics     # 获取统计信息
POST   /api/auto-download/trigger        # 手动触发执行
```

## 🔧 技术实现

### 后端架构
```
app/
├── db/models/auto_download.py          # 数据模型
├── schema/auto_download.py             # API Schema
├── service/auto_download.py            # 业务逻辑
├── api/auto_download.py                # API路由
└── utils/video_collector.py            # 视频收集器
```

### 前端架构
```
frontend/src/
├── apis/autoDownload.ts                # API接口
└── routes/_index/auto-download/
    ├── index.tsx                       # 主页面
    ├── rules.tsx                       # 规则管理
    └── subscriptions.tsx               # 订阅记录
```

### 定时任务
- **执行频率**: 每60分钟
- **任务名称**: `auto_download`
- **主要逻辑**: 执行所有启用的规则，筛选和下载符合条件的作品

## 📊 数据库表结构

### auto_download_rules (规则表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| name | VARCHAR(255) | 规则名称 |
| min_rating | DECIMAL(3,1) | 最低评分 |
| min_comments | INT | 最低评论数 |
| time_range_type | ENUM | 时间范围类型 |
| time_range_value | INT | 时间范围值 |
| is_hd/is_zh/is_uncensored | BOOLEAN | 质量要求 |
| is_enabled | BOOLEAN | 是否启用 |

### auto_download_subscriptions (订阅记录表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| rule_id | INT | 关联规则ID |
| num | VARCHAR(50) | 番号 |
| title | VARCHAR(500) | 标题 |
| rating | DECIMAL(3,1) | 评分 |
| comments_count | INT | 评论数 |
| status | ENUM | 下载状态 |
| download_url | VARCHAR(1000) | 下载链接 |

## 🚨 注意事项

### 性能考虑
1. **检查频率**: 建议设置为60分钟以上，避免过于频繁的网站请求
2. **下载限制**: 设置合理的每日下载数量，避免占用过多带宽
3. **规则数量**: 建议同时激活的规则数量不超过5个

### 安全考虑
1. **API认证**: 所有API接口都需要用户认证
2. **参数验证**: 输入参数已进行严格验证
3. **异常处理**: 完善的错误处理和日志记录

### 监控建议
1. **定期检查**: 监控订阅记录的成功率
2. **日志审查**: 关注系统日志中的错误信息
3. **资源使用**: 监控服务器资源使用情况

## 🔍 故障排除

### 常见问题

**1. 规则不执行**
- 检查规则是否启用
- 确认定时任务是否正常运行
- 查看系统日志错误信息

**2. 筛选结果为空**
- 降低筛选条件（评分、评论数）
- 扩大时间范围
- 检查网站数据源是否正常

**3. 下载失败**
- 检查网络连接
- 确认qBittorrent连接正常
- 查看下载服务日志

### 日志查看
```bash
# 查看应用日志
tail -f logs/app.log

# 查看自动下载相关日志
grep "auto_download\|AutoDownload" logs/app.log
```

## 📈 未来扩展

### 计划功能
1. **智能推荐**: 基于用户下载历史的推荐算法
2. **更多数据源**: 集成更多视频网站的数据
3. **高级筛选**: 支持演员、制作商等更多筛选条件
4. **通知增强**: 微信、邮件等多种通知方式
5. **统计分析**: 更详细的下载统计和趋势分析

### 贡献指南
欢迎提交Issue和Pull Request来改进这个功能！

---

**版本**: v1.0.0  
**最后更新**: 2025-01-06  
**维护者**: Tissue-Plus Team