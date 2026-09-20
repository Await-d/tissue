/**
 * 主题颜色 Hook
 * 根据当前主题模式动态返回对应的颜色值,用于内联样式
 * 颜色由 ThemeColorsProvider 统一计算并通过 Context 下发
 */
import { createContext, useContext } from 'react'
import {
    DARK_COLORS,
    LIGHT_COLORS,
    DARK_RGBA_COLORS,
    LIGHT_RGBA_COLORS,
    ThemeColorConfig
} from '@/config/colors.config'

/**
 * 主题颜色 Hook 返回类型
 */
export interface ThemeColors extends ThemeColorConfig {
    /**
     * 工具方法：生成 rgba 颜色（用于动态透明度）
     * @param color - 颜色类型: 'gold' | 'white' | 'black' | 'red' | 'green' | 'blue' | 'warning' | 'bgContainer'
     * @param alpha - 透明度值 (0-1)
     * @returns rgba 颜色字符串
     */
    rgba: (color: 'gold' | 'white' | 'black' | 'red' | 'green' | 'blue' | 'warning' | 'bgContainer', alpha: number) => string
}

/**
 * 纯函数：根据是否为暗色模式计算完整的主题颜色对象
 * @param isDark - 是否为暗色模式
 * @returns 主题颜色对象
 */
export const computeThemeColors = (isDark: boolean): ThemeColors => {
    const baseColors = isDark ? DARK_COLORS : LIGHT_COLORS
    const rgbaColors = isDark ? DARK_RGBA_COLORS : LIGHT_RGBA_COLORS

    return {
        ...baseColors,
        // 工具方法：生成 rgba 颜色（用于动态透明度）
        rgba: (color: 'gold' | 'white' | 'black' | 'red' | 'green' | 'blue' | 'warning' | 'bgContainer', alpha: number) => {
            return `rgba(${rgbaColors[color]}, ${alpha})`
        },
        // 模态框专用颜色（直接暴露）
        modalBg: baseColors.modalBg,
        modalOverlay: baseColors.modalOverlay,
    }
}

/**
 * 亮色模式静态默认值（模块级常量）
 * 若组件在 ThemeColorsProvider 之外渲染,则作为兜底值,避免崩溃
 */
const LIGHT_DEFAULT: ThemeColors = computeThemeColors(false)

/**
 * 主题颜色 Context
 * 由 ThemeColorsProvider 提供,useThemeColors 消费
 */
export const ThemeColorsContext = createContext<ThemeColors>(LIGHT_DEFAULT)

/**
 * 主题颜色 Hook
 * 从 ThemeColorsContext 读取,不再在调用点各自订阅 redux / matchMedia
 */
export const useThemeColors = (): ThemeColors => {
    return useContext(ThemeColorsContext)
}
