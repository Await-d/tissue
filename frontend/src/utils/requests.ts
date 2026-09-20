import Axios, { type AxiosInstance, type AxiosRequestConfig } from "axios";
import configs from "../configs";
import { message } from "antd";


interface RequestConfigExt<D = any> extends AxiosRequestConfig<D> {
    rawResponse?: boolean
    silentError?: boolean
}

interface RequestInstance extends AxiosInstance {
    request<T = any, R = T, D = any>(config: RequestConfigExt<D>): Promise<R>
    get<T = any, R = T, D = any>(url: string, config?: RequestConfigExt<D>): Promise<R>
    delete<T = any, R = T, D = any>(url: string, config?: RequestConfigExt<D>): Promise<R>
    post<T = any, R = T, D = any>(url: string, data?: D, config?: RequestConfigExt<D>): Promise<R>
    put<T = any, R = T, D = any>(url: string, data?: D, config?: RequestConfigExt<D>): Promise<R>
    patch<T = any, R = T, D = any>(url: string, data?: D, config?: RequestConfigExt<D>): Promise<R>
}

type TokenGetter = () => string | undefined
type UnauthorizedHandler = () => void

let getToken: TokenGetter = () => undefined
let onUnauthorized: UnauthorizedHandler = () => {}
let unauthorizedHandled = false

/**
 * 请求层依赖注入：避免 requests 反向依赖 models，打断 models/apis/requests 循环引用。
 * 在应用启动时（main.tsx）调用一次完成装配。
 */
export function configureRequest(opts: { getToken?: TokenGetter; onUnauthorized?: UnauthorizedHandler }) {
    if (opts.getToken) getToken = opts.getToken
    if (opts.onUnauthorized) onUnauthorized = opts.onUnauthorized
}

export const request = Axios.create({
    baseURL: configs.BASE_API
}) as RequestInstance

request.interceptors.request.use(request => {
    const token = getToken()
    if (token) {
        request.headers['Authorization'] = `Bearer ${token}`
    }
    return request
})

request.interceptors.response.use(response => {
    // 成功响应代表会话仍然有效，重置 401 去重标记，保证后续会话的 401 仍能触发登出。
    unauthorizedHandled = false
    // 默认只返回 data。少数接口需要读响应头（如榜单的 X-Data-Stale），
    // 可在请求配置里传 rawResponse: true 拿到完整响应。
    if ((response.config as any)?.rawResponse) {
        return response as any
    }
    return response.data
}, error => {
    const silentError = (error.config as RequestConfigExt)?.silentError === true
    if (!error.response) {
        console.error('网络错误:', error.message);
        if (!silentError) {
            message.error(`网络错误: ${error.message}`);
        }
        return Promise.reject(error);
    }

    if (error.response.status === 401) {
        // 并发请求同时 401 时只触发一次登出（logout 内部会 router.invalidate）。
        if (!unauthorizedHandled) {
            unauthorizedHandled = true
            onUnauthorized()
        }
    } else if (error.response.data) {
        let errorMsg: string;
        const detail = error.response.data?.detail;
        if (Array.isArray(detail)) {
            // FastAPI/Pydantic validation error format: [{type, loc, msg, input}]
            errorMsg = detail.map((e: { msg?: string }) => e.msg || '').filter(Boolean).join('; ') || '请求参数错误';
        } else if (typeof detail === 'object' && detail !== null) {
            errorMsg = detail.msg || JSON.stringify(detail);
        } else {
            errorMsg = detail || error.response.data?.message || JSON.stringify(error.response.data);
        }
        if (!silentError) {
            message.error(errorMsg)
        }
    }
    return Promise.reject(error)
})
