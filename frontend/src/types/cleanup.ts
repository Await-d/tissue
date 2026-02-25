/**
 * 清理文件相关类型定义
 */

/**
 * 清理文件信息
 */
export interface CleanupFile {
  name: string
  path: string
  size: number
  size_mb?: number
  reason?: string
}

/**
 * 清理预览数据
 */
export interface CleanupPreviewData {
  success: boolean
  files_to_delete: CleanupFile[]
  files_to_keep?: CleanupFile[]
  total_size?: string
  deleted_size_mb?: number
  kept_count?: number
}

/**
 * 单个种子清理结果
 */
export interface TorrentCleanupResult {
  hash: string
  name: string
  success: boolean
  deleted_files: number
  deleted_size_mb: number
  message: string
}

/**
 * 清理结果数据
 */
export interface CleanupResultData {
  success: boolean
  message?: string
  dry_run?: boolean
  category?: string
  total_torrents?: number
  processed_torrents?: number
  failed_torrents?: number
  total_deleted_files?: number
  total_deleted_size_bytes?: number
  total_deleted_size_mb?: number
  total_deleted_size_gb?: number
  torrent_results?: TorrentCleanupResult[]
  errors?: string[]
}
