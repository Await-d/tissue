/*
 * @Author: Await
 * @Date: 2025-05-24 17:05:38
 * @LastEditors: Await
 * @LastEditTime: 2025-05-26 16:49:02
 * @Description: TISSUE+ 根路由 - 电影美学主题配置
 */
import React, { useEffect } from 'react';
import zhCN from "antd/lib/locale/zh_CN";
import dayjs from "dayjs";
import localizedFormat from 'dayjs/plugin/localizedFormat';
import relativeTime from "dayjs/plugin/relativeTime";
import 'dayjs/locale/zh-cn'
import { useTheme } from "ahooks";
import { useSelector } from "react-redux";

import { ConfigProvider, theme, App as AntdApp } from "antd";
import { RootState } from "../models";
import { createRootRouteWithContext, Outlet } from "@tanstack/react-router";


dayjs.extend(relativeTime)
dayjs.extend(localizedFormat)
dayjs.locale('zh-cn')

interface MyRouteContext {
    userToken?: string
}

export const Route = createRootRouteWithContext<MyRouteContext>()({
    component: App
})

// 电影美学主题 - 暗色版本（深灰 + 金色点缀）
const darkTheme = {
    // 色彩令牌
    colorPrimary: '#d4a852',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#ff4d4f',
    colorInfo: '#1890ff',
    colorLink: '#d4a852',

    // 背景色系
    colorBgBase: '#0d0d0f',
    colorBgContainer: '#1a1a1d',
    colorBgElevated: '#222226',
    colorBgLayout: '#0d0d0f',
    colorBgSpotlight: '#2a2a2e',
    colorBgMask: 'rgba(0, 0, 0, 0.6)',

    // 文字色系
    colorText: '#f0f0f2',
    colorTextSecondary: '#a0a0a8',
    colorTextTertiary: '#6a6a72',
    colorTextQuaternary: '#4a4a52',

    // 边框色系
    colorBorder: 'rgba(255, 255, 255, 0.08)',
    colorBorderSecondary: 'rgba(255, 255, 255, 0.04)',

    // 填充色系
    colorFill: 'rgba(255, 255, 255, 0.06)',
    colorFillSecondary: 'rgba(255, 255, 255, 0.04)',
    colorFillTertiary: 'rgba(255, 255, 255, 0.02)',
    colorFillQuaternary: 'rgba(255, 255, 255, 0.01)',

    // 圆角
    borderRadius: 10,
    borderRadiusLG: 14,
    borderRadiusSM: 6,
    borderRadiusXS: 4,

    // 阴影
    boxShadow: '0 4px 16px rgba(0, 0, 0, 0.4)',
    boxShadowSecondary: '0 2px 8px rgba(0, 0, 0, 0.3)',

    // 字体
    fontFamily: "'SF Pro Text', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    fontSize: 14,
    fontSizeHeading1: 38,
    fontSizeHeading2: 30,
    fontSizeHeading3: 24,
    fontSizeHeading4: 20,
    fontSizeHeading5: 16,

    // 线高
    lineHeight: 1.5714285714285714,
    lineHeightLG: 1.5,
    lineHeightSM: 1.6666666666666667,

    // 动画
    motionDurationFast: '150ms',
    motionDurationMid: '250ms',
    motionDurationSlow: '400ms',
    motionEaseInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',

    // 间距
    padding: 16,
    paddingLG: 24,
    paddingSM: 12,
    paddingXS: 8,
    paddingXXS: 4,
    margin: 16,
    marginLG: 24,
    marginSM: 12,
    marginXS: 8,
    marginXXS: 4,

    // 控件尺寸
    controlHeight: 36,
    controlHeightLG: 44,
    controlHeightSM: 28,

    // 其他
    wireframe: false,
}

