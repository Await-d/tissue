/**
 * 设置页共享上下文
 *
 * 设计目标（与旧页面行为保持兼容）：
 * - 惰性加载：Provider 挂载时**不**发请求；第一个调用 `ensureLoaded()` 的消费者才触发 GET /setting/。
 *   因此 version / download-filter 这类不消费设置配置的 Tab 不会产生任何额外请求。
 * - 幂等：`ensureLoaded()` 重复调用（含并发）只会有一个在途请求；成功后直接复用内存缓存。
 * - 本地更新：保存成功后用 `setLocal(section, data)` 更新内存配置，之后切 Tab 再挂载的页面
 *   能立即看到刚保存的值，无需回读接口。
 * - 表单回填：`useSectionSettings` 用 useLayoutEffect + appliedRef 保证「每次挂载只回填一次」，
 *   既避免先渲染空表单再闪成有值，又保留旧页面「页面/标签挂载时写一次表单」的语义。
 */
import { App, Form } from 'antd'
import type { FormInstance } from 'antd'
import {
    createContext,
    useCallback,
    useContext,
    useEffect,
    useLayoutEffect,
    useMemo,
    useRef,
    useState,
} from 'react'
import type { ReactNode } from 'react'

import * as api from '../../../../apis/setting.ts'

/** 后端返回的整份设置配置（区块名 -> 区块配置），故意保持宽松类型。 */
export type SettingsConfig = Record<string, any>

/** 单个设置区块的配置，例如 `res.app`、`res.download`。 */
export type SettingsSectionConfig = Record<string, any>

export interface SettingsContextValue {
    /** 整份设置配置；首次加载完成前为 undefined */
    config: SettingsConfig | undefined
    /** 是否有在途的 getSettings 请求 */
    loading: boolean
    /** 最近一次加载失败的错误（重新加载开始时清空） */
    error: Error | undefined
    /** 惰性、幂等地触发首次加载；并发调用共享同一个请求 */
    ensureLoaded: () => Promise<void>
    /** 强制重新拉取并覆盖内存配置 */
    refresh: () => Promise<void>
    /** 仅更新内存中某个区块的配置（保存成功后调用），不发网络请求 */
    setLocal: (section: string, data: SettingsSectionConfig) => void
}

const SettingsContext = createContext<SettingsContextValue | null>(null)

export function SettingsProvider({ children }: { children: ReactNode }) {
    const [config, setConfig] = useState<SettingsConfig | undefined>(undefined)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<Error | undefined>(undefined)

    // 成功加载过一次后，ensureLoaded 直接返回，保证幂等。
    const loadedRef = useRef(false)
    // 在途请求：并发 ensureLoaded 共享同一个 Promise。
    const inflightRef = useRef<Promise<void> | null>(null)
    // 请求序号：refresh 覆盖旧请求时，让旧请求的响应与收尾逻辑失效。
    const requestIdRef = useRef(0)

    const load = useCallback((force: boolean): Promise<void> => {
        if (!force && (loadedRef.current || inflightRef.current)) {
            return inflightRef.current ?? Promise.resolve()
        }

        const requestId = ++requestIdRef.current
        setLoading(true)
        setError(undefined)

        const promise = api
            .getSettings()
            .then((res: SettingsConfig | undefined) => {
                if (requestId !== requestIdRef.current) return
                loadedRef.current = true
                setConfig(res)
            })
            .catch((err: unknown) => {
                if (requestId !== requestIdRef.current) return
                setError(err instanceof Error ? err : new Error(String(err)))
            })
            .finally(() => {
                if (requestId !== requestIdRef.current) return
                inflightRef.current = null
                setLoading(false)
            })

        inflightRef.current = promise
        return promise
    }, [])

    const ensureLoaded = useCallback(() => load(false), [load])
    const refresh = useCallback(() => load(true), [load])

    const setLocal = useCallback((section: string, data: SettingsSectionConfig) => {
        setConfig(prev => ({ ...prev, [section]: data }))
    }, [])

    const value = useMemo<SettingsContextValue>(() => ({
        config,
        loading,
        error,
        ensureLoaded,
        refresh,
        setLocal,
    }), [config, loading, error, ensureLoaded, refresh, setLocal])

    return (
        <SettingsContext.Provider value={value}>
            {children}
        </SettingsContext.Provider>
    )
}

