import { request } from "../utils/requests";

export async function getDownloads(params?: {
    include_success?: boolean;
    include_failed?: boolean;
}) {
    const response = await request.request({
        url: '/download/',
        method: 'get',
        params
    })
    return response.data.data
}

export function completeDownload(hash: string) {
    return request.request({
        url: '/download/complete',
        method: 'get',
        params: { torrent_hash: hash }
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
export async function setFilesPriority(data: {
    torrent_hash: string;
    file_indices: number[];
    priority: number;
}) {
    const response = await request.request({
        url: '/download/torrent/files/priority',
        method: 'post',
        data
    })
    return response.data
}

/**
 * 对种子应用全局过滤规则
 */
export async function applyFilterToTorrent(torrentHash: string) {
    const response = await request.request({
        url: '/download/torrent/apply-filter',
        method: 'post',
        data: { torrent_hash: torrentHash }
    })
    return response.data
}

/**
 * 暂停种子下载
 */
export async function pauseTorrent(torrentHash: string) {
    const response = await request.request({
        url: `/download/torrent/${torrentHash}/pause`,
        method: 'post'
    })
    return response.data
}

/**
 * 恢复种子下载
 */
export async function resumeTorrent(torrentHash: string) {
    const response = await request.request({
        url: `/download/torrent/${torrentHash}/resume`,
        method: 'post'
    })
    return response.data
}

/**
 * 删除种子
 */
export async function deleteTorrent(torrentHash: string, deleteFiles: boolean = false) {
    const response = await request.request({
        url: `/download/torrent/${torrentHash}`,
        method: 'delete',
        params: { delete_files: deleteFiles }
    })
    return response.data
}
