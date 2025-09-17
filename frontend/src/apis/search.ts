/**
 * 搜索功能相关API
 */
import { request } from "../utils/requests"

export interface SearchRequest {
  query: string
  search_type?: string
  sources?: string[]
  page?: number
  page_size?: number
  is_hd?: boolean
  is_zh?: boolean
  is_uncensored?: boolean
  date_from?: string
  date_to?: string
  min_rating?: number
  max_rating?: number
  sort_by?: string
  sort_order?: string
}

export interface QuickSearchRequest {
  query: string
  search_type?: string
  limit?: number
}

export interface SearchSuggestionRequest {
  query: string
  limit?: number
  suggestion_types?: string[]
}

export interface SearchHistoryRequest {
  limit?: number
  search_type?: string
}

// 统一搜索接口
export const unifiedSearch = (data: SearchRequest) => {
  return request.post('/search/unified', data)
}

// 快速搜索接口（仅本地搜索）
export const quickSearch = (data: QuickSearchRequest) => {
  return request.post('/search/quick', data)
}

// 获取搜索建议
export const getSearchSuggestions = (query: string, limit: number = 10) => {
  return request.get(`/search/suggestions?query=${encodeURIComponent(query)}&limit=${limit}`)
}

// 获取搜索历史
export const getSearchHistory = (limit: number = 50, searchType?: string) => {
  const params = new URLSearchParams({ limit: limit.toString() })
  if (searchType) {
    params.append('search_type', searchType)
  }
  return request.get(`/search/history?${params}`)
}

// 清除搜索历史
export const clearSearchHistory = () => {
  return request.delete('/search/history')
}

// 获取热门搜索
export const getHotSearches = (limit: number = 10) => {
  return request.get(`/search/hot?limit=${limit}`)
}

// 获取搜索统计
export const getSearchStatistics = () => {
  return request.get('/search/statistics')
}

// 兼容性接口：演员搜索
export const searchActor = (actorName: string, force: boolean = true) => {
  return request.get(`/search/actor?actor_name=${encodeURIComponent(actorName)}&force=${force}`)
}

// 兼容性接口：视频搜索
export const searchVideo = (num: string) => {
  return request.get(`/search/video?num=${encodeURIComponent(num)}`)
}

// 增强演员搜索
export const searchActorsEnhanced = (
  query: string,
  source: string = 'local',
  page: number = 1,
  pageSize: number = 20
) => {
  return request.get(`/search/actors/search?query=${encodeURIComponent(query)}&source=${source}&page=${page}&page_size=${pageSize}`)
}

// 获取所有演员列表（增强版）
export const getAllActorsEnhanced = (
  force: boolean = false,
  page: number = 1,
  pageSize: number = 50
) => {
  return request.get(`/search/actors/all?force=${force}&page=${page}&page_size=${pageSize}`)
}

// 获取缓存信息
export const getCacheInfo = () => {
  return request.get('/search/cache/info')
}

// 清除搜索缓存
export const clearSearchCache = (cacheType?: string) => {
  const params = cacheType ? `?cache_type=${cacheType}` : ''
  return request.delete(`/search/cache${params}`)
}

// 搜索建议相关
export interface SearchSuggestion {
  value: string
  type: string
  count?: number
}

// 热门搜索项
export interface HotSearchItem {
  query: string
  search_count: number
  daily_count: number
  weekly_count: number
  trend_score: number
}

// 搜索历史项
export interface SearchHistoryItem {
  id: number
  query: string
  search_type: string
  result_count: number
  created_at: string
}

// 搜索结果项
export interface SearchResultItem {
  result_type: string
  source?: string
  title?: string
  num?: string
  cover?: string
  url?: string
  actors?: string[]
  studio?: string
  publisher?: string
  rating?: number
  premiered?: string
  runtime?: string
  tags?: string[]
  is_hd?: boolean
  is_zh?: boolean
  is_uncensored?: boolean
  name?: string
  thumb?: string
  extra_data?: any
}

// 搜索结果数据
export interface SearchResultsData {
  query: string
  total: number
  page: number
  page_size: number
  search_time: number
  results: {
    local_videos: SearchResultItem[]
    local_actors: SearchResultItem[]
    web_videos: SearchResultItem[]
    web_actors: SearchResultItem[]
  }
  suggestions: string[]
}

// 搜索统计数据
export interface SearchStatistics {
  total_searches: number
  unique_queries: number
  avg_response_time: number
  top_searches: HotSearchItem[]
  search_trends: any[]
}

export default {
  unifiedSearch,
  quickSearch,
  getSearchSuggestions,
  getSearchHistory,
  clearSearchHistory,
  getHotSearches,
  getSearchStatistics,
  searchActor,
  searchVideo,
  searchActorsEnhanced,
  getAllActorsEnhanced,
  getCacheInfo,
  clearSearchCache
}