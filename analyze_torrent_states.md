# 种子状态分析说明

## 常见的qBittorrent种子状态

### 下载相关状态
- `downloading` - 正在下载
- `stalledDL` - 下载停滞（无速度）
- `queuedDL` - 下载队列中
- `pausedDL` - 暂停下载

### 做种相关状态  
- `uploading` - 正在上传（做种）
- `stalledUP` - 上传停滞（做种但无上传速度）
- `queuedUP` - 上传队列中
- `forcedUP` - 强制上传
- `pausedUP` - 暂停上传

### 完成状态
- `completed` - 已完成（可能在做种也可能不在）

## 修改后的检测逻辑

新的检测条件更加智能：
```python
# 检查是否有整理相关标签
has_organize_tag = '整理成功' in tags or '整理失败' in tags

# 决定是否停止做种
should_stop = is_completed and is_seeding and (is_organized or not has_organize_tag)
```

这意味着会停止以下种子的做种：
1. **已完成 + 已整理成功 + 正在做种** （原逻辑）
2. **已完成 + 无整理标签 + 正在做种** （新增：处理未整理的完成种子）

不会停止：
- **已完成 + 整理失败 + 正在做种** （保留失败的，可能需要重新处理）