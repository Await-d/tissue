/**
 * 请求层统一响应类型。
 * 后端统一返回信封结构：{ success, details, data, total }
 */
export interface ApiEnvelope<T = unknown> {
    success: boolean;
    details?: string | null;
    data: T;
    total?: number;
    /**
     * @deprecated 后端实际使用 details 传递消息，该字段并非后端契约。
     * 仅因既有调用点读取 `res.message` 而保留，新代码请使用 `details`。
     */
    message?: string;
}

export type ApiResponse<T = any> = ApiEnvelope<T>

export type ApiError = import('axios').AxiosError<ApiEnvelope>
