/* 演员搜索组件样式应用示例 */

// ====== 示例1: 搜索输入框 ======
<Input
  className="actor-search-input"
  placeholder="搜索演员..."
  prefix={<SearchOutlined style={{ color: '#a0a0a8' }} />}
  style={{
    background: '#141416',
    border: '1px solid rgba(255, 255, 255, 0.08)',
    color: '#f0f0f2'
  }}
/>

// ====== 示例2: 下拉菜单 ======
<AutoComplete
  popupClassName="actor-search-dropdown"
  options={options}
/>

// ====== 示例3: 演员卡片 ======
<div className="web-actor-card">
  <div className="web-actor-avatar-wrapper">
    <Avatar
      size={64}
      src={actorThumb}
      style={{
        border: '3px solid #141416',
        background: '#222226'
      }}
    />
  </div>
  <div>{actorName}</div>
</div>

// ====== 示例4: 视频卡片 ======
<Card
  className="web-actor-video-card"
  hoverable
  styles={{
    body: {
      padding: '16px',
      background: '#141416'
    }
  }}
>
  <Card.Meta
    title={<span style={{ color: '#f0f0f2' }}>{videoTitle}</span>}
    description={
      <div>
        <span className="web-actor-badge web-actor-badge-zh">中文</span>
        <span className="web-actor-badge web-actor-badge-uncensored">无码</span>
      </div>
    }
  />
</Card>

// ====== 示例5: 来源选择按钮组 ======
<Radio.Group
  className="web-actor-source-group"
  value={sourceType}
>
  <Radio.Button value="javdb">JavDB</Radio.Button>
  <Radio.Button value="javbus">JavBus</Radio.Button>
</Radio.Group>

// ====== 示例6: 选中演员信息卡 ======
<div className="web-actor-selected-card">
  <div className="web-actor-avatar-wrapper" style={{ padding: '6px' }}>
    <Avatar
      size={96}
      src={selectedActor.thumb}
      style={{
        border: '4px solid #141416',
        background: '#222226'
      }}
    />
  </div>
  <h2 style={{ color: '#f0f0f2' }}>{selectedActor.name}</h2>
</div>

// ====== 示例7: 主容器 ======
<div style={{
  padding: '20px',
  background: '#0d0d0f',
  minHeight: '100vh'
}}>
  {/* 组件内容 */}
</div>

// ====== 色彩使用指南 ======
const colors = {
  // 背景色
  base: '#0d0d0f',          // 页面主背景
  elevated: '#141416',      // 卡片、输入框背景
  container: '#1a1a1d',     // 容器背景
  spotlight: '#222226',     // 高亮容器背景
  
  // 金色系
  goldPrimary: '#d4a852',   // 主要金色（按钮、边框）
  goldLight: '#e8c780',     // 浅金色（悬停、高亮）
  goldDark: '#b08d3e',      // 深金色（激活、选中）
  
  // 文字色
  textPrimary: '#f0f0f2',   // 主要文字
  textSecondary: '#a0a0a8', // 次要文字
  textTertiary: '#6a6a72',  // 辅助文字
  
  // 边框
  border: 'rgba(255, 255, 255, 0.08)'
};

// ====== 阴影使用指南 ======
const shadows = {
  card: '0 8px 32px rgba(212, 168, 82, 0.2)',       // 卡片悬停
  cardHover: '0 12px 40px rgba(212, 168, 82, 0.25)', // 视频卡片悬停
  avatar: '0 4px 12px rgba(212, 168, 82, 0.3)',     // 头像
  avatarHover: '0 0 24px rgba(212, 168, 82, 0.6)',  // 头像悬停光晕
  dropdown: '0 12px 48px rgba(0, 0, 0, 0.5)',       // 下拉菜单
  button: '0 4px 16px rgba(212, 168, 82, 0.4)'      // 按钮悬停
};

// ====== 过渡动画指南 ======
const transitions = {
  default: 'all 0.3s ease',
  smooth: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  fast: 'all 0.2s ease',
  slow: 'all 0.5s ease'
};

// ====== 实战技巧 ======

// 1. 悬停上移效果
const hoverStyle = {
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  ':hover': {
    transform: 'translateY(-4px)',
    boxShadow: '0 8px 32px rgba(212, 168, 82, 0.2)'
  }
};

// 2. 金色聚焦效果
const focusStyle = {
  ':focus': {
    borderColor: '#d4a852',
    boxShadow: '0 0 0 3px rgba(212, 168, 82, 0.1)'
  }
};

// 3. 渐变背景
const gradientBg = {
  background: 'linear-gradient(135deg, #d4a852 0%, #e8c780 100%)'
};

// 4. 玻璃态效果
const glassmorphism = {
  background: 'rgba(20, 20, 22, 0.8)',
  backdropFilter: 'blur(24px)',
  border: '1px solid rgba(255, 255, 255, 0.08)'
};
