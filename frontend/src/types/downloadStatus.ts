/**
 * 下载状态相关类型定义
 */

/**
 * 下载状态类型
 * - 'downloaded': 已下载
 * - 'downloading': 下载中
 * - 'none': 未下载
 */
export type DownloadStatus = 'downloaded' | 'downloading' | 'none';

/**
 * 下载状态映射类型
 * 键为视频番号，值为下载状态
 */
export type DownloadStatusMap = Record<string, DownloadStatus>;
