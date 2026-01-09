import {request} from "../utils/requests";
import configs from "../configs";

export async function getVideos(force: boolean = false) {
    const response = await request.request({
        url: '/video/',
        method: 'get',
        params: {force}
    })
    return response.data.data
}

export async function getVideoDetail(path: string) {
    const response = await request.request({
        url: '/video/detail',
        method: 'get',
        params: {path}
    })
    return response.data.data
}

export async function parseVideoNum(path: string) {
    const response = await request.request({
        url: '/video/parse',
        method: 'get',
        params: {path}
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
        params: {num}
    })
}

export function saveVideo(data: any, mode?: string, transMode?: string) {
    return request.request({
        url: '/video/',
        method: 'post',
        params: {mode, trans_mode: transMode},
        data: data
    })
}

export function deleteVideo(path?: string) {
    return request.request({
        url: '/video/',
        method: 'delete',
        params: {path},
    })
}

// Get all local actors
export async function getAllActors(force: boolean = false) {
    const response = await request.request({
        url: '/video/actors',
        method: 'get',
        params: { force }
    })
    return response.data.data
}

// Search videos by actor name
export async function searchVideosByActor(actorName: string, force: boolean = false) {
    const response = await request.request({
        url: '/video/search/actor',
        method: 'get',
        params: { actor_name: actorName, force }
    })
    return response.data.data
}

// Get popular actors from web source (JavDB/JavBus)
export async function getWebActors(sourceType: string) {
    const response = await request.request({
        url: '/video/web/actors',
        method: 'get',
        params: { source: sourceType }
    })
    return response.data.data
}

// Search actors on web source
export async function searchWebActor(actorName: string, sourceType: string) {
    const response = await request.request({
        url: '/video/web/actor/search',
        method: 'get',
        params: { actor_name: actorName, source: sourceType }
    })
    return response.data.data
}

// Get actor's videos from web source
export async function getWebActorVideos(actorName: string, sourceType: string) {
    const response = await request.request({
        url: '/video/web/actor/videos',
        method: 'get',
        params: { actor_name: actorName, source: sourceType }
    })
    return response.data.data
}

// Get video download resources
export async function getVideoDownloads(num: string, sourceType: string, url: string) {
    const response = await request.request({
        url: '/video/web/downloads',
        method: 'get',
        params: { num, source: sourceType, url }
    })
    return response.data.data
}

// Get web video detail
export async function getWebVideoDetail(num: string, source: string, url: string) {
    const response = await request.request({
        url: '/video/web/detail',
        method: 'get',
        params: { num, source, url }
    })
    return response.data.data
}