// 电影美学主题 - 亮色版本（浅灰 + 金色点缀）
const lightTheme = {
    // 色彩令牌
    colorPrimary: '#b08d3e',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#ff4d4f',
    colorInfo: '#1890ff',
    colorLink: '#b08d3e',

    // 背景色系
    colorBgBase: '#f5f5f7',
    colorBgContainer: '#ffffff',
    colorBgElevated: '#ffffff',
    colorBgLayout: '#f0f0f2',
    colorBgSpotlight: '#fafafa',
    colorBgMask: 'rgba(0, 0, 0, 0.45)',

    // 文字色系
    colorText: '#1a1a1d',
    colorTextSecondary: '#6a6a72',
    colorTextTertiary: '#a0a0a8',
    colorTextQuaternary: '#c0c0c8',

    // 边框色系
    colorBorder: 'rgba(0, 0, 0, 0.12)',
    colorBorderSecondary: 'rgba(0, 0, 0, 0.06)',

    // 填充色系
    colorFill: 'rgba(0, 0, 0, 0.06)',
    colorFillSecondary: 'rgba(0, 0, 0, 0.04)',
    colorFillTertiary: 'rgba(0, 0, 0, 0.02)',
    colorFillQuaternary: 'rgba(0, 0, 0, 0.01)',

    // 圆角
    borderRadius: 10,
    borderRadiusLG: 14,
    borderRadiusSM: 6,
    borderRadiusXS: 4,

    // 阴影
    boxShadow: '0 4px 16px rgba(0, 0, 0, 0.08)',
    boxShadowSecondary: '0 2px 8px rgba(0, 0, 0, 0.06)',

    // 字体
    fontFamily: "'SF Pro Text', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    fontSize: 14,
    fontSizeHeading1: 38,
    fontSizeHeading2: 30,
    fontSizeHeading3: 24,
    fontSizeHeading4: 20,
    fontSizeHeading5: 16,

    // 线高
    lineHeight: 1.5714285714285714,
    lineHeightLG: 1.5,
    lineHeightSM: 1.6666666666666667,

    // 动画
    motionDurationFast: '150ms',
    motionDurationMid: '250ms',
    motionDurationSlow: '400ms',
    motionEaseInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',

    // 间距
    padding: 16,
    paddingLG: 24,
    paddingSM: 12,
    paddingXS: 8,
    paddingXXS: 4,
    margin: 16,
    marginLG: 24,
    marginSM: 12,
    marginXS: 8,
    marginXXS: 4,

    // 控件尺寸
    controlHeight: 36,
    controlHeightLG: 44,
    controlHeightSM: 28,

    // 其他
    wireframe: false,
}

