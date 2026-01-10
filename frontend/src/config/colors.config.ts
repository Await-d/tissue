/**
 * 主题颜色配置文件
 * 定义暗色和亮色模式下的所有颜色值
 */

export interface ThemeColorConfig {
    // 背景色系
    bgBase: string
    bgElevated: string
    bgContainer: string
    bgSpotlight: string

    // 金色强调
    goldPrimary: string
    goldLight: string
    goldDark: string
    goldGlow: string

    // 文字色系
    textPrimary: string
    textSecondary: string
    textTertiary: string
    textGold: string

    // 边框与分割
    borderPrimary: string
    borderSecondary: string
    borderGold: string

    // 填充色系
    fill: string
    fillSecondary: string

    // 功能色
    success: string
    warning: string
    error: string
    info: string

    // 金色渐变（用于按钮等）
    goldGradient: string
    goldGradientHover: string

    // 阴影
    shadowSm: string
    shadowMd: string
    shadowLg: string
    shadowGold: string

    // 模态框专用色
    modalBg: string
    modalOverlay: string

    // 兼容旧属性名（别名）
    bgSecondary: string    // 对应 bgElevated
    bgTertiary: string     // 对应 bgContainer
    bgDark: string         // 对应 bgBase
    text: string           // 对应 textPrimary
    gold: string           // 对应 goldPrimary
    dark: string           // 对应 bgBase
    borderColor: string    // 对应 borderPrimary
    border: string         // 对应 borderPrimary
    buttonText: string     // 对应 textPrimary

    // 额外的旧属性（别名）
    background: string     // 对应 bgBase
    bgDarker: string       // 对应 bgBase（更深的背景色）
    cardBg: string         // 对应 bgContainer
    goldAlt: string        // 对应 goldLight
    red: string            // 对应 error
    redLight: string       // 红色的浅色版本
    secondaryText: string  // 对应 textSecondary
    sidebarBg: string      // 对应 bgElevated
    tertiaryText: string   // 对应 textTertiary
    textMuted: string      // 对应 textTertiary
}

export interface RgbaColorMap {
    gold: string
    white: string
    black: string
    red: string
    bgContainer: string
}

/**
 * 暗色模式颜色配置
 */
export const DARK_COLORS: ThemeColorConfig = {
    // 背景色系
    bgBase: '#0d0d0f',
    bgElevated: '#141416',
    bgContainer: '#1a1a1d',
    bgSpotlight: '#222226',

    // 金色强调
    goldPrimary: '#d4a852',
    goldLight: '#e8c780',
    goldDark: '#b08d3e',
    goldGlow: 'rgba(212, 168, 82, 0.15)',

    // 文字色系
    textPrimary: '#f0f0f2',
    textSecondary: '#a0a0a8',
    textTertiary: '#6a6a72',
    textGold: '#d4a852',

    // 边框与分割
    borderPrimary: 'rgba(255, 255, 255, 0.08)',
    borderSecondary: 'rgba(255, 255, 255, 0.04)',
    borderGold: 'rgba(212, 168, 82, 0.3)',

    // 填充色系
    fill: 'rgba(255, 255, 255, 0.06)',
    fillSecondary: 'rgba(255, 255, 255, 0.04)',

    // 功能色
    success: '#52c41a',
    warning: '#faad14',
    error: '#ff4d4f',
    info: '#1890ff',

    // 金色渐变
    goldGradient: 'linear-gradient(135deg, #d4a852 0%, #b08d3e 100%)',
    goldGradientHover: 'linear-gradient(135deg, #e8c780 0%, #d4a852 100%)',

    // 阴影
    shadowSm: '0 2px 8px rgba(0, 0, 0, 0.3)',
    shadowMd: '0 4px 16px rgba(0, 0, 0, 0.4)',
    shadowLg: '0 8px 32px rgba(0, 0, 0, 0.5)',
    shadowGold: '0 0 20px rgba(212, 168, 82, 0.15)',

    // 模态框专用色
    modalBg: '#1a1a1d',
    modalOverlay: 'rgba(0, 0, 0, 0.75)',

    // 兼容旧属性名（别名）
    bgSecondary: '#141416',              // 对应 bgElevated
    bgTertiary: '#1a1a1d',               // 对应 bgContainer
    bgDark: '#0d0d0f',                   // 对应 bgBase
    text: '#f0f0f2',                     // 对应 textPrimary
    gold: '#d4a852',                     // 对应 goldPrimary
    dark: '#0d0d0f',                     // 对应 bgBase
    borderColor: 'rgba(255, 255, 255, 0.08)',  // 对应 borderPrimary
    border: 'rgba(255, 255, 255, 0.08)', // 对应 borderPrimary
    buttonText: '#f0f0f2',               // 对应 textPrimary

    // 额外的旧属性（别名）
    background: '#0d0d0f',               // 对应 bgBase
    bgDarker: '#0a0a0c',                 // 更深的背景色
    cardBg: '#1a1a1d',                   // 对应 bgContainer
    goldAlt: '#e8c780',                  // 对应 goldLight
    red: '#ff4d4f',                      // 对应 error
    redLight: '#ff7875',                 // 红色的浅色版本
    secondaryText: '#a0a0a8',            // 对应 textSecondary
    sidebarBg: '#141416',                // 对应 bgElevated
    tertiaryText: '#6a6a72',             // 对应 textTertiary
    textMuted: '#6a6a72',                // 对应 textTertiary
}