/** 读取设置上下文；未包裹 <SettingsProvider> 时抛出可定位的错误。 */
export function useSettingsConfig(): SettingsContextValue {
    const ctx = useContext(SettingsContext)
    if (!ctx) {
        throw new Error(
            'useSettingsConfig 必须在 <SettingsProvider> 内使用：' +
            '请确认组件渲染在 /setting 路由的 <Outlet/> 之下（见 setting/route.tsx）。'
        )
    }
    return ctx
}

/**
 * 把泛型表单值收敛为宽松的区块配置。
 * 单独抽出是为了避免在业务代码里散落 `as any`（`unknown` -> Record 是安全断言）。
 */
function asSectionConfig(value: unknown): SettingsSectionConfig {
    return value as SettingsSectionConfig
}

export interface SectionSettingsResult<T = any> {
    /** 页面表单实例，直接传给 <Form form={form}> 与 Form.Item */
    form: FormInstance<T>
    /** 配置加载中或本挂载尚未回填完成时为 true（用于显示 <Skeleton active/>） */
    loading: boolean
    /** 保存请求在途 */
    saving: boolean
    /** 保存当前区块；成功后写回内存配置并提示「设置成功」 */
    submit: (data: T) => Promise<void>
}

/**
 * 设置区块的通用表单 Hook。
 *
 * 行为等价于旧页面：
 * `Form.useForm()` + `useRequest(getSettings, { onSuccess: res => form.setFieldsValue(res.<section>) })`
 * + `useRequest(saveSetting, { manual: true, onSuccess: () => message.success('设置成功') })`
 * 的合并版本，但数据来自共享 Provider（避免每个 Tab 各拉一次 /setting/）。
 */
export function useSectionSettings<T = any>(section: string): SectionSettingsResult<T> {
    const { config, loading: configLoading, error, ensureLoaded, setLocal } = useSettingsConfig()
    const { message } = App.useApp()
    const [form] = Form.useForm()
    const [applied, setApplied] = useState(false)
    const [saving, setSaving] = useState(false)
    const appliedRef = useRef(false)

    // 惰性触发加载：只有真正消费设置区块的页面才会请求 /setting/。
    useEffect(() => {
        void ensureLoaded()
    }, [ensureLoaded])

    // useLayoutEffect 在浏览器绘制前执行：配置一到就写表单，不会先闪一帧空值。
    // appliedRef 保证每个挂载周期只写一次（保存后 setLocal / refresh 都不会重置用户正在编辑的内容）。
    useLayoutEffect(() => {
        if (appliedRef.current) return
        // 首次加载失败（error 且无 config）时也结束骨架屏，渲染空表单，
        // 与旧页面 useRequest 失败后的表现一致，避免无限 Skeleton。
        if (!config && !error) return
        appliedRef.current = true
        const sectionConfig = config?.[section]
        if (sectionConfig) {
            form.setFieldsValue(sectionConfig)
        }
        setApplied(true)
    }, [config, error, form, section])

    const submit = useCallback(async (data: T) => {
        setSaving(true)
        try {
            const values = asSectionConfig(data)
            await api.saveSetting(section, values)
            setLocal(section, values)
            message.success('设置成功')
        } catch (err) {
            // 请求层拦截器已统一提示错误；这里只补日志，保持 submit 不向外抛。
            console.error('保存设置失败:', err)
        } finally {
            setSaving(false)
        }
    }, [message, section, setLocal])

    return {
        form,
        loading: configLoading || !applied,
        saving,
        submit,
    }
}
