# 已下载番号显示标识功能 - 实现计划

## 📋 需求分析

用户希望在首页（排行榜）、番号订阅列表和演员订阅页面中，对已下载过的番号进行明显的视觉提示，防止重复订阅和下载。

## 🎯 目标

1. 在视频卡片上显示"已下载"徽章/标签
2. 支持首页、订阅页面、演员订阅页面
3. 检测来源包括：
   - qBittorrent 下载记录（`torrent` 表）
   - 演员订阅下载记录（`actor_subscribe_download` 表）
   - 番号订阅记录（`subscribe` 表，status=2）
   - 文件整理历史（`history` 表，status=1）
   - 文件系统扫描（可选，性能考虑）

## 📐 技术方案

### 1. 后端实现

#### 1.1 创建检测服务 `DownloadStatusService`

**文件**: `app/service/download_status.py`

```python
class DownloadStatusService(BaseService):
    def check_download_status_batch(self, nums: List[str]) -> Dict[str, bool]:
        """批量检测番号下载状态
        
        Args:
            nums: 番号列表
            
        Returns:
            Dict[番号, 是否已下载]
        """
        # 检测逻辑：
        # 1. 查询 torrent 表
        # 2. 查询 actor_subscribe_download 表  
        # 3. 查询 subscribe 表（status=2）
        # 4. 查询 history 表（status=1）
        # 返回 {num: True/False} 字典
```

#### 1.2 创建 API 端点

**文件**: `app/api/download_status.py`

```python
@router.post('/check-batch')
def check_download_status_batch(
    request: DownloadStatusBatchRequest,
    service: DownloadStatusService = Depends(...)
):
    """批量检测下载状态
    
    Request:
        {
            "nums": ["ABC-123", "DEF-456", ...]
        }
        
    Response:
        {
            "data": {
                "ABC-123": true,
                "DEF-456": false,
                ...
            }
        }
    """
```

#### 1.3 Schema 定义

**文件**: `app/schema/download_status.py`

```python
class DownloadStatusBatchRequest(BaseModel):
    nums: List[str]
    
class DownloadStatusBatchResponse(BaseModel):
    data: Dict[str, bool]
```

### 2. 前端实现

#### 2.1 创建 API 调用函数

**文件**: `frontend/src/apis/downloadStatus.ts`

```typescript
export async function checkDownloadStatusBatch(nums: string[]) {
    const response = await request.request({
        url: '/download-status/check-batch',
        method: 'post',
        data: { nums }
    });
    return response.data.data;
}
```

#### 2.2 创建 Hook

**文件**: `frontend/src/hooks/useDownloadStatus.ts`

```typescript
export function useDownloadStatus(videos: any[]) {
    const [statusMap, setStatusMap] = useState<Record<string, boolean>>({});
    const [loading, setLoading] = useState(false);
    
    useEffect(() => {
        const nums = videos.map(v => v.num).filter(Boolean);
        if (nums.length === 0) return;
        
        setLoading(true);
        checkDownloadStatusBatch(nums)
            .then(setStatusMap)
            .finally(() => setLoading(false));
    }, [videos]);
    
    return { statusMap, loading };
}
```

#### 2.3 修改视频卡片组件

**文件**: `frontend/src/routes/_index/home/-components/item.tsx`

在组件中添加已下载徽章：

```tsx
// 在视频卡片封面区域添加
{isDownloaded && (
    <div style={{
        position: 'absolute',
        top: 14,
        right: 14,
        background: 'rgba(76, 175, 80, 0.95)',
        color: 'white',
        padding: '6px 12px',
        borderRadius: 8,
        fontSize: 12,
        fontWeight: 600,
        boxShadow: '0 2px 8px rgba(0,0,0,0.3)'
    }}>
        ✓ 已下载
    </div>
)}
```

#### 2.4 修改首页

**文件**: `frontend/src/routes/_index/home/index.tsx`

```typescript
// 使用 hook 获取下载状态
const videos = await Route.useLoaderData().data;
const { statusMap } = useDownloadStatus(videos);

// 传递给每个视频卡片
<JavDBItem 
    item={video} 
    isDownloaded={statusMap[video.num]} 
/>
```

#### 2.5 修改订阅页面

