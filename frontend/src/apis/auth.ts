import {request} from "../utils/requests";

type LoginPayload = {
    readonly username: string
    readonly password: string
    readonly remember: boolean
}

export async function login(data: LoginPayload) {
    const response = await request.request({
        url: '/auth/login',
        method: 'post',
        headers: {'content-type': 'application/x-www-form-urlencoded'},
        data: `username=${encodeURIComponent(data.username)}&password=${encodeURIComponent(data.password)}&remember=${String(data.remember)}`
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
