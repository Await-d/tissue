/**
 * @Author: Await
 * @Date: 2025-01-10
 * @Description: 批量选择状态管理 Hook
 */
import { useState, useCallback, useMemo } from 'react';

export interface BatchSelectVideo {
    num: string;
    title?: string;
    cover?: string;
    url?: string;
    is_zh?: boolean;
    is_uncensored?: boolean;
    rank?: number;
    publish_date?: string;
    source?: string;
}

export interface UseBatchSelectReturn {
    /** 是否处于批量选择模式 */
    isBatchMode: boolean;
    /** 已选中的视频 Map (num -> video) */
    selectedVideos: Map<string, BatchSelectVideo>;
    /** 选中的视频数量 */
    selectedCount: number;
    /** 切换批量选择模式 */
    toggleBatchMode: () => void;
    /** 进入批量选择模式 */
    enterBatchMode: () => void;
    /** 退出批量选择模式 */
    exitBatchMode: () => void;
    /** 切换视频选择状态 */
    toggleVideoSelection: (video: BatchSelectVideo) => void;
    /** 选择视频 */
    selectVideo: (video: BatchSelectVideo) => void;
    /** 取消选择视频 */
    unselectVideo: (num: string) => void;
    /** 全选 */
    selectAll: (videos: BatchSelectVideo[]) => void;
    /** 取消全选 */
    unselectAll: () => void;
    /** 检查视频是否已选中 */
    isSelected: (num: string) => boolean;
    /** 获取选中的视频列表 */
    getSelectedList: () => BatchSelectVideo[];
    /** 清空选择并退出批量模式 */
    reset: () => void;
}

/**
 * 批量选择状态管理 Hook
 */
export function useBatchSelect(): UseBatchSelectReturn {
    const [isBatchMode, setIsBatchMode] = useState(false);
    const [selectedVideos, setSelectedVideos] = useState<Map<string, BatchSelectVideo>>(new Map());

    // 选中数量
    const selectedCount = useMemo(() => selectedVideos.size, [selectedVideos]);

    // 切换批量模式
    const toggleBatchMode = useCallback(() => {
        setIsBatchMode(prev => {
            if (prev) {
                // 退出批量模式时清空选择
                setSelectedVideos(new Map());
            }
            return !prev;
        });
    }, []);

    // 进入批量模式
    const enterBatchMode = useCallback(() => {
        setIsBatchMode(true);
    }, []);

    // 退出批量模式
    const exitBatchMode = useCallback(() => {
        setIsBatchMode(false);
        setSelectedVideos(new Map());
    }, []);

    // 切换视频选择状态
    const toggleVideoSelection = useCallback((video: BatchSelectVideo) => {
        setSelectedVideos(prev => {
            const newMap = new Map(prev);
            if (newMap.has(video.num)) {
                newMap.delete(video.num);
            } else {
                newMap.set(video.num, video);
            }
            return newMap;
        });
    }, []);

    // 选择视频
    const selectVideo = useCallback((video: BatchSelectVideo) => {
        setSelectedVideos(prev => {
            const newMap = new Map(prev);
            newMap.set(video.num, video);
            return newMap;
        });
    }, []);

    // 取消选择视频
    const unselectVideo = useCallback((num: string) => {
        setSelectedVideos(prev => {
            const newMap = new Map(prev);
            newMap.delete(num);
            return newMap;
        });
    }, []);

    // 全选
    const selectAll = useCallback((videos: BatchSelectVideo[]) => {
        setSelectedVideos(prev => {
            const newMap = new Map(prev);
            videos.forEach(video => {
                if (video.num) {
                    newMap.set(video.num, video);
                }
            });
            return newMap;
        });
    }, []);

    // 取消全选
    const unselectAll = useCallback(() => {
        setSelectedVideos(new Map());
    }, []);

    // 检查是否选中
    const isSelected = useCallback((num: string) => {
        return selectedVideos.has(num);
    }, [selectedVideos]);

    // 获取选中列表
    const getSelectedList = useCallback(() => {
        return Array.from(selectedVideos.values());
    }, [selectedVideos]);

    // 重置
    const reset = useCallback(() => {
        setIsBatchMode(false);
        setSelectedVideos(new Map());
    }, []);

    return {
        isBatchMode,
        selectedVideos,
        selectedCount,
        toggleBatchMode,
        enterBatchMode,
        exitBatchMode,
        toggleVideoSelection,
        selectVideo,
        unselectVideo,
        selectAll,
        unselectAll,
        isSelected,
        getSelectedList,
        reset,
    };
}

export default useBatchSelect;