// 暗色组件级别定制
const darkComponentTokens = {
    Layout: {
        headerPadding: '0 16px',
        headerBg: 'transparent',
        bodyBg: '#0d0d0f',
        siderBg: '#0d0d0f',
        footerBg: 'transparent',
    },
    Menu: {
        activeBarBorderWidth: 0,
        itemBg: 'transparent',
        itemColor: '#a0a0a8',
        itemHoverColor: '#f0f0f2',
        itemHoverBg: 'rgba(212, 168, 82, 0.08)',
        itemSelectedColor: '#d4a852',
        itemSelectedBg: 'rgba(212, 168, 82, 0.12)',
        groupTitleColor: '#6a6a72',
        subMenuItemBg: 'transparent',
        darkItemBg: 'transparent',
        darkItemColor: '#a0a0a8',
        darkItemHoverColor: '#f0f0f2',
        darkItemHoverBg: 'rgba(212, 168, 82, 0.08)',
        darkItemSelectedColor: '#d4a852',
        darkItemSelectedBg: 'rgba(212, 168, 82, 0.12)',
    },
    Card: {
        colorBgContainer: '#1a1a1d',
        colorBorderSecondary: 'rgba(255, 255, 255, 0.08)',
        paddingLG: 20,
    },
    Button: {
        primaryColor: '#0d0d0f',
        defaultBg: '#1a1a1d',
        defaultColor: '#f0f0f2',
        defaultBorderColor: 'rgba(255, 255, 255, 0.08)',
        defaultHoverBg: '#222226',
        defaultHoverColor: '#d4a852',
        defaultHoverBorderColor: 'rgba(212, 168, 82, 0.3)',
        defaultActiveBg: '#2a2a2e',
        defaultActiveBorderColor: 'rgba(212, 168, 82, 0.5)',
        textHoverBg: 'rgba(212, 168, 82, 0.08)',
    },
    Input: {
        colorBgContainer: '#1a1a1d',
        colorBorder: 'rgba(255, 255, 255, 0.08)',
        hoverBorderColor: 'rgba(212, 168, 82, 0.3)',
        activeBorderColor: '#d4a852',
        activeShadow: '0 0 0 2px rgba(212, 168, 82, 0.1)',
    },
    Select: {
        colorBgContainer: '#1a1a1d',
        colorBorder: 'rgba(255, 255, 255, 0.08)',
        optionSelectedBg: 'rgba(212, 168, 82, 0.12)',
        optionActiveBg: 'rgba(212, 168, 82, 0.08)',
        selectorBg: '#1a1a1d',
    },
    Table: {
        headerBg: '#141416',
        headerColor: '#a0a0a8',
        rowHoverBg: 'rgba(212, 168, 82, 0.04)',
        rowSelectedBg: 'rgba(212, 168, 82, 0.08)',
        rowSelectedHoverBg: 'rgba(212, 168, 82, 0.12)',
        borderColor: 'rgba(255, 255, 255, 0.04)',
    },
    Modal: {
        contentBg: '#1a1a1d',
        headerBg: '#1a1a1d',
        footerBg: '#1a1a1d',
        titleColor: '#f0f0f2',
    },
    Drawer: {
        colorBgElevated: '#1a1a1d',
    },
    Dropdown: {
        colorBgElevated: '#1a1a1d',
        controlItemBgHover: 'rgba(212, 168, 82, 0.08)',
        controlItemBgActive: 'rgba(212, 168, 82, 0.12)',
    },
    Rate: {
        starSize: 15,
        starColor: '#d4a852',
    },
    Tag: {
        defaultBg: '#222226',
        defaultColor: '#a0a0a8',
    },
    Tabs: {
        itemColor: '#a0a0a8',
        itemHoverColor: '#f0f0f2',
        itemSelectedColor: '#d4a852',
        inkBarColor: '#d4a852',
    },
    Segmented: {
        itemColor: '#a0a0a8',
        itemHoverColor: '#f0f0f2',
        itemSelectedColor: '#d4a852',
        itemSelectedBg: 'rgba(212, 168, 82, 0.12)',
        trackBg: '#141416',
    },
    Pagination: {
        itemBg: 'transparent',
        itemActiveBg: 'rgba(212, 168, 82, 0.12)',
    },
    Tooltip: {
        colorBgSpotlight: '#2a2a2e',
    },
    Popover: {
        colorBgElevated: '#1a1a1d',
    },
    FloatButton: {
        colorBgElevated: '#1a1a1d',
    },
    Badge: {
        colorBgContainer: '#d4a852',
        colorError: '#ff4d4f',
    },
    Empty: {
        colorText: '#6a6a72',
        colorTextDisabled: '#4a4a52',
    },
    Skeleton: {
        gradientFromColor: '#222226',
        gradientToColor: '#1a1a1d',
    },
    Spin: {
        colorPrimary: '#d4a852',
    },
    Message: {
        contentBg: '#1a1a1d',
    },
    Notification: {
        colorBgElevated: '#1a1a1d',
    },
    Progress: {
        defaultColor: '#d4a852',
        remainingColor: '#222226',
    },
    Slider: {
        trackBg: '#d4a852',
        trackHoverBg: '#e8c780',
        railBg: '#222226',
        railHoverBg: '#2a2a2e',
        handleColor: '#d4a852',
        handleActiveColor: '#e8c780',
    },
    Switch: {
        colorPrimary: '#d4a852',
        colorPrimaryHover: '#e8c780',
    },
    Checkbox: {
        colorPrimary: '#d4a852',
        colorPrimaryHover: '#e8c780',
    },
    Radio: {
        colorPrimary: '#d4a852',
        colorPrimaryHover: '#e8c780',
    },
    Form: {
        labelColor: '#a0a0a8',
    },
    Divider: {
        colorSplit: 'rgba(255, 255, 255, 0.06)',
    },
    List: {
        colorBorder: 'rgba(255, 255, 255, 0.04)',
    },
    Collapse: {
        headerBg: '#141416',
        contentBg: '#1a1a1d',
    },
    Timeline: {
        dotBg: '#d4a852',
        tailColor: 'rgba(255, 255, 255, 0.08)',
    },
    Tree: {
        nodeSelectedBg: 'rgba(212, 168, 82, 0.12)',
        nodeHoverBg: 'rgba(212, 168, 82, 0.08)',
    },
}

