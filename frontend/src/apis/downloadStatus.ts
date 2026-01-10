/**
 * @Author: Await
 * @Date: 2026-01-11
 * @Description: 下载状态检测相关 API
 */
import { request } from '../utils/requests';

/**
 * 批量检查视频下载状态
 * @param nums - 视频番号列表
 * @returns Promise 返回番号到下载状态的映射 { "ABC-123": true, "DEF-456": false }
 */
export async function checkDownloadStatusBatch(nums: string[]): Promise<Record<string, boolean>> {
    const response = await request.request({
        url: '/download-status/check-batch',
        method: 'post',
        data: { nums }
    });
    return response.data.data;
}
