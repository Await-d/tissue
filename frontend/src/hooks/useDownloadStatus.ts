/**
 * @Author: Await
 * @Date: 2026-01-11
 * @Description: 下载状态检测 Hook
 */
import { useState, useEffect, useMemo } from 'react';
import { checkDownloadStatusBatch, type DownloadStatus } from '../apis/downloadStatus';

/**
 * 视频对象接口（最小化必需字段）
 */
export interface VideoWithNum {
    num?: string;
    [key: string]: any;
}

/**
 * Hook 返回值接口
 */
export interface UseDownloadStatusReturn {
    /** 番号到下载状态的映射 { "ABC-123": "downloaded", "DEF-456": "none" } */
    statusMap: Record<string, DownloadStatus>;
    /** 是否正在加载 */
    loading: boolean;
    /** 错误信息（如果有） */
    error: Error | null;
    /** 重新加载下载状态 */
    reload: () => void;
}

/**
 * 下载状态检测 Hook
 *
 * @param videos - 包含 num 字段的视频列表
 * @returns 下载状态映射、加载状态和重新加载方法
 *
 * @example
 * ```tsx
 * const { statusMap, loading } = useDownloadStatus(videos);
 * const downloadStatus = statusMap[video.num] || 'none';
 * ```
 */
export function useDownloadStatus(videos: VideoWithNum[]): UseDownloadStatusReturn {
    const [statusMap, setStatusMap] = useState<Record<string, DownloadStatus>>({});
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<Error | null>(null);
    const [reloadTrigger, setReloadTrigger] = useState<number>(0);

    // 从 videos 中提取有效的 num 列表
    // 使用序列化后的 nums 作为依赖，避免 videos 数组引用变化导致的不必要重新计算
    const numsString = useMemo(() => {
        const extractedNums = videos
            .map(video => video.num)
            .filter((num): num is string => typeof num === 'string' && num.trim() !== '');
        return JSON.stringify(extractedNums.sort());
    }, [videos]);

    const nums = useMemo(() => {
        return JSON.parse(numsString) as string[];
    }, [numsString]);

    // 重新加载方法
    const reload = () => {
        setReloadTrigger(prev => prev + 1);
    };

    useEffect(() => {
        // 如果没有有效的番号，清空状态并返回
        if (nums.length === 0) {
            setStatusMap({});
            setLoading(false);
            setError(null);
            return;
        }

        let isMounted = true;

        const fetchDownloadStatus = async () => {
            setLoading(true);
            setError(null);

            try {
                const result = await checkDownloadStatusBatch(nums);

                if (isMounted) {
                    setStatusMap(result);
                }
            } catch (err) {
                if (isMounted) {
                    const error = err instanceof Error ? err : new Error('Failed to check download status');
                    setError(error);
                    console.error('Error fetching download status:', error);
                }
            } finally {
                if (isMounted) {
                    setLoading(false);
                }
            }
        };

        fetchDownloadStatus();

        // 清理函数，防止组件卸载后更新状态
        return () => {
            isMounted = false;
        };
    }, [nums, reloadTrigger]);

    return {
        statusMap,
        loading,
        error,
        reload
    };
}

export default useDownloadStatus;