**文件**: `frontend/src/routes/_index/subscribe/index.tsx`

类似修改，添加下载状态检测和显示

#### 2.6 修改演员订阅页面  

**文件**: `frontend/src/routes/_index/actor-subscribe/index.tsx`

在演员订阅的下载记录列表中已经显示了下载的内容，主要关注其他页面

### 3. 性能优化方案

#### 3.1 批量查询优化

```python
# 使用 IN 查询替代多次单独查询
nums_set = set(nums)

# 一次性查询所有相关记录
torrent_nums = set(self.db.query(Torrent.num)
                   .filter(Torrent.num.in_(nums))
                   .distinct())

subscribe_nums = set(self.db.query(Subscribe.num)
                    .filter(Subscribe.num.in_(nums), Subscribe.status == 2)
                    .distinct())

# ...合并结果
```

#### 3.2 缓存机制（可选）

```python
from functools import lru_cache
from datetime import datetime, timedelta

class DownloadStatusCache:
    """下载状态缓存，5分钟有效期"""
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
        
    def get(self, num: str) -> Optional[bool]:
        if num in self._cache:
            if datetime.now() - self._timestamps[num] < timedelta(minutes=5):
                return self._cache[num]
        return None
        
    def set(self, num: str, status: bool):
        self._cache[num] = status
        self._timestamps[num] = datetime.now()
```

### 4. UI/UX 设计

#### 4.1 徽章样式

- **已下载**: 绿色徽章，带勾选标记
- **位置**: 视频卡片右上角
- **样式**: 半透明背景，白色文字

#### 4.2 可选增强

- 鼠标悬停显示下载详情（下载时间、来源等）
- 支持点击徽章快速跳转到下载列表
- 提供筛选功能：只显示未下载/已下载

## 📝 实现步骤

### 阶段 1: 后端开发（2-3小时）

1. ✅ 分析现有下载记录表结构
2. ⏳ 创建 `DownloadStatusService` 服务
3. ⏳ 实现批量检测逻辑
4. ⏳ 创建 API 路由和 schema
5. ⏳ 编写单元测试

### 阶段 2: 前端开发（2-3小时）

1. ⏳ 创建 API 调用函数
2. ⏳ 实现 `useDownloadStatus` hook
3. ⏳ 修改视频卡片组件
4. ⏳ 修改首页、订阅页面
5. ⏳ 调整样式和交互

### 阶段 3: 测试和优化（1-2小时）

1. ⏳ 功能测试（各页面显示）
2. ⏳ 性能测试（大量数据场景）
3. ⏳ UI/UX 优化
4. ⏳ 错误处理和边界情况

## 🔍 技术细节

### 数据库查询优化

```sql
-- 高效的批量查询示例
SELECT DISTINCT num FROM (
    SELECT num FROM torrent WHERE num IN (?, ?, ...)
    UNION
    SELECT num FROM subscribe WHERE num IN (?, ?, ...) AND status = 2
    UNION
    SELECT num FROM actor_subscribe_download WHERE num IN (?, ?, ...)
    UNION  
    SELECT num FROM history WHERE num IN (?, ?, ...) AND status = 1
) AS combined_results
```

### API 响应格式

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "ABC-123": true,
        "DEF-456": false,
        "GHI-789": true
    }
}
```

## ⚠️ 注意事项

1. **番号大小写**: 统一转换为大写进行比较
2. **性能考虑**: 限制单次批量查询的番号数量（如最多100个）
3. **缓存失效**: 当有新下载时需要清除相关缓存
4. **文件系统扫描**: 可选功能，需要考虑性能影响
5. **错误处理**: API 调用失败时不应影响页面正常显示

## 📊 预期效果

- 用户可以一目了然地看到哪些视频已下载
- 减少重复订阅和下载
- 提升用户体验
- 对系统性能影响最小（批量查询 + 可选缓存）

## 🚀 后续优化

1. 添加下载来源标识（订阅/演员订阅/手动下载）
2. 显示下载时间
3. 支持点击徽章查看详情
4. 添加筛选和排序功能
5. 导出已下载番号列表

---

**创建时间**: 2026-01-11  
**作者**: Claude Code
**状态**: 计划中
