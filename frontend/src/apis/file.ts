import {request} from "../utils/requests";

export async function getFiles() {
    const response = await request.request({
        url: '/file/',
    })
    return response.data.data
}

export async function batchParseFiles(paths: string[]) {
    const response = await request.request({
        url: '/file/batch/parse',
        method: 'post',
        data: paths
    })
    return response
}
