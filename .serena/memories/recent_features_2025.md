# 最近新增功能和修复 (2025)

## 智能下载评分评论筛选修复 (2025-01-09)

### 问题背景
智能下载规则设置"评分>=4.0, 评论>=1000"条件后，无法筛选到符合条件的视频，影响自动下载功能的正常使用。

### 修复内容

#### 1. 字段映射统一化
- **javdb.py**: 确保所有爬虫方法都设置 `comments` 和 `comments_count` 字段
- **最新视频页面**: 添加评论数字段初始化（设为0）
- **排行榜页面**: 同时设置两个评论字段

#### 2. 数据处理健壮性
- **类型转换**: 添加 `float()` 和 `int()` 的异常处理
- **多字段兼容**: 支持从 `comments` 或 `comments_count` 获取评论数
- **边界情况**: 正确处理评论数为0的情况

#### 3. 调试和监控增强
- **详细日志**: 显示每个视频的评分、评论数及数据类型
- **筛选过程**: 记录具体的比较结果和决策原因
- **统计信息**: 显示有效数据的比例和分布

### 技术实现

#### 字段兼容性处理
```python
# 尝试从多个字段获取评论数
if video_comments == 0 and video_comments_count != 0:
    video_comments = video_comments_count
```

#### 类型安全的比较
```python
try:
    rating_float = float(video_rating)
    min_rating_float = float(min_rating)
    if rating_float < min_rating_float:
        continue
except (ValueError, TypeError) as e:
    logger.warning(f"评分转换失败: {video_rating}, 错误: {e}")
```

#### 详细的调试日志
```python
logger.info(f"视频 {video.get('num')} 评分比较: {rating_float} >= {min_rating_float} ? {rating_float >= min_rating_float}")
```

### 修复效果
1. **问题诊断**: 现在可以清楚看到每个视频的数据和筛选过程
2. **数据完整性**: 确保评分和评论数据的正确获取和处理
3. **系统稳定性**: 避免因数据类型问题导致的筛选失败
4. **用户体验**: 智能下载规则现在可以正确工作

### 核心文件变更
- `app/service/auto_download.py`: 增强调试日志和字段兼容性
- `app/utils/video_collector.py`: 优化筛选逻辑和错误处理  
- `app/utils/spider/javdb.py`: 修复字段映射不一致问题

### 部署信息
- **提交ID**: c11a54e
- **修改时间**: 2025-01-09
- **影响范围**: 智能下载功能
- **兼容性**: 向后兼容，无破坏性更改

### 验证建议
1. 重新运行智能下载规则，观察日志输出
2. 检查"有效评分数据"和"有效评论数据"统计
3. 确认筛选逻辑按预期工作
4. 验证符合条件的视频能够被正确识别和下载