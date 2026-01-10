/*
 * @Author: Await
 * @Date: 2026-01-11
 * @Description: 文件扫描 API
 */
import { request } from "../utils/requests";

// 扫描结果类型定义
export interface ScanResult {
    scan_id?: number;           // 扫描ID
    scan_time: string;          // 扫描时间
    total_files: number;        // 扫描文件总数
    new_found: number;          // 新发现视频数
    already_exists: number;     // 已存在视频数
    scan_duration: number;      // 扫描耗时（秒）
    status: 'success' | 'failed' | 'running';
    error_message?: string;     // 错误信息
}

// 扫描记录类型定义
export interface ScanRecord {
    id: number;
    scan_time: string;
    total_files: number;
    new_found: number;
    already_exists: number;
    scan_duration: number;
    status: string;
    error_message?: string;
}

// 分页响应类型
export interface PaginatedScanRecords {
    items: ScanRecord[];
    total: number;
    page: number;
    page_size: number;
}

/**
 * 触发文件扫描
 * @returns 扫描结果
 */
export async function triggerScan(): Promise<ScanResult> {
    const response = await request.request({
        url: '/file-scan/trigger',
        method: 'post'
    });
    return response.data.data;
}

/**
 * 获取扫描记录（分页）
 * @param page 页码（从1开始）
 * @param pageSize 每页数量
 * @returns 分页的扫描记录
 */
export async function getScanRecords(
    page: number = 1,
    pageSize: number = 10
): Promise<PaginatedScanRecords> {
    const response = await request.request({
        url: '/file-scan/records',
        method: 'get',
        params: { page, page_size: pageSize }
    });
    return response.data.data;
}

/**
 * 获取最新一次扫描结果
 * @returns 最新扫描结果
 */
export async function getLatestScan(): Promise<ScanResult | null> {
    const response = await request.request({
        url: '/file-scan/latest',
        method: 'get'
    });
    return response.data.data;
}

/**
 * 获取当前扫描状态
 * @returns 扫描状态信息
 */
export async function getScanStatus(): Promise<{
    is_scanning: boolean;
    current_scan_id: number | null;
}> {
    const response = await request.request({
        url: '/file-scan/status',
        method: 'get'
    });
    return response.data.data;
}
