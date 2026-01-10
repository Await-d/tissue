import { request } from '@/utils/requests'

// 类型定义
export interface FilterSettings {
  id?: number
  min_file_size_mb: number
  max_file_size_mb?: number | null
  allowed_extensions?: string[] | null
  blocked_extensions?: string[] | null
  min_seed_count?: number | null
  max_total_size_gb?: number | null
  enable_smart_filter: boolean
  skip_sample_files: boolean
  skip_subtitle_only: boolean
  media_files_only: boolean
  include_subtitles: boolean
  is_active?: boolean
  created_at?: string
  updated_at?: string
}

export interface TorrentFileInfo {
  name: string
  path: string
  size: number
  size_mb: number
  extension: string
  is_video: boolean
  is_sample: boolean
  is_subtitle: boolean
}

export interface MagnetFilterResult {
  should_download: boolean
  total_files: number
  filtered_files: number
  filtered_size_mb: number
  filter_reason: string
  files: TorrentFileInfo[]
}

export interface TorrentFilterResult {
  success: boolean
  message: string
  original_files: number
  filtered_files: number
  filtered_size_mb: number
  files: TorrentFileInfo[]
}

export interface FilterStatistics {
  total_filtered_torrents: number
  total_saved_space_gb: number
  most_common_filtered_types: string[]
}

export interface ApiResponse<T = any> {
  success: boolean
  message: string
  data?: T
}

// 过滤设置API
export const getFilterSettings = (): Promise<ApiResponse<FilterSettings>> => {
  return request.get('/download-filter/settings')
}

export const saveFilterSettings = (settings: Omit<FilterSettings, 'id' | 'is_active' | 'created_at' | 'updated_at'>): Promise<ApiResponse> => {
  return request.post('/download-filter/settings', settings)
}

export const getDefaultSettings = (): Promise<ApiResponse<FilterSettings>> => {
  return request.get('/download-filter/default-settings')
}

export const resetToDefaultSettings = (): Promise<ApiResponse> => {
  return request.post('/download-filter/reset-settings')
}

// 过滤测试API
export const testMagnetFilter = (magnetUrl: string): Promise<ApiResponse<MagnetFilterResult>> => {
  return request.post('/download-filter/test-magnet', { magnet_url: magnetUrl })
}

export const filterTorrent = (torrentHash: string): Promise<ApiResponse<TorrentFilterResult>> => {
  return request.post('/download-filter/filter-torrent', { torrent_hash: torrentHash })
}

// 统计信息API
export const getFilterStatistics = (): Promise<ApiResponse<FilterStatistics>> => {
  return request.get('/download-filter/statistics')
}

// 清理相关API
export const previewCleanup = (torrentHash: string): Promise<ApiResponse> => {
  return request.get(`/download-filter/preview-cleanup/${torrentHash}`)
}

export const cleanupTorrent = (torrentHash: string, dryRun: boolean = true): Promise<ApiResponse> => {
  return request.post(`/download-filter/cleanup-torrent/${torrentHash}`, null, {
    params: { dry_run: dryRun }
  })
}

export const cleanupAllTorrents = (category?: string, dryRun: boolean = true): Promise<ApiResponse> => {
  return request.post('/download-filter/cleanup-all', null, {
    params: { category, dry_run: dryRun }
  })
}