// 亮色组件级别定制
const lightComponentTokens = {
    Layout: {
        headerPadding: '0 16px',
        headerBg: 'transparent',
        bodyBg: '#f0f0f2',
        siderBg: '#ffffff',
        footerBg: 'transparent',
    },
    Menu: {
        activeBarBorderWidth: 0,
        itemBg: 'transparent',
        itemColor: '#6a6a72',
        itemHoverColor: '#1a1a1d',
        itemHoverBg: 'rgba(176, 141, 62, 0.08)',
        itemSelectedColor: '#b08d3e',
        itemSelectedBg: 'rgba(176, 141, 62, 0.12)',
        groupTitleColor: '#a0a0a8',
        subMenuItemBg: 'transparent',
    },
    Card: {
        colorBgContainer: '#ffffff',
        colorBorderSecondary: 'rgba(0, 0, 0, 0.06)',
        paddingLG: 20,
    },
    Button: {
        primaryColor: '#ffffff',
        defaultBg: '#ffffff',
        defaultColor: '#1a1a1d',
        defaultBorderColor: 'rgba(0, 0, 0, 0.12)',
        defaultHoverBg: '#fafafa',
        defaultHoverColor: '#b08d3e',
        defaultHoverBorderColor: 'rgba(176, 141, 62, 0.3)',
        defaultActiveBg: '#f5f5f5',
        defaultActiveBorderColor: 'rgba(176, 141, 62, 0.5)',
        textHoverBg: 'rgba(176, 141, 62, 0.08)',
    },
    Input: {
        colorBgContainer: '#ffffff',
        colorBorder: 'rgba(0, 0, 0, 0.12)',
        hoverBorderColor: 'rgba(176, 141, 62, 0.3)',
        activeBorderColor: '#b08d3e',
        activeShadow: '0 0 0 2px rgba(176, 141, 62, 0.1)',
    },
    Select: {
        colorBgContainer: '#ffffff',
        colorBorder: 'rgba(0, 0, 0, 0.12)',
        optionSelectedBg: 'rgba(176, 141, 62, 0.12)',
        optionActiveBg: 'rgba(176, 141, 62, 0.08)',
        selectorBg: '#ffffff',
    },
    Table: {
        headerBg: '#fafafa',
        headerColor: '#6a6a72',
        rowHoverBg: 'rgba(176, 141, 62, 0.04)',
        rowSelectedBg: 'rgba(176, 141, 62, 0.08)',
        rowSelectedHoverBg: 'rgba(176, 141, 62, 0.12)',
        borderColor: 'rgba(0, 0, 0, 0.06)',
    },
    Modal: {
        contentBg: '#ffffff',
        headerBg: '#ffffff',
        footerBg: '#ffffff',
        titleColor: '#1a1a1d',
    },
    Drawer: {
        colorBgElevated: '#ffffff',
    },
    Dropdown: {
        colorBgElevated: '#ffffff',
        controlItemBgHover: 'rgba(176, 141, 62, 0.08)',
        controlItemBgActive: 'rgba(176, 141, 62, 0.12)',
    },
    Rate: {
        starSize: 15,
        starColor: '#b08d3e',
    },
    Tag: {
        defaultBg: '#f5f5f5',
        defaultColor: '#6a6a72',
    },
    Tabs: {
        itemColor: '#6a6a72',
        itemHoverColor: '#1a1a1d',
        itemSelectedColor: '#b08d3e',
        inkBarColor: '#b08d3e',
    },
    Segmented: {
        itemColor: '#6a6a72',
        itemHoverColor: '#1a1a1d',
        itemSelectedColor: '#b08d3e',
        itemSelectedBg: 'rgba(176, 141, 62, 0.12)',
        trackBg: '#f5f5f5',
    },
    Pagination: {
        itemBg: 'transparent',
        itemActiveBg: 'rgba(176, 141, 62, 0.12)',
    },
    Tooltip: {
        colorBgSpotlight: '#1a1a1d',
    },
    Popover: {
        colorBgElevated: '#ffffff',
    },
    FloatButton: {
        colorBgElevated: '#ffffff',
    },
    Badge: {
        colorBgContainer: '#b08d3e',
        colorError: '#ff4d4f',
    },
    Empty: {
        colorText: '#a0a0a8',
        colorTextDisabled: '#c0c0c8',
    },
    Skeleton: {
        gradientFromColor: '#f5f5f5',
        gradientToColor: '#e8e8e8',
    },
    Spin: {
        colorPrimary: '#b08d3e',
    },
    Message: {
        contentBg: '#ffffff',
    },
    Notification: {
        colorBgElevated: '#ffffff',
    },
    Progress: {
        defaultColor: '#b08d3e',
        remainingColor: '#f0f0f0',
    },
    Slider: {
        trackBg: '#b08d3e',
        trackHoverBg: '#c9a654',
        railBg: '#e8e8e8',
        railHoverBg: '#d9d9d9',
        handleColor: '#b08d3e',
        handleActiveColor: '#c9a654',
    },
    Switch: {
        colorPrimary: '#b08d3e',
        colorPrimaryHover: '#c9a654',
    },
    Checkbox: {
        colorPrimary: '#b08d3e',
        colorPrimaryHover: '#c9a654',
    },
    Radio: {
        colorPrimary: '#b08d3e',
        colorPrimaryHover: '#c9a654',
    },
    Form: {
        labelColor: '#6a6a72',
    },
    Divider: {
        colorSplit: 'rgba(0, 0, 0, 0.06)',
    },
    List: {
        colorBorder: 'rgba(0, 0, 0, 0.06)',
    },
    Collapse: {
        headerBg: '#fafafa',
        contentBg: '#ffffff',
    },
    Timeline: {
        dotBg: '#b08d3e',
        tailColor: 'rgba(0, 0, 0, 0.08)',
    },
    Tree: {
        nodeSelectedBg: 'rgba(176, 141, 62, 0.12)',
        nodeHoverBg: 'rgba(176, 141, 62, 0.08)',
    },
}

