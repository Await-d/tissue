/**
 * @Author: Await
 * @Date: 2025-01-10
 * @Description: 批量下载弹窗组件
 */
import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Modal, List, Avatar, Progress, Tag, Space, Switch, Button, App, Empty, Spin } from 'antd';
import {
    CheckCircleFilled,
    CloseCircleFilled,
    LoadingOutlined,
    ClockCircleOutlined,
    PlayCircleOutlined,
    PauseCircleOutlined,
    CloudDownloadOutlined
} from '@ant-design/icons';
import type { BatchSelectVideo } from '@/hooks/useBatchSelect';
import * as videoApi from '@/apis/video';
import * as subscribeApi from '@/apis/subscribe';
import './BatchDownloadModal.css';

interface DownloadStatus {
    status: 'pending' | 'loading' | 'success' | 'error' | 'skipped';
    message?: string;
}

interface BatchDownloadModalProps {
    /** 是否显示 */
    open: boolean;
    /** 选中的视频列表 */
    videos: BatchSelectVideo[];
    /** 数据源类型 */
    sourceType?: string;
    /** 关闭回调 */
    onCancel: () => void;
    /** 下载完成回调 */
    onComplete?: (successCount: number, failCount: number) => void;
}

const BatchDownloadModal: React.FC<BatchDownloadModalProps> = ({
    open,
    videos,
    sourceType = 'javdb',
    onCancel,
    onComplete,
}) => {
    const { message } = App.useApp();
    const [downloading, setDownloading] = useState(false);
    const [paused, setPaused] = useState(false);
    const [currentIndex, setCurrentIndex] = useState(-1);
    const [downloadStatuses, setDownloadStatuses] = useState<Map<string, DownloadStatus>>(new Map());
    const [preferences, setPreferences] = useState({
        preferHD: true,
        preferZh: true,
        autoSelectBest: true,
    });

    const pausedRef = useRef(false);
    const abortRef = useRef(false);

    // 统计数据
    const successCount = Array.from(downloadStatuses.values()).filter(s => s.status === 'success').length;
    const errorCount = Array.from(downloadStatuses.values()).filter(s => s.status === 'error').length;
    const skippedCount = Array.from(downloadStatuses.values()).filter(s => s.status === 'skipped').length;
    const completedCount = successCount + errorCount + skippedCount;
    const progress = videos.length > 0 ? Math.round((completedCount / videos.length) * 100) : 0;

    // 重置状态
    useEffect(() => {
        if (open) {
            setDownloadStatuses(new Map());
            setCurrentIndex(-1);
            setDownloading(false);
            setPaused(false);
            pausedRef.current = false;
            abortRef.current = false;
        }
    }, [open]);

    // 选择最佳下载项
    const selectBestDownload = (downloads: any[]) => {
        if (!downloads || downloads.length === 0) return null;

        let selected = downloads[0];
        let bestScore = 0;

        for (const download of downloads) {
            let score = 0;
            const name = (download.name || '').toLowerCase();

            // 优先高清
            if (preferences.preferHD) {
                if (name.includes('1080p') || name.includes('fhd')) score += 100;
                else if (name.includes('720p') || name.includes('hd')) score += 50;
                else if (name.includes('4k') || name.includes('2160p')) score += 150;
            }

            // 优先中文
            if (preferences.preferZh) {
                if (name.includes('中文') || name.includes('字幕') || name.includes('ch')) score += 80;
            }

            // 文件大小评分 (较大的文件通常质量更好，但也不要太大)
            if (download.size) {
                const sizeGB = parseFloat(download.size);
                if (sizeGB >= 2 && sizeGB <= 10) score += 30;
                else if (sizeGB > 10) score += 10;
            }

            if (score > bestScore) {
                bestScore = score;
                selected = download;
            }
        }

        return selected;
    };

    // 处理单个视频下载
    const processVideo = async (video: BatchSelectVideo): Promise<DownloadStatus> => {
        try {
            // 获取下载资源
            const detailData = await videoApi.getVideoDownloads(
                video.num,
                video.source || sourceType,
                video.url
            );

            if (!detailData || !detailData.downloads || detailData.downloads.length === 0) {
                return { status: 'skipped', message: '没有可用的下载资源' };
            }

            // 选择下载项
            const selectedDownload = preferences.autoSelectBest
                ? selectBestDownload(detailData.downloads)
                : detailData.downloads[0];

            if (!selectedDownload) {
                return { status: 'skipped', message: '没有符合偏好的下载资源' };
            }

            // 执行下载
            await subscribeApi.downloadVideos(detailData, selectedDownload);
            return { status: 'success', message: selectedDownload.name };
        } catch (error: any) {
            console.error(`下载失败 [${video.num}]:`, error);
            return {
                status: 'error',
                message: error?.response?.data?.detail || error?.message || '下载失败'
            };
        }
    };

    // 开始批量下载
    const startDownload = async () => {
        if (videos.length === 0) {
            message.warning('没有选中任何视频');
            return;
        }

        setDownloading(true);
        setPaused(false);
        pausedRef.current = false;
        abortRef.current = false;

        for (let i = 0; i < videos.length; i++) {
            // 检查是否中止
            if (abortRef.current) {
                break;
            }

            // 检查是否暂停
            while (pausedRef.current && !abortRef.current) {
                await new Promise(resolve => setTimeout(resolve, 500));
            }

            if (abortRef.current) break;

            const video = videos[i];
            setCurrentIndex(i);

            // 更新状态为加载中
            setDownloadStatuses(prev => {
                const newMap = new Map(prev);
                newMap.set(video.num, { status: 'loading' });
                return newMap;
            });

            // 处理下载
            const result = await processVideo(video);

            // 更新状态
            setDownloadStatuses(prev => {
                const newMap = new Map(prev);
                newMap.set(video.num, result);
                return newMap;
            });

            // 短暂延迟，避免请求过快
            if (i < videos.length - 1) {
                await new Promise(resolve => setTimeout(resolve, 800));
            }
        }

        setDownloading(false);
        setCurrentIndex(-1);

        // 计算最终结果
        const finalStatuses = downloadStatuses;
        const finalSuccess = Array.from(finalStatuses.values()).filter(s => s.status === 'success').length;
        const finalError = Array.from(finalStatuses.values()).filter(s => s.status === 'error').length;

        if (!abortRef.current) {
            message.success(`批量下载完成：成功 ${finalSuccess}，失败 ${finalError}`);
            onComplete?.(finalSuccess, finalError);
        }
    };

    // 暂停/继续
    const togglePause = () => {
        pausedRef.current = !pausedRef.current;
        setPaused(pausedRef.current);
    };

    // 中止下载
    const abortDownload = () => {
        abortRef.current = true;
        pausedRef.current = false;
        setPaused(false);
    };

    // 渲染状态图标
    const renderStatusIcon = (status: DownloadStatus['status']) => {
        switch (status) {
            case 'success':
                return <CheckCircleFilled style={{ color: '#52c41a', fontSize: 18 }} />;
            case 'error':
                return <CloseCircleFilled style={{ color: '#ff4d4f', fontSize: 18 }} />;
            case 'loading':
                return <LoadingOutlined style={{ color: '#d4a852', fontSize: 18 }} spin />;
            case 'skipped':
                return <ClockCircleOutlined style={{ color: '#faad14', fontSize: 18 }} />;
            default:
                return <ClockCircleOutlined style={{ color: '#6a6a72', fontSize: 18 }} />;
        }
    };

    return (
        <Modal
            title={
                <span style={{ color: '#f0f0f2', fontSize: 18, fontWeight: 600 }}>
                    <CloudDownloadOutlined style={{ marginRight: 8, color: '#d4a852' }} />
                    批量下载
                </span>
            }
            open={open}
            onCancel={() => {
                if (downloading) {
                    Modal.confirm({
                        title: '确认取消',
                        content: '下载正在进行中，确定要取消吗？',
                        okText: '确定',
                        cancelText: '继续下载',
                        onOk: () => {
                            abortDownload();
                            onCancel();
                        }
                    });
                } else {
                    onCancel();
                }
            }}
            footer={null}
            width={680}
            className="batch-download-modal"
            centered
        >
            {/* 下载偏好设置 */}
            {!downloading && completedCount === 0 && (
                <div className="download-preferences">
                    <h4 style={{ color: '#a0a0a8', marginBottom: 12 }}>下载偏好</h4>
                    <Space size="large">
                        <div className="preference-item">
                            <Switch
                                checked={preferences.preferHD}
                                onChange={(checked) => setPreferences(p => ({ ...p, preferHD: checked }))}
                                size="small"
                            />
                            <span>优先高清</span>
                        </div>
                        <div className="preference-item">
                            <Switch
                                checked={preferences.preferZh}
                                onChange={(checked) => setPreferences(p => ({ ...p, preferZh: checked }))}
                                size="small"
                            />
                            <span>优先中文</span>
                        </div>
                        <div className="preference-item">
                            <Switch
                                checked={preferences.autoSelectBest}
                                onChange={(checked) => setPreferences(p => ({ ...p, autoSelectBest: checked }))}
                                size="small"
                            />
                            <span>自动选择最佳</span>
                        </div>
                    </Space>
                </div>
            )}

            {/* 进度条 */}
            {(downloading || completedCount > 0) && (
                <div className="download-progress">
                    <Progress
                        percent={progress}
                        status={downloading ? 'active' : (errorCount > 0 ? 'exception' : 'success')}
                        strokeColor={{
                            '0%': '#d4a852',
                            '100%': '#e8c780',
                        }}
                        trailColor="rgba(255, 255, 255, 0.08)"
                    />
                    <div className="progress-stats">
                        <span>
                            <CheckCircleFilled style={{ color: '#52c41a', marginRight: 4 }} />
                            成功: {successCount}
                        </span>
                        <span>
                            <CloseCircleFilled style={{ color: '#ff4d4f', marginRight: 4 }} />
                            失败: {errorCount}
                        </span>
                        <span>
                            <ClockCircleOutlined style={{ color: '#faad14', marginRight: 4 }} />
                            跳过: {skippedCount}
                        </span>
                    </div>
                </div>
            )}

            {/* 视频列表 */}
            <div className="video-list-container">
                {videos.length === 0 ? (
                    <Empty description="没有选中的视频" />
                ) : (
                    <List
                        dataSource={videos}
                        className="batch-video-list"
                        renderItem={(video, index) => {
                            const status = downloadStatuses.get(video.num);
                            const isCurrentItem = currentIndex === index && downloading;

                            return (
                                <List.Item
                                    className={`batch-video-item ${isCurrentItem ? 'current' : ''} ${status?.status || ''}`}
                                >
                                    <div className="video-item-content">
                                        <Avatar
                                            shape="square"
                                            size={48}
                                            src={video.cover ? videoApi.getVideoCover(video.cover) : undefined}
                                            style={{ background: '#222226' }}
                                        >
                                            {video.num?.substring(0, 2)}
                                        </Avatar>
                                        <div className="video-info">
                                            <div className="video-num">{video.num}</div>
                                            <div className="video-title">{video.title || video.num}</div>
                                            {status?.message && (
                                                <div className={`video-status-message ${status.status}`}>
                                                    {status.message}
                                                </div>
                                            )}
                                        </div>
                                        <div className="video-status">
                                            {renderStatusIcon(status?.status || 'pending')}
                                        </div>
                                    </div>
                                </List.Item>
                            );
                        }}
                    />
                )}
            </div>

            {/* 操作按钮 */}
            <div className="modal-actions">
                {!downloading && completedCount === 0 && (
                    <Button
                        type="primary"
                        size="large"
                        icon={<CloudDownloadOutlined />}
                        onClick={startDownload}
                        disabled={videos.length === 0}
                        className="start-download-btn"
                    >
                        开始下载 ({videos.length} 个视频)
                    </Button>
                )}

                {downloading && (
                    <Space>
                        <Button
                            size="large"
                            icon={paused ? <PlayCircleOutlined /> : <PauseCircleOutlined />}
                            onClick={togglePause}
                            className="pause-btn"
                        >
                            {paused ? '继续' : '暂停'}
                        </Button>
                        <Button
                            size="large"
                            danger
                            onClick={abortDownload}
                        >
                            取消下载
                        </Button>
                    </Space>
                )}

                {!downloading && completedCount > 0 && (
                    <Button
                        type="primary"
                        size="large"
                        onClick={onCancel}
                        className="complete-btn"
                    >
                        完成
                    </Button>
                )}
            </div>
        </Modal>
    );
};

export default BatchDownloadModal;
