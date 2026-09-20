/**
 * 设置页共享外壳（presentational shell）
 *
 * 目的：让 6 个设置页的「页头 + 卡片 + 表单 + 底部保存按钮」结构可以逐像素复用，
 * 同时允许每个页面保留自己现有的视觉差异。**本组件不迁移任何页面**，只冻结 API。
 *
 * 变体速查（按现有页面实测）：
 * | 页面          | maxWidth | headerGradient | cardBorder | saveButtonVariant  |
 * |---------------|----------|----------------|------------|--------------------|
 * | app           | '5xl'    | 'base'         | 'solid'    | 'legacy'           |
 * | download      | '5xl'    | 'base'         | 'solid'    | 'legacy'           |
 * | file          | '5xl'    | 'elevated'     | 'none'     | 'file'             |
 * | notify        | '5xl'    | 'elevated'     | 'solid'    | 'hover'            |
 * | cookiecloud   | '5xl'    | 'elevated'     | 'solid'    | 'plain'            |
 * | auto-download | '7xl'    | 'elevated'     | 'solid'    | renderSaveButton   |
 *
 * 结构复刻（与旧页面 DOM 对齐）：
 * ```
 * <div class="{maxWidth} mx-auto px-6 py-8">
 *   {beforeCard}                                  // auto-download 的统计卡片
 *   <div class="rounded-2xl shadow-2xl overflow-hidden[ border]">
 *     <div class="px-8 py-6 border-b">            // 页头（渐变随 headerGradient 变化）
 *       <h2 class="text-2xl font-bold flex items-center gap-3"> [金色竖条] {title} </h2>
 *       <p class="text-sm mt-2 ml-6">{subtitle}</p>
 *     </div>
 *     <div class="p-8">
 *       <Form form layout=vertical onFinish initialValues>
 *         {children}                              // Form.Item 等
 *         <div class={footerClassName}>{保存按钮或 renderSaveButton(saving)}</div>
 *       </Form>
 *       {afterForm}                               // auto-download 的“使用说明”
 *     </div>
 *   </div>
 * </div>
 * ```
 */
import { Button, Form, Skeleton } from 'antd'
import type { FormInstance } from 'antd'
import type { CSSProperties, ReactNode } from 'react'

import { useThemeColors } from '../../../../hooks/useThemeColors'

/** 外层容器最大宽度。'5xl' -> max-w-5xl，'7xl' -> max-w-7xl。 */
export type SettingsPageMaxWidth = '5xl' | '7xl'

/**
 * 页头渐变：
 * - 'elevated'（默认）：bgElevated -> bgContainer（file / notify / cookiecloud / auto-download）
 * - 'base'：bgBase -> bgContainer（app / download，使用旧别名 bgDark -> cardBg）
 */
export type SettingsPageHeaderGradient = 'elevated' | 'base'

/**
 * 卡片容器边框：
 * - 'solid'（默认）：`border` 类 + 内联 borderColor（notify / cookiecloud / auto-download）
 * - 'none'：不渲染 `border` 类，仅内联 borderWidth/borderColor（file.tsx 的写法；当前实际无可见边框）
 */
export type SettingsPageCardBorder = 'solid' | 'none'

/**
 * 默认保存按钮外观（文案固定为「保存设置」）：
 * - 'plain'（默认）：CookieCloud —— 192x44、goldGradient、无 hover
 * - 'hover'：Notify —— 192x44、goldGradient、hover 换 goldGradientHover + 金色辉光
 * - 'file'：File —— 192x44、goldPrimary->goldDark、金色投影、hover 换 goldLight->goldPrimary
 * - 'legacy'：App / Download —— w-48 h-11 + shadow-lg hover:shadow-xl、金色线性渐变
 */
export type SettingsPageSaveButtonVariant = 'plain' | 'hover' | 'file' | 'legacy'

