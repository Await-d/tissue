import {request} from "../utils/requests";

export async function getDownloads() {
    const response = await request.request({
        url: '/download/',
        method: 'get'
    })
    return response.data.data
}

export function completeDownload(hash: string) {
    return request.request({
        url: '/download/complete',
        method: 'get',
        params: {torrent_hash: hash}
    })
}

/**
 * 测试qBittorrent连接状态
 */
export function testConnection() {
    return request.request({
        url: '/download/test-connection',
        method: 'get'
    })
}

/**
 * 获取种子的文件列表
 */
export async function getTorrentFiles(torrentHash: string) {
    const response = await request.request({
        url: `/download/torrent/${torrentHash}/files`,
        method: 'get'
    })
    return response.data.data
}

/**
 * 设置文件下载优先级
 */
export function setFilesPriority(torrentHash: string, fileIndices: number[], priority: number) {
    return request.request({
        url: '/download/torrent/files/priority',
        method: 'post',
        data: {
            torrent_hash: torrentHash,
            file_indices: fileIndices,
            priority: priority
        }
    })
}

/**
 * 对种子应用全局过滤规则
 */
export function applyFilterToTorrent(torrentHash: string) {
    return request.request({
        url: '/download/torrent/apply-filter',
        method: 'post',
        data: {
            torrent_hash: torrentHash
        }
    })
}

/**
 * 暂停种子下载
 */
export function pauseTorrent(torrentHash: string) {
    return request.request({
        url: `/download/torrent/${torrentHash}/pause`,
        method: 'post'
    })
}

/**
 * 恢复种子下载
 */
export function resumeTorrent(torrentHash: string) {
    return request.request({
        url: `/download/torrent/${torrentHash}/resume`,
        method: 'post'
    })
}

/**
 * 删除种子
 */
export function deleteTorrent(torrentHash: string, deleteFiles: boolean = false) {
    return request.request({
        url: `/download/torrent/${torrentHash}`,
        method: 'delete',
        params: {delete_files: deleteFiles}
    })
}
