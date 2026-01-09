import {request} from "../utils/requests";

export async function getSubscribes() {
    const response = await request.request({
        url: '/subscribe/',
        method: 'get'
    })
    return response.data.data
}

export async function getSubscribeHistories() {
    const response = await request.request({
        url: '/subscribe/history',
        method: 'get'
    })
    return response.data.data
}

export function modifySubscribe(data: any) {
    return request.request({
        url: '/subscribe/',
        method: data.id ? 'put' : 'post',
        data: data
    })
}

export function resubscribe(id: any) {
    return request.request({
        url: '/subscribe/resubscribe',
        method: 'post',
        params: {subscribe_id: id},
    })
}

export function deleteSubscribe(id: number) {
    return request.request({
        url: '/subscribe/',
        method: 'delete',
        params: {subscribe_id: id},
    })
}

export async function searchVideo(param:any) {
    const response = await request.request({
        url: '/subscribe/search',
        method: 'get',
        params: param
    })
    return response.data.data
}

export async function downloadVideos(video: any, link: any) {
    const response = await request.request({
        url: '/subscribe/download',
        method: 'post',
        data: {
            video, link
        }
    })
    return response.data.data
}

// Actor Subscription APIs
export async function getActorSubscriptions() {
    const response = await request.request({
        url: '/actor-subscribe/',
        method: 'get'
    })
    return response.data.data
}

export async function addActorSubscription(data: any) {
    const response = await request.request({
        url: '/actor-subscribe/',
        method: 'post',
        data: data
    })
    return response.data
}

export async function updateActorSubscription(data: any) {
    const response = await request.request({
        url: '/actor-subscribe/',
        method: 'put',
        data: data
    })
    return response.data
}

export async function updateActorSubscriptionStatus(id: number, isPaused: boolean) {
    const response = await request.request({
        url: '/actor-subscribe/status',
        method: 'put',
        data: {
            subscription_id: id,
            is_paused: isPaused
        }
    })
    return response.data
}

export async function deleteActorSubscription(id: number, deleteDownloads: boolean = false) {
    const response = await request.request({
        url: '/actor-subscribe/',
        method: 'delete',
        data: {
            subscription_id: id,
            delete_downloads: deleteDownloads
        }
    })
    return response.data
}

export async function getActorSubscriptionDownloads(actorId: number) {
    const response = await request.request({
        url: '/actor-subscribe/downloads',
        method: 'get',
        params: { actor_id: actorId }
    })
    return response.data.data
}

export async function getAllSubscriptionDownloads() {
    const response = await request.request({
        url: '/actor-subscribe/all-downloads',
        method: 'get'
    })
    return response.data.data
}

export async function deleteSubscriptionDownload(downloadId: number, deleteFiles: boolean = false) {
    const response = await request.request({
        url: `/actor-subscribe/download/${downloadId}`,
        method: 'delete',
        params: { delete_files: deleteFiles }
    })
    return response.data
}

export async function runActorSubscribe() {
    const response = await request.request({
        url: '/actor-subscribe/run',
        method: 'post'
    })
    return response.data
}

// Subscribe to an actor (create or update subscription)
export async function subscribeActor(data: {
    actor_name: string;
    actor_url?: string;
    actor_thumb?: string;
    from_date: string;
    is_hd?: boolean;
    is_zh?: boolean;
    is_uncensored?: boolean;
    min_rating?: number;
    min_comments?: number;
}) {
    const response = await request.request({
        url: '/actor-subscribe/',
        method: 'post',
        data: data
    })
    return response.data
}
