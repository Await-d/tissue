import { request } from '@/utils/requests'

// 类型定义
export interface AutoDownloadRule {
  id: number
  name: string
  min_rating: number
  min_comments: number
  time_range_type: 'day' | 'week' | 'month'
  time_range_value: number
  is_hd: boolean
  is_zh: boolean
  is_uncensored: boolean
  is_enabled: boolean
  created_at: string
  updated_at: string
  subscription_count?: number
  success_count?: number
}

export interface AutoDownloadSubscription {
  id: number
  rule_id: number
  rule_name?: string
  num: string
  title?: string
  rating?: number
  comments_count: number
  cover?: string
  actors?: string
  status: 'pending' | 'downloading' | 'completed' | 'failed'
  download_url?: string
  download_time?: string
  created_at: string
}

export interface AutoDownloadStatistics {
  total_rules: number
  active_rules: number
  total_subscriptions: number
  pending_subscriptions: number
  downloading_subscriptions: number
  completed_subscriptions: number
  failed_subscriptions: number
  today_subscriptions: number
  success_rate: number
}

export interface ListResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ApiResponse<T = any> {
  success: boolean
  message: string
  data?: T
}

// 规则管理API
export const getRules = (params: {
  page?: number
  page_size?: number
  is_enabled?: boolean
  name?: string
}): Promise<ListResponse<AutoDownloadRule>> => {
  return request.get('/api/auto-download/rules', { params })
}

export const createRule = (data: Omit<AutoDownloadRule, 'id' | 'created_at' | 'updated_at' | 'subscription_count' | 'success_count'>): Promise<ApiResponse> => {
  return request.post('/api/auto-download/rules', data)
}

export const updateRule = (id: number, data: Partial<AutoDownloadRule>): Promise<ApiResponse> => {
  return request.put(`/api/auto-download/rules/${id}`, data)
}

export const deleteRule = (id: number): Promise<ApiResponse> => {
  return request.delete(`/api/auto-download/rules/${id}`)
}

export const toggleRule = (id: number, enabled: boolean): Promise<ApiResponse> => {
  return request.patch(`/api/auto-download/rules/${id}/toggle`, null, {
    params: { enabled }
  })
}

// 订阅记录管理API
export const getSubscriptions = (params: {
  page?: number
  page_size?: number
  rule_id?: number
  status?: string
  num?: string
  start_date?: string
  end_date?: string
}): Promise<ListResponse<AutoDownloadSubscription>> => {
  return request.get('/api/auto-download/subscriptions', { params })
}

export const deleteSubscription = (id: number): Promise<ApiResponse> => {
  return request.delete(`/api/auto-download/subscriptions/${id}`)
}

export const batchOperation = (data: {
  ids: number[]
  action: 'delete' | 'retry' | 'pause' | 'resume'
}): Promise<ApiResponse> => {
  return request.post('/api/auto-download/subscriptions/batch', data)
}

// 统计和管理API
export const getStatistics = (): Promise<AutoDownloadStatistics> => {
  return request.get('/api/auto-download/statistics')
}

export const triggerAutoDownload = (data: {
  rule_ids?: number[]
  force?: boolean
}): Promise<ApiResponse> => {
  return request.post('/api/auto-download/trigger', data)
}

export const testRule = (id: number, limit?: number): Promise<ApiResponse> => {
  return request.post(`/api/auto-download/rules/${id}/test`, null, {
    params: { limit }
  })
}