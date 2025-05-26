/*
 * @Author: Await
 * @Date: 2025-05-24 17:05:38
 * @LastEditors: Await
 * @LastEditTime: 2025-05-26 00:02:10
 * @Description: 请填写简介
 */
import { request } from "../utils/requests";

export async function getSubscribes() {
    const response = await request.request({
        url: '/subscribe/',
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

export function deleteSubscribe(id: number) {
    return request.request({
        url: '/subscribe/',
        method: 'delete',
        params: { subscribe_id: id },
    })
}

export async function searchVideo(param: any) {
    const response = await request.request({
        url: '/subscribe/search',
        method: 'get',
        params: param
    })
    return response.data.data
}

export async function downloadVideos(video: any, link: any) {
    // 处理video对象，确保actors字段是字符串
    const processedVideo = { ...video };

    // 如果actors是数组，则将其转换为字符串
    if (Array.isArray(processedVideo.actors)) {
        processedVideo.actors = processedVideo.actors.map((actor: any) =>
            typeof actor === 'string' ? actor : actor.name
        ).join(', ');
    }

    const response = await request.request({
        url: '/subscribe/download',
        method: 'post',
        data: {
            video: processedVideo,
            link
        }
    })
    return response.data.data
}

// 演员订阅相关API

export async function getActorSubscriptions() {
    const response = await request.request({
        url: '/actor-subscribe/',
        method: 'get'
    })
    return response.data.data
}

export function subscribeActor(data: any) {
    return request.request({
        url: '/actor-subscribe/',
        method: data.id ? 'put' : 'post',
        data: data
    })
}

export function updateActorSubscription(data: any) {
    return request.request({
        url: '/actor-subscribe/',
        method: 'put',
        data: data
    })
}

export function updateActorSubscriptionStatus(id: number, isPaused: boolean) {
    return request.request({
        url: '/actor-subscribe/status',
        method: 'put',
        data: { id, is_paused: isPaused }
    })
}

export function deleteActorSubscription(subscriptionId: number, deleteDownloads: boolean = false) {
    return request.request({
        url: '/actor-subscribe/',
        method: 'delete',
        data: {
            subscription_id: subscriptionId,
            delete_downloads: deleteDownloads
        }
    })
}

export async function getActorSubscriptionDownloads(actorId: number) {
    const response = await request.request({
        url: '/actor-subscribe/downloads',
        method: 'get',
        params: { actor_id: actorId }
    })
    return response.data.data
}

export function runActorSubscribe() {
    return request.request({
        url: '/actor-subscribe/run',
        method: 'post'
    })
}