export interface SettingsPageProps {
    /** 页头标题（应用设置 / 下载设置 / 文件设置 ...） */
    title: ReactNode
    /** 页头副标题（h2 下方的说明文字） */
    subtitle?: ReactNode
    /** true 时整体渲染 <Skeleton active/>，与旧页面的 loading 分支一致 */
    loading?: boolean
    /** 页面表单实例：来自 useSectionSettings().form 或 Form.useForm() */
    form: FormInstance
    /** 表单提交回调（旧页面的 onFinish） */
    onFinish: (values: Record<string, any>) => void
    /** 保存按钮 loading（旧页面的 saving） */
    saving?: boolean
    /** 表单字段（Form.Item 等），渲染在 <Form> 内部 */
    children: ReactNode
    /** 外层容器宽度，默认 '5xl'；auto-download / version 使用 '7xl' */
    maxWidth?: SettingsPageMaxWidth
    /** 页头渐变，默认 'elevated'；app / download 使用 'base' */
    headerGradient?: SettingsPageHeaderGradient
    /** 卡片边框，默认 'solid'；file 使用 'none' */
    cardBorder?: SettingsPageCardBorder
    /** 透传给 antd <Form initialValues>（auto-download 需要） */
    formInitialValues?: Record<string, any>
    /** 渲染在卡片之前的节点（auto-download 的「运行状态」统计卡片，自带 mb-6） */
    beforeCard?: ReactNode
    /** 渲染在 </Form> 之后、卡片 body 内的节点（auto-download 的「使用说明」，自带 mt-8 pt-8 border-t） */
    afterForm?: ReactNode
    /** 底部按钮容器 className，默认 'flex justify-center pt-6'；auto-download 用 'flex justify-center gap-4 pt-6 border-t' */
    footerClassName?: string
    /** 默认保存按钮外观，默认 'plain' */
    saveButtonVariant?: SettingsPageSaveButtonVariant
    /** 完全接管底部保存按钮（如 auto-download 的「保存/手动触发/测试连接/刷新统计」多按钮组合）；入参为 saving */
    renderSaveButton?: (saving: boolean) => ReactNode
}

// 用查表而不是模板字符串，确保 Tailwind 能静态扫描到 max-w-5xl / max-w-7xl。
const MAX_WIDTH_CLASS: Record<SettingsPageMaxWidth, string> = {
    '5xl': 'max-w-5xl',
    '7xl': 'max-w-7xl',
}

export function SettingsPage(props: SettingsPageProps) {
    const colors = useThemeColors()
    const {
        title,
        subtitle,
        loading = false,
        form,
        onFinish,
        saving = false,
        children,
        maxWidth = '5xl',
        headerGradient = 'elevated',
        cardBorder = 'solid',
        formInitialValues,
        beforeCard,
        afterForm,
        footerClassName = 'flex justify-center pt-6',
        saveButtonVariant = 'plain',
        renderSaveButton,
    } = props

    if (loading) {
        return <Skeleton active/>
    }

    const headerBackground = headerGradient === 'base'
        ? `linear-gradient(to right, ${colors.bgBase}, ${colors.bgContainer})`
        : `linear-gradient(to right, ${colors.bgElevated}, ${colors.bgContainer})`

    const cardStyle: CSSProperties = cardBorder === 'solid'
        ? { backgroundColor: colors.bgContainer, borderColor: colors.borderPrimary }
        : { backgroundColor: colors.bgContainer, borderColor: colors.borderPrimary, borderWidth: '1px' }

    const cardClassName = cardBorder === 'solid'
        ? 'rounded-2xl border shadow-2xl overflow-hidden'
        : 'rounded-2xl shadow-2xl overflow-hidden'

    return (
        <div className={`${MAX_WIDTH_CLASS[maxWidth]} mx-auto px-6 py-8`}>
            {beforeCard}

            <div style={cardStyle} className={cardClassName}>
                {/* 页头 */}
                <div
                    style={{ borderBottomColor: colors.borderPrimary, backgroundImage: headerBackground }}
                    className="px-8 py-6 border-b"
                >
                    <h2 style={{ color: colors.goldPrimary }} className="text-2xl font-bold flex items-center gap-3">
                        <span
                            style={{ backgroundImage: `linear-gradient(to bottom, ${colors.goldPrimary}, ${colors.goldDark})` }}
                            className="w-1.5 h-8 rounded-full"
                        ></span>
                        {title}
                    </h2>
                    {subtitle !== undefined && (
                        <p style={{ color: colors.textSecondary }} className="text-sm mt-2 ml-6">{subtitle}</p>
                    )}
                </div>

                <div className="p-8">
                    <Form
                        form={form}
                        layout={'vertical'}
                        onFinish={onFinish}
                        initialValues={formInitialValues}
                    >
                        {children}
                        <div className={footerClassName}>
                            {renderSaveButton
                                ? renderSaveButton(saving)
                                : <SettingsSaveButton saving={saving} variant={saveButtonVariant}/>}
                        </div>
                    </Form>
                    {afterForm}
                </div>
            </div>
        </div>
    )
}