/**
 * 亮色模式颜色配置
 */
export const LIGHT_COLORS: ThemeColorConfig = {
    // 背景色系
    bgBase: '#f5f5f7',
    bgElevated: '#ffffff',
    bgContainer: '#ffffff',
    bgSpotlight: '#fafafa',

    // 金色强调
    goldPrimary: '#b08d3e',
    goldLight: '#c9a654',
    goldDark: '#8a6d2e',
    goldGlow: 'rgba(176, 141, 62, 0.15)',

    // 文字色系
    textPrimary: '#1a1a1d',
    textSecondary: '#6a6a72',
    textTertiary: '#a0a0a8',
    textGold: '#b08d3e',

    // 边框与分割
    borderPrimary: 'rgba(0, 0, 0, 0.12)',
    borderSecondary: 'rgba(0, 0, 0, 0.06)',
    borderGold: 'rgba(176, 141, 62, 0.3)',

    // 填充色系
    fill: 'rgba(0, 0, 0, 0.06)',
    fillSecondary: 'rgba(0, 0, 0, 0.04)',

    // 功能色
    success: '#52c41a',
    warning: '#faad14',
    error: '#ff4d4f',
    info: '#1890ff',

    // 金色渐变
    goldGradient: 'linear-gradient(135deg, #b08d3e 0%, #8a6d2e 100%)',
    goldGradientHover: 'linear-gradient(135deg, #c9a654 0%, #b08d3e 100%)',

    // 阴影
    shadowSm: '0 2px 8px rgba(0, 0, 0, 0.08)',
    shadowMd: '0 4px 16px rgba(0, 0, 0, 0.1)',
    shadowLg: '0 8px 32px rgba(0, 0, 0, 0.12)',
    shadowGold: '0 0 20px rgba(176, 141, 62, 0.12)',

    // 模态框专用色
    modalBg: '#ffffff',
    modalOverlay: 'rgba(0, 0, 0, 0.45)',

    // 兼容旧属性名（别名）
    bgSecondary: '#ffffff',              // 对应 bgElevated
    bgTertiary: '#ffffff',               // 对应 bgContainer
    bgDark: '#f5f5f7',                   // 对应 bgBase
    text: '#1a1a1d',                     // 对应 textPrimary
    gold: '#b08d3e',                     // 对应 goldPrimary
    dark: '#f5f5f7',                     // 对应 bgBase
    borderColor: 'rgba(0, 0, 0, 0.12)',  // 对应 borderPrimary
    border: 'rgba(0, 0, 0, 0.12)',       // 对应 borderPrimary
    buttonText: '#1a1a1d',               // 对应 textPrimary

    // 额外的旧属性（别名）
    background: '#f5f5f7',               // 对应 bgBase
    bgDarker: '#e8e8ea',                 // 更深的背景色
    cardBg: '#ffffff',                   // 对应 bgContainer
    goldAlt: '#c9a654',                  // 对应 goldLight
    red: '#ff4d4f',                      // 对应 error
    redLight: '#ff7875',                 // 红色的浅色版本
    secondaryText: '#6a6a72',            // 对应 textSecondary
    sidebarBg: '#ffffff',                // 对应 bgElevated
    tertiaryText: '#a0a0a8',             // 对应 textTertiary
    textMuted: '#a0a0a8',                // 对应 textTertiary
}

/**
 * RGBA 颜色基础值配置
 */
export const DARK_RGBA_COLORS: RgbaColorMap = {
    gold: '212, 168, 82',
    white: '255, 255, 255',
    black: '0, 0, 0',
    red: '255, 77, 79',
    bgContainer: '26, 26, 29',
}

export const LIGHT_RGBA_COLORS: RgbaColorMap = {
    gold: '176, 141, 62',
    white: '255, 255, 255',
    black: '0, 0, 0',
    red: '255, 77, 79',
    bgContainer: '255, 255, 255',
}
