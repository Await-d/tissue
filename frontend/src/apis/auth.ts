import {request} from "../utils/requests";

export async function login(data: any) {
    const response = await request.request({
        url: '/auth/login',
        method: 'post',
        headers: {'content-type': 'application/x-www-form-urlencoded'},
        data: `username=${data.username}&password=${data.password}`
    })
    return response.data
}

export async function getInfo() {
    const response = await request.request({
        url: '/user/',
        method: 'get'
    })
    return response.data
}

export async function getVersions() {
    const response = await request.request({
        url: '/common/version',
        method: 'get'
    })
    return response.data
}