interface SettingsSaveButtonProps {
    saving: boolean
    variant: SettingsPageSaveButtonVariant
}

/** 默认保存按钮：按 variant 复刻各页面现有样式，文案固定为「保存设置」。 */
function SettingsSaveButton({ saving, variant }: SettingsSaveButtonProps) {
    const colors = useThemeColors()

    if (variant === 'legacy') {
        return (
            <Button
                type={'primary'}
                size="large"
                loading={saving}
                htmlType={"submit"}
                style={{
                    background: `linear-gradient(to right, ${colors.gold}, ${colors.goldDark})`,
                    border: 0,
                    color: colors.buttonText,
                    fontWeight: 600,
                }}
                className="w-48 h-11 shadow-lg hover:shadow-xl"
            >
                保存设置
            </Button>
        )
    }

    if (variant === 'file') {
        return (
            <Button
                type={'primary'}
                size="large"
                loading={saving}
                htmlType={"submit"}
                style={{
                    width: '192px',
                    height: '44px',
                    backgroundImage: `linear-gradient(to right, ${colors.goldPrimary}, ${colors.goldDark})`,
                    borderWidth: 0,
                    color: colors.bgBase,
                    fontWeight: 'bold',
                    boxShadow: `0 8px 16px ${colors.goldPrimary}30`,
                }}
                onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundImage = `linear-gradient(to right, ${colors.goldLight}, ${colors.goldPrimary})`
                    e.currentTarget.style.boxShadow = `0 8px 16px ${colors.goldPrimary}50`
                }}
                onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundImage = `linear-gradient(to right, ${colors.goldPrimary}, ${colors.goldDark})`
                    e.currentTarget.style.boxShadow = `0 8px 16px ${colors.goldPrimary}30`
                }}
            >
                保存设置
            </Button>
        )
    }

    if (variant === 'hover') {
        return (
            <Button
                type={'primary'}
                size="large"
                loading={saving}
                htmlType={"submit"}
                style={{
                    width: '192px',
                    height: '44px',
                    background: colors.goldGradient,
                    border: 'none',
                    color: colors.bgBase,
                    fontWeight: '600',
                }}
                onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundImage = colors.goldGradientHover
                    e.currentTarget.style.boxShadow = `0 0 20px ${colors.rgba('gold', 0.2)}`
                }}
                onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundImage = colors.goldGradient
                    e.currentTarget.style.boxShadow = 'none'
                }}
            >
                保存设置
            </Button>
        )
    }

    return (
        <Button
            type={'primary'}
            size="large"
            loading={saving}
            htmlType={"submit"}
            style={{
                width: '192px',
                height: '44px',
                background: colors.goldGradient,
                border: 'none',
                color: colors.bgBase,
                fontWeight: '600',
            }}
        >
            保存设置
        </Button>
    )
}
