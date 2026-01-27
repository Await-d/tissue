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
    return response.data
}

export function completeDownload(hash: string) {
    return request.request({
        url: '/download/complete',
        method: 'get',
        params: { torrent_hash: hash }
    })
}
