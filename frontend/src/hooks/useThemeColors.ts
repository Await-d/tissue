/**
 * 主题颜色 Hook
 * 根据当前主题模式动态返回对应的颜色值,用于内联样式
 */
import { useMemo } from 'react'
import { useSelector } from 'react-redux'
import { useTheme } from 'ahooks'
import { RootState } from '../models'
import {
    DARK_COLORS,
    LIGHT_COLORS,
    DARK_RGBA_COLORS,
    LIGHT_RGBA_COLORS,
    ThemeColorConfig
} from '../config/colors.config'

/**
 * 主题颜色 Hook 返回类型
 */
export interface ThemeColors extends ThemeColorConfig {
    /**
     * 工具方法：生成 rgba 颜色（用于动态透明度）
     * @param color - 颜色类型: 'gold' | 'white' | 'black'
     * @param alpha - 透明度值 (0-1)
     * @returns rgba 颜色字符串
     */
    rgba: (color: 'gold' | 'white' | 'black', alpha: number) => string
}

/**
 * 主题颜色 Hook
 * 性能优化：使用 useMemo 缓存计算结果
 */
export const useThemeColors = (): ThemeColors => {
    const themeMode = useSelector((state: RootState) => state.app?.themeMode)
    const { theme: systemTheme } = useTheme()

    // 使用 useMemo 缓存 isDark 计算
    const isDark = useMemo(() => {
        if (themeMode === 'dark') return true
        if (themeMode === 'light') return false
        return systemTheme === 'dark'
    }, [themeMode, systemTheme])

    // 使用 useMemo 缓存整个颜色对象
    return useMemo(() => {
        const baseColors = isDark ? DARK_COLORS : LIGHT_COLORS
        const rgbaColors = isDark ? DARK_RGBA_COLORS : LIGHT_RGBA_COLORS

        return {
            ...baseColors,
            // 工具方法：生成 rgba 颜色（用于动态透明度）
            rgba: (color: 'gold' | 'white' | 'black', alpha: number) => {
                return `rgba(${rgbaColors[color]}, ${alpha})`
            },
            // 模态框专用颜色（直接暴露）
            modalBg: baseColors.modalBg,
            modalOverlay: baseColors.modalOverlay,
        }
    }, [isDark])
}
