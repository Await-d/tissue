/*
 * @Author: Await
 * @Date: 2025-05-24 17:05:38
 * @LastEditors: Await
 * @LastEditTime: 2025-05-27 16:19:27
 * @Description: TISSUE+ 视频卡片组件 - 电影美学风格
 */
import React, { useState } from "react";
import { Badge, Rate, Space, Button, Tooltip, App } from "antd";
import { CloudDownloadOutlined, EyeOutlined, PlayCircleOutlined } from "@ant-design/icons";
import VideoCover from "../../../../components/VideoCover";
import * as api from "../../../../apis/video";
import * as subscribeApi from "../../../../apis/subscribe";
import DownloadListModal from "../../../_index/search/-components/downloadListModal";
import { PreviewModal } from "../../../../components/VideoPreview";
import { useRequest } from "ahooks";

function JavDBItem(props: { item: any }) {
    const { item } = props;
    const { message } = App.useApp();

    const [loadingVideoId, setLoadingVideoId] = useState<string | null>(null);
    const [selectedVideo, setSelectedVideo] = useState<any>(null);
    const [downloadOptions, setDownloadOptions] = useState<any[]>([]);
    const [showDownloadList, setShowDownloadList] = useState(false);

    // 预览相关状态
    const [loadingPreview, setLoadingPreview] = useState(false);
    const [showPreviewModal, setShowPreviewModal] = useState(false);
    const [previewData, setPreviewData] = useState<any[]>([]);

    // 添加下载功能
    const { run: onDownload, loading: onDownloading } = useRequest(subscribeApi.downloadVideos, {
        manual: true,
        onSuccess: () => {
            setSelectedVideo(null);
            setShowDownloadList(false);
            setDownloadOptions([]);
            message.success("下载任务创建成功");
        },
        onError: (error) => {
            console.error('下载失败:', error);
            message.error('创建下载任务失败');
        }
    });

    // 处理视频下载
    const handleVideoDownload = (e: React.MouseEvent) => {
        e.stopPropagation();

        const videoId = `${item.num}-${Math.random().toString(36).substring(2, 7)}`;
        setLoadingVideoId(videoId);

        message.loading({ content: '正在获取下载资源...', key: 'download' });

        const source = 'JavDB';

        api.getVideoDownloads(item.num, source.toLowerCase(), item.url)
            .then(detailData => {
                setLoadingVideoId(null);

                if (detailData && detailData.downloads && detailData.downloads.length > 0) {
                    setSelectedVideo(detailData);
                    setDownloadOptions(detailData.downloads);
                    setShowDownloadList(true);
                    message.destroy('download');
                } else {
                    message.warning({ content: '没有找到可用的下载资源', key: 'download' });
                }
            })
            .catch(error => {
                setLoadingVideoId(null);
                console.error('获取下载资源失败:', error);
                message.error({ content: '获取下载资源失败', key: 'download' });
            });
    };

    const handleModalCancel = (e: React.MouseEvent) => {
        if (e && e.stopPropagation) {
            e.stopPropagation();
        }
        setShowDownloadList(false);
    };

    const handleDownload = (video: any, downloadItem: any) => {
        onDownload(video, downloadItem);
    };

    const handlePreviewClick = (e: React.MouseEvent) => {
        e.stopPropagation();

        setLoadingPreview(true);
        message.loading({ content: '正在获取预览...', key: 'preview' });

        const source = 'JavDB';

        api.getVideoDownloads(item.num, source.toLowerCase(), item.url)
            .then(detailData => {
                setLoadingPreview(false);

                if (detailData && detailData.previews && detailData.previews.length > 0) {
                    const firstPreview = detailData.previews[0];
                    if (firstPreview && firstPreview.items && firstPreview.items.length > 0) {
                        setPreviewData(firstPreview.items);
                        setShowPreviewModal(true);
                        message.destroy('preview');
                    } else {
                        message.warning({ content: '该视频暂无预览图片', key: 'preview' });
                    }
                } else {
                    message.warning({ content: '该视频暂无预览图片', key: 'preview' });
                }
            })
            .catch(error => {
                setLoadingPreview(false);
                console.error('获取预览失败:', error);
                message.error({ content: '获取预览失败', key: 'preview' });
            });
    };

    const handlePreviewModalCancel = (e?: React.MouseEvent) => {
        if (e && e.stopPropagation) {
            e.stopPropagation();
        }
        setShowPreviewModal(false);
    };

    function render() {
        return (
            <div
                className="tissue-card group"
                style={{
                    background: '#1a1a1d',
                    borderRadius: 14,
                    overflow: 'hidden',
                    border: '1px solid rgba(255, 255, 255, 0.06)',
                    cursor: 'pointer',
                    transition: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
                }}
                onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-6px) scale(1.01)';
                    e.currentTarget.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(212, 168, 82, 0.2)';
                    e.currentTarget.style.borderColor = 'rgba(212, 168, 82, 0.3)';
                }}
                onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0) scale(1)';
                    e.currentTarget.style.boxShadow = 'none';
                    e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.06)';
                }}
            >
                {/* 封面区域 */}
                <div style={{ position: 'relative', overflow: 'hidden' }}>
                    <div style={{
                        aspectRatio: '16/10',
                        overflow: 'hidden',
                    }}>
                        <VideoCover src={item.cover} />
                    </div>

                    {/* 渐变遮罩 */}
                    <div style={{
                        position: 'absolute',
                        inset: 0,
                        background: 'linear-gradient(to bottom, transparent 40%, rgba(0,0,0,0.9) 100%)',
                        pointerEvents: 'none',
                    }} />

                    {/* 悬浮时显示的播放图标 */}
                    <div
                        className="opacity-0 group-hover:opacity-100"
                        style={{
                            position: 'absolute',
                            top: '50%',
                            left: '50%',
                            transform: 'translate(-50%, -50%)',
                            transition: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
                        }}
                    >
                        <PlayCircleOutlined style={{
                            fontSize: 56,
                            color: 'rgba(255, 255, 255, 0.9)',
                            filter: 'drop-shadow(0 4px 12px rgba(0, 0, 0, 0.5))',
                        }} />
                    </div>

                    {/* 操作按钮 */}
                    <div style={{
                        position: 'absolute',
                        bottom: 12,
                        right: 12,
                        zIndex: 10,
                        display: 'flex',
                        gap: 8,
                    }}>
                        <Tooltip title="预览图片">
                            <Button
                                type="default"
                                shape="circle"
                                icon={<EyeOutlined style={{ color: '#f0f0f2' }} />}
                                size="middle"
                                loading={loadingPreview}
                                onClick={handlePreviewClick}
                                style={{
                                    background: 'rgba(26, 26, 29, 0.9)',
                                    backdropFilter: 'blur(10px)',
                                    border: '1px solid rgba(255, 255, 255, 0.1)',
                                    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.4)',
                                }}
                            />
                        </Tooltip>
                        <Tooltip title="推送到下载器">
                            <Button
                                type="primary"
                                shape="circle"
                                icon={<CloudDownloadOutlined />}
                                size="middle"
                                loading={!!loadingVideoId}
                                onClick={handleVideoDownload}
                                style={{
                                    background: 'linear-gradient(135deg, #d4a852 0%, #b08d3e 100%)',
                                    border: 'none',
                                    boxShadow: '0 4px 12px rgba(212, 168, 82, 0.4)',
                                }}
                            />
                        </Tooltip>
                    </div>

                    {/* 评分角标 */}
                    {item.rank > 0 && (
                        <div style={{
                            position: 'absolute',
                            top: 12,
                            left: 12,
                            background: 'linear-gradient(135deg, rgba(212, 168, 82, 0.95) 0%, rgba(176, 141, 62, 0.95) 100%)',
                            padding: '4px 10px',
                            borderRadius: 8,
                            display: 'flex',
                            alignItems: 'center',
                            gap: 4,
                            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
                        }}>
                            <span style={{ fontSize: 14, fontWeight: 700, color: '#0d0d0f' }}>
                                {item.rank?.toFixed(1)}
                            </span>
                        </div>
                    )}
                </div>

                {/* 内容区域 */}
                <div style={{ padding: '14px 16px' }}>
                    {/* 番号 */}
                    <div style={{
                        fontSize: 11,
                        fontWeight: 600,
                        color: '#d4a852',
                        letterSpacing: '0.05em',
                        marginBottom: 6,
                        textTransform: 'uppercase',
                    }}>
                        {item.num}
                    </div>

                    {/* 标题 */}
                    <Tooltip title={item.title || ''}>
                        <div style={{
                            fontSize: 14,
                            fontWeight: 500,
                            color: '#f0f0f2',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                            lineHeight: 1.4,
                            minHeight: '2.8em',
                            marginBottom: 10,
                        }}>
                            {item.title || ''}
                        </div>
                    </Tooltip>

                    {/* 评分与信息 */}
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        paddingTop: 10,
                        borderTop: '1px solid rgba(255, 255, 255, 0.06)',
                    }}>
                        <Space size={6} align="center">
                            <Rate
                                disabled
                                allowHalf
                                value={item.rank || 0}
                                style={{ fontSize: 12 }}
                            />
                            <span style={{
                                fontSize: 12,
                                color: '#6a6a72',
                            }}>
                                {item.rank_count || 0} 评论
                            </span>
                        </Space>
                        <span style={{
                            fontSize: 11,
                            color: '#4a4a52',
                        }}>
                            {item.publish_date || ''}
                        </span>
                    </div>
                </div>

                {/* 下载列表模态框 */}
                <DownloadListModal
                    open={showDownloadList}
                    video={selectedVideo}
                    downloads={downloadOptions}
                    onCancel={handleModalCancel}
                    onDownload={handleDownload}
                    confirmLoading={onDownloading}
                    modalRender={(modal) => (
                        <div onClick={(e) => e.stopPropagation()} onMouseDown={(e) => e.stopPropagation()} onMouseUp={(e) => e.stopPropagation()}>
                            {modal}
                        </div>
                    )}
                />

                {/* 预览模态框 */}
                <PreviewModal
                    open={showPreviewModal}
                    onCancel={handlePreviewModalCancel}
                    previews={previewData}
                    title={`${item.num} 预览`}
                />
            </div>
        )
    }

    return (
        item.isZh ? (
            <Badge.Ribbon
                text={'中文'}
                style={{
                    background: 'linear-gradient(135deg, #d4a852 0%, #b08d3e 100%)',
                    boxShadow: '0 2px 8px rgba(212, 168, 82, 0.3)',
                }}
            >
                {render()}
            </Badge.Ribbon>
        ) : (
            render()
        )
    )
}

export default JavDBItem
