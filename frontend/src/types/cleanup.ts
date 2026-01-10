/**
 * 清理文件相关类型定义
 */

/**
 * 清理文件信息
 */
export interface CleanupFile {
  name: string
  path: string
  size: string
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
 * 清理结果数据
 */
export interface CleanupResultData {
  success: boolean
  torrents_processed?: number
  files_deleted?: number
  space_freed_mb?: number
  details?: Array<{
    torrent_name?: string
    files_removed?: string[]
  }>
}