function App() {

    const themeMode = useSelector((state: RootState) => state.app?.themeMode)
    const { theme: systemTheme } = useTheme()

    // 判断当前是否为暗色模式
    const isDark = () => {
        if (themeMode === 'dark') return true
        if (themeMode === 'light') return false
        // system 模式：根据系统主题判断
        return systemTheme === 'dark'
    }

    // 根据当前主题模式返回对应的算法
    const getAlgorithm = () => {
        return isDark() ? theme.darkAlgorithm : theme.defaultAlgorithm
    }

    // 根据当前主题模式返回对应的 token 配置
    const getThemeTokens = () => {
        return isDark() ? darkTheme : lightTheme
    }

    // 根据当前主题模式返回对应的组件配置
    const getComponentTokens = () => {
        return isDark() ? darkComponentTokens : lightComponentTokens
    }

    // 同步主题到 HTML 元素，以便 CSS 变量能正确切换
    useEffect(() => {
        const currentTheme = isDark() ? 'dark' : 'light'
        document.documentElement.setAttribute('data-theme', currentTheme)
    }, [themeMode, systemTheme])

    return (
        <ConfigProvider
            locale={zhCN}
            theme={{
                algorithm: getAlgorithm(),
                token: getThemeTokens(),
                components: getComponentTokens(),
            }}>
            <AntdApp>
                <Outlet />
            </AntdApp>
        </ConfigProvider>
    );
}
