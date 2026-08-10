import {request} from "../utils/requests";

export interface RankingResult {
    items: any[]
    /** 后端返回的是兜底旧数据（源站抓取失败）时为 true */
    stale: boolean
    /** 数据来源：cache / refresh / live / stale-cache / empty */
    dataSource: string
}

export async function getRankings(params: any): Promise<RankingResult> {
    // rawResponse 让拦截器返回完整响应，以便读取 X-Data-Stale 响应头
    const response: any = await request.request({
        url: '/home/ranking',
        method: 'get',
        params: params,
        rawResponse: true,
    } as any)

    const items = Array.isArray(response?.data) ? response.data : []
    const headers = response?.headers ?? {}

    return {
        items,
        stale: String(headers['x-data-stale'] ?? '').toLowerCase() === 'true',
        dataSource: String(headers['x-data-source'] ?? ''),
    }
}


export async function getRankingDetail(params: any) {
    const response = await request.request({
        url: '/home/ranking/detail',
        method: 'get',
        params: params
    })
    return response
}
