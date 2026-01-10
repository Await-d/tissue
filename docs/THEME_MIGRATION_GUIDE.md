# 主题颜色迁移指南

## 概述
本项目已支持明亮/暗黑主题切换。所有组件的硬编码颜色值需要迁移到使用 `useThemeColors` hook。

## 迁移步骤

###  1. 导入 hook
在组件文件顶部添加导入：

```typescript
import { useThemeColors } from '../../../hooks/useThemeColors';
// 或根据文件位置调整路径
```

### 2. 在组件函数中调用 hook
```typescript
function MyComponent() {
    const colors = useThemeColors()
    // ... 其他代码
}
```

### 3. 替换硬编码颜色

#### 背景色
```typescript
// 旧代码
background: '#0d0d0f'
background: '#141416'
background: '#1a1a1d'
background: '#222226'

// 新代码
background: colors.bgBase
background: colors.bgElevated
background: colors.bgContainer
background: colors.bgSpotlight
```

#### 文字颜色
```typescript
// 旧代码
color: '#f0f0f2'
color: '#a0a0a8'
color: '#6a6a72'

// 新代码
color: colors.textPrimary
color: colors.textSecondary
color: colors.textTertiary
```

#### 金色强调
```typescript
// 旧代码
color: '#d4a852'
color: '#e8c780'
color: '#b08d3e'

// 新代码
color: colors.goldPrimary
color: colors.goldLight
color: colors.goldDark
```

#### 边框颜色
```typescript
// 旧代码
borderColor: 'rgba(255, 255, 255, 0.08)'
borderColor: 'rgba(255, 255, 255, 0.04)'
borderColor: 'rgba(212, 168, 82, 0.3)'

// 新代码
borderColor: colors.borderPrimary
borderColor: colors.borderSecondary
borderColor: colors.borderGold
```

#### 渐变色
```typescript
// 旧代码
background: 'linear-gradient(135deg, #d4a852 0%, #b08d3e 100%)'

// 新代码
background: colors.goldGradient
```

#### 动态透明度
```typescript
// 旧代码
background: 'rgba(212, 168, 82, 0.2)'
background: 'rgba(212, 168, 82, 0.1)'

// 新代码
background: colors.rgba('gold', 0.2)
background: colors.rgba('gold', 0.1)
background: colors.rgba('white', 0.08)
background: colors.rgba('black', 0.12)
```

## 完整示例

### 迁移前
```typescript
import { Card } from 'antd';

function MyComponent() {
    return (
        <Card style={{
            background: '#1a1a1d',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            color: '#f0f0f2'
        }}>
            <h1 style={{ color: '#d4a852' }}>标题</h1>
        </Card>
    );
}
```

### 迁移后
```typescript
import { Card } from 'antd';
import { useThemeColors } from '../../../hooks/useThemeColors';

function MyComponent() {
    const colors = useThemeColors()

    return (
        <Card style={{
            background: colors.bgContainer,
            border: `1px solid ${colors.borderPrimary}`,
            color: colors.textPrimary
        }}>
            <h1 style={{ color: colors.goldPrimary }}>标题</h1>
        </Card>
    );
}
```

## 可用颜色属性

### 背景色
- `colors.bgBase` - 基础背景
- `colors.bgElevated` - 提升背景
- `colors.bgContainer` - 容器背景
- `colors.bgSpotlight` - 高亮背景

### 文字色
- `colors.textPrimary` - 主要文字
- `colors.textSecondary` - 次要文字
- `colors.textTertiary` - 第三级文字
- `colors.textGold` - 金色文字

### 金色强调
- `colors.goldPrimary` - 金色主色
- `colors.goldLight` - 浅金色
- `colors.goldDark` - 深金色
- `colors.goldGlow` - 金色光晕

### 边框
- `colors.borderPrimary` - 主要边框
- `colors.borderSecondary` - 次要边框
- `colors.borderGold` - 金色边框

### 填充
- `colors.fill` - 主要填充
- `colors.fillSecondary` - 次要填充

### 功能色
- `colors.success` - 成功色 (#52c41a)
- `colors.warning` - 警告色 (#faad14)
- `colors.error` - 错误色 (#ff4d4f)
- `colors.info` - 信息色 (#1890ff)

### 渐变
- `colors.goldGradient` - 金色渐变
- `colors.goldGradientHover` - 金色渐变悬停

### 阴影
- `colors.shadowSm` - 小阴影
- `colors.shadowMd` - 中等阴影
- `colors.shadowLg` - 大阴影
- `colors.shadowGold` - 金色阴影

### 工具方法
- `colors.rgba(color, alpha)` - 生成rgba颜色
  - color: 'gold' | 'white' | 'black'
  - alpha: 0-1 之间的透明度值

## 已迁移文件
- ✅ frontend/src/routes/__root.tsx
- ✅ frontend/src/routes/login/index.tsx
- ✅ frontend/src/routes/_index/download/index.tsx
- ✅ 所有 CSS 文件（使用 CSS 变量）

## 待迁移文件（TSX 内联样式）
请参考上面的指南逐个迁移以下文件中的内联样式：

### 设置页面
- frontend/src/routes/_index/setting/version.tsx
- frontend/src/routes/_index/setting/download-filter.tsx
- frontend/src/routes/_index/setting/auto-download.tsx
- frontend/src/routes/_index/setting/app.tsx
- frontend/src/routes/_index/setting/download.tsx
- frontend/src/routes/_index/setting/file.tsx
- frontend/src/routes/_index/setting/notify.tsx

### 自动下载
- frontend/src/routes/_index/auto-download/subscriptions.tsx
- frontend/src/routes/_index/auto-download/rules.tsx

### 订阅管理
- frontend/src/routes/_index/subscribe/index.tsx
- frontend/src/routes/_index/actor-subscribe/index.tsx

### 其他页面
- frontend/src/routes/_index/search/index.tsx
- frontend/src/routes/_index/history/index.tsx
- frontend/src/routes/_index/site/index.tsx
- frontend/src/routes/_index/schedule/index.tsx
- frontend/src/routes/_index/home/index.tsx
- frontend/src/routes/_index/about/index.tsx
- frontend/src/routes/_index/file/index.tsx
- frontend/src/routes/_index/actor/index.tsx

### 组件
- frontend/src/components/ActorSearch/*.tsx
- frontend/src/components/VideoDetail/index.tsx
- frontend/src/components/VideoActors/index.tsx
- frontend/src/components/BatchDownload/BatchDownloadModal.tsx
- frontend/src/components/PinView/index.tsx
- frontend/src/components/Slider/index.tsx
- frontend/src/components/ProgressFloatButton/index.tsx

## 注意事项

1. **CSS 变量优先**：对于可以使用 CSS 类的地方，优先使用 CSS 变量而不是内联样式
2. **性能考虑**：`useThemeColors` hook 在主题切换时会触发组件重新渲染
3. **类型安全**：所有颜色值都是字符串类型，可以直接在样式对象中使用
4. **渐进迁移**：可以逐个文件迁移，新旧代码可以共存

## 测试
迁移后，测试以下场景：
1. 切换到明亮主题，检查所有颜色是否正确
2. 切换到暗黑主题，检查所有颜色是否正确
3. 切换到跟随系统，检查主题是否跟随系统设置
