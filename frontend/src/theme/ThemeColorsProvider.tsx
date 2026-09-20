/**
 * 主题颜色 Provider
 * 统一计算 isDark 并提供主题颜色,避免每个调用点各自订阅 redux / matchMedia
 */
import { useMemo, type ReactNode } from 'react'
import { useSelector } from 'react-redux'
import { useTheme } from 'ahooks'
import { RootState } from '../models'
import { computeThemeColors, ThemeColorsContext } from '../hooks/useThemeColors'

interface ThemeColorsProviderProps {
    children: ReactNode
}

/**
 * 主题颜色 Provider 组件
 * isDark 判断逻辑与 __root 的 App 保持一致
 */
export const ThemeColorsProvider = ({ children }: ThemeColorsProviderProps) => {
    const themeMode = useSelector((state: RootState) => state.app?.themeMode)
    const { theme: systemTheme } = useTheme()

    // 判断当前是否为暗色模式
    const isDark = useMemo(() => {
        if (themeMode === 'dark') return true
        if (themeMode === 'light') return false
        // system 模式：根据系统主题判断
        return systemTheme === 'dark'
    }, [themeMode, systemTheme])

    // 缓存整个颜色对象
    const colors = useMemo(() => computeThemeColors(isDark), [isDark])

    return (
        <ThemeColorsContext.Provider value={colors}>
            {children}
        </ThemeColorsContext.Provider>
    )
}
