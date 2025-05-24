/*
 * @Author: Await
 * @Date: 2025-05-24 17:05:38
 * @LastEditors: Await
 * @LastEditTime: 2025-05-25 04:53:46
 * @Description: 请填写简介
 */
import { request } from "../utils/requests";
import configs from "../configs";

export async function getVideos(force: boolean = false) {
    const response = await request.request({
        url: '/video/',
        method: 'get',
        params: { force }
    })
    return response.data.data
}

export async function getVideoDetail(path: string) {
    const response = await request.request({
        url: '/video/detail',
        method: 'get',
        params: { path }
    })
    return response.data.data
}

export async function parseVideoNum(path: string) {
    const response = await request.request({
        url: '/video/parse',
        method: 'get',
        params: { path }
    })
    return response.data.data
}

export function getVideoCover(url: string) {
    return configs.BASE_API + '/common/cover?url=' + encodeURIComponent(url)
}

export function getVideoTrailer(url: string) {
    return configs.BASE_API + '/common/trailer?url=' + encodeURIComponent(url)
}

export function scrapeVideo(num: string) {
    return request.request({
        url: '/video/scrape',
        method: 'get',
        params: { num }
    })
}

export function saveVideo(data: any, mode?: string, transMode?: string) {
    return request.request({
        url: '/video/',
        method: 'post',
        params: { mode, trans_mode: transMode },
        data: data
    })
}

export function deleteVideo(path?: string) {
    return request.request({
        url: '/video/',
        method: 'delete',
        params: { path },
    })
}

export async function getAllActors(force: boolean = false) {
    const response = await request.request({
        url: '/video/actors',
        method: 'get',
        params: { force }
    })
    return response.data.data
}

export async function searchVideosByActor(actorName: string, force: boolean = false) {
    const response = await request.request({
        url: '/video/search/actor',
        method: 'get',
        params: { actor_name: actorName, force }
    })
    return response.data.data
}

export async function getWebActors(source: string = 'javdb') {
    const response = await request.request({
        url: '/video/web/actors',
        method: 'get',
        params: { source }
    })
    return response.data.data
}

export async function searchWebActor(actorName: string, source: string = 'javdb') {
    const response = await request.request({
        url: '/video/web/search/actor',
        method: 'get',
        params: { actor_name: actorName, source }
    })
    return response.data.data
}

export async function getWebActorVideos(actorName: string, source: string = 'javdb') {
    const response = await request.request({
        url: '/video/web/actor/videos',
        method: 'get',
        params: { actor_name: actorName, source }
    })
    return response.data.data
}

export async function getVideoDownloads(num: string, source: string = 'javdb', url?: string) {
    const response = await request.request({
        url: '/home/ranking/detail',
        method: 'get',
        params: {
            num: num,
            source: source,
            url: url
        }
    })
    return response.data
}
