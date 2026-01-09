import { request } from "../utils/requests";

/**
 * Favorite API
 * Handles video favorite operations
 */

// Add favorite
export async function addFavorite(data: {
    video_num: string;
    video_title?: string;
    video_cover?: string
}) {
    const response = await request.request({
        url: '/favorite/',
        method: 'post',
        data: data
    });
    return response.data;
}

// Remove favorite
export async function removeFavorite(num: string) {
    const response = await request.request({
        url: `/favorite/${num}`,
        method: 'delete'
    });
    return response.data;
}

// Get favorites list
export async function getFavorites(params?: { page?: number; size?: number }) {
    const response = await request.request({
        url: '/favorite/',
        method: 'get',
        params: params
    });
    return response.data.data;
}

// Check if video is favorited
export async function checkFavorite(video_num: string) {
    const response = await request.request({
        url: '/favorite/check',
        method: 'get',
        params: { video_num }
    });
    return response.data.data;
}

// Batch add favorites
export async function batchAddFavorites(video_nums: string[]) {
    const response = await request.request({
        url: '/favorite/batch',
        method: 'post',
        data: { video_nums }
    });
    return response.data;
}

// Batch remove favorites
export async function batchRemoveFavorites(video_nums: string[]) {
    const response = await request.request({
        url: '/favorite/batch',
        method: 'delete',
        data: { video_nums }
    });
    return response.data;
}
