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
import { useThemeColors } from "../../../../hooks/useThemeColors";

function JavDBItem(props: { item: any; isDownloaded?: boolean }) {
    const { item, isDownloaded = false } = props;
    const { message } = App.useApp();
    const colors = useThemeColors();

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
                className="tissue-home-card"
                style={{
                    background: colors.bgContainer,
                    borderRadius: 16,
                    overflow: 'hidden',
                    border: `1px solid ${colors.borderSecondary}`,
                    cursor: 'pointer',
                    transition: 'all 400ms cubic-bezier(0.34, 1.56, 0.64, 1)',
                    position: 'relative',
                    boxShadow: `0 4px 12px ${colors.rgba('black', 0.15)}`,
                }}
                onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-8px)';
                    e.currentTarget.style.boxShadow = `
                        0 24px 48px ${colors.rgba('black', 0.3)},
                        0 0 0 1px ${colors.borderGold},
                        0 0 32px ${colors.rgba('gold', 0.2)}
                    `;
                    e.currentTarget.style.borderColor = colors.borderGold;
                }}
                onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = `0 4px 12px ${colors.rgba('black', 0.15)}`;
                    e.currentTarget.style.borderColor = colors.borderSecondary;
                }}
            >
                {/* 金色光晕装饰 */}
                <div style={{
                    position: 'absolute',
                    top: -2,
                    left: -2,
                    right: -2,
                    height: '50%',
                    background: `linear-gradient(135deg, ${colors.rgba('gold', 0.08)} 0%, transparent 50%)`,
                    opacity: 0,
                    transition: 'opacity 400ms ease',
                    pointerEvents: 'none',
                    zIndex: 1,
                }} className="tissue-card-glow" />

                {/* 封面区域 */}
                <div style={{ position: 'relative', overflow: 'hidden' }}>
                    <div style={{
                        aspectRatio: '16/10',
                        overflow: 'hidden',
                        position: 'relative',
                    }}>
                        <VideoCover src={item.cover} />
                        
                        {/* 顶部淡入遮罩 */}
                        <div style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            right: 0,
                            height: '40%',
                            background: 'linear-gradient(to bottom, rgba(0,0,0,0.5) 0%, transparent 100%)',
                            pointerEvents: 'none',
                        }} />
                    </div>

                    {/* 底部渐变遮罩 - 更自然的过渡 */}
                    <div style={{
                        position: 'absolute',
                        bottom: 0,
                        left: 0,
                        right: 0,
                        height: '60%',
                        background: 'linear-gradient(to bottom, transparent 0%, rgba(0,0,0,0.85) 100%)',
                        pointerEvents: 'none',
                    }} />

                    {/* 悬浮时显示的播放图标 */}
                    <div
                        className="tissue-play-icon"
                        style={{
                            position: 'absolute',
                            top: '50%',
                            left: '50%',
                            transform: 'translate(-50%, -50%) scale(0.8)',
                            opacity: 0,
                            transition: 'all 400ms cubic-bezier(0.34, 1.56, 0.64, 1)',
                            pointerEvents: 'none',
                        }}
                    >
                        <div style={{
                            width: 72,
                            height: 72,
                            borderRadius: '50%',
                            background: colors.rgba('bgContainer', 0.95),
                            backdropFilter: 'blur(20px)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            border: `2px solid ${colors.goldPrimary}`,
                            boxShadow: `0 8px 24px ${colors.rgba('black', 0.4)}, 0 0 32px ${colors.rgba('gold', 0.3)}`,
                        }}>
                            <PlayCircleOutlined style={{
                                fontSize: 36,
                                color: colors.goldPrimary,
                            }} />
                        </div>
                    </div>

                    {/* 操作按钮组 */}
                    <div style={{
                        position: 'absolute',
                        bottom: 14,
                        right: 14,
                        zIndex: 10,
                        display: 'flex',
                        gap: 10,
                    }}>
                        <Tooltip title="预览图片" placement="top">
                            <Button
                                type="default"
                                shape="circle"
                                icon={<EyeOutlined />}
                                size="large"
                                loading={loadingPreview}
                                onClick={handlePreviewClick}
                                style={{
                                    background: colors.rgba('bgContainer', 0.95),
                                    backdropFilter: 'blur(20px)',
                                    border: `1px solid ${colors.borderPrimary}`,
                                    boxShadow: `0 4px 12px ${colors.rgba('black', 0.3)}`,
                                    color: colors.textPrimary,
                                    width: 40,
                                    height: 40,
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    transition: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
                                }}
                                onMouseEnter={(e) => {
                                    e.currentTarget.style.background = colors.rgba('bgContainer', 1);
                                    e.currentTarget.style.borderColor = colors.borderGold;
                                    e.currentTarget.style.color = colors.goldPrimary;
                                    e.currentTarget.style.transform = 'scale(1.1)';
                                }}
                                onMouseLeave={(e) => {
                                    e.currentTarget.style.background = colors.rgba('bgContainer', 0.95);
                                    e.currentTarget.style.borderColor = colors.borderPrimary;
                                    e.currentTarget.style.color = colors.textPrimary;
                                    e.currentTarget.style.transform = 'scale(1)';
                                }}
                            />
                        </Tooltip>
                        <Tooltip title="推送到下载器" placement="top">
                            <Button
                                type="primary"
                                shape="circle"
                                icon={<CloudDownloadOutlined />}
                                size="large"
                                loading={!!loadingVideoId}
                                onClick={handleVideoDownload}
                                style={{
                                    background: `linear-gradient(135deg, ${colors.goldPrimary} 0%, ${colors.goldDark} 100%)`,
                                    border: 'none',
                                    boxShadow: `0 4px 16px ${colors.rgba('gold', 0.4)}`,
                                    color: colors.bgBase,
                                    width: 40,
                                    height: 40,
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    transition: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
                                }}
                                onMouseEnter={(e) => {
                                    e.currentTarget.style.boxShadow = `0 6px 24px ${colors.rgba('gold', 0.5)}`;
                                    e.currentTarget.style.transform = 'scale(1.1)';
                                }}
                                onMouseLeave={(e) => {
                                    e.currentTarget.style.boxShadow = `0 4px 16px ${colors.rgba('gold', 0.4)}`;
                                    e.currentTarget.style.transform = 'scale(1)';
                                }}
                            />
                        </Tooltip>
                    </div>

                    {/* 评分角标 - 更精致的设计 */}
                    {item.rank > 0 && (
                        <div style={{
                            position: 'absolute',
                            top: 14,
                            left: 14,
                            background: `linear-gradient(135deg, ${colors.goldPrimary} 0%, ${colors.goldDark} 100%)`,
                            padding: '6px 12px',
                            borderRadius: 10,
                            display: 'flex',
                            alignItems: 'center',
                            gap: 4,
                            boxShadow: `0 4px 12px ${colors.rgba('gold', 0.3)}`,
                            border: `1px solid ${colors.rgba('gold', 0.3)}`,
                        }}>
                            <span style={{
                                fontSize: 15,
                                fontWeight: 700,
                                color: colors.bgBase,
                                letterSpacing: '0.02em',
                            }}>
                                ★ {item.rank?.toFixed(1)}
                            </span>
                        </div>
                    )}

                    {/* 已下载徽章 */}
                    {isDownloaded && (
                        <div style={{
                            position: 'absolute',
                            top: 14,
                            right: 14,
                            background: 'rgba(82, 196, 26, 0.95)',
                            backdropFilter: 'blur(10px)',
                            padding: '6px 12px',
                            borderRadius: 10,
                            display: 'flex',
                            alignItems: 'center',
                            gap: 6,
                            boxShadow: '0 4px 12px rgba(82, 196, 26, 0.4)',
                            border: '1px solid rgba(82, 196, 26, 0.5)',
                            zIndex: 10,
                        }}>
                            <span style={{
                                fontSize: 14,
                                fontWeight: 600,
                                color: '#fff',
                                letterSpacing: '0.02em',
                                lineHeight: 1,
                            }}>
                                ✓ 已下载
                            </span>
                        </div>
                    )}
                </div>

                {/* 内容区域 */}
                <div style={{ 
                    padding: '16px 18px',
                    background: `linear-gradient(to bottom, ${colors.bgContainer} 0%, ${colors.bgElevated} 100%)`,
                }}>
                    {/* 番号标签 */}
                    <div style={{
                        display: 'inline-block',
                        fontSize: 11,
                        fontWeight: 700,
                        color: colors.goldPrimary,
                        letterSpacing: '0.08em',
                        marginBottom: 8,
                        textTransform: 'uppercase',
                        padding: '3px 8px',
                        background: colors.rgba('gold', 0.12),
                        borderRadius: 6,
                        border: `1px solid ${colors.rgba('gold', 0.25)}`,
                    }}>
                        {item.num}
                    </div>

                    {/* 标题 */}
                    <Tooltip title={item.title || ''} placement="top">
                        <div style={{
                            fontSize: 14,
                            fontWeight: 500,
                            color: colors.textPrimary,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                            lineHeight: 1.5,
                            minHeight: '3em',
                            marginBottom: 12,
                            letterSpacing: '0.01em',
                        }}>
                            {item.title || ''}
                        </div>
                    </Tooltip>

                    {/* 评分与信息 */}
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        paddingTop: 12,
                        borderTop: `1px solid ${colors.borderSecondary}`,
                    }}>
                        <Space size={8} align="center">
                            <Rate
                                disabled
                                allowHalf
                                value={item.rank || 0}
                                style={{ fontSize: 13, color: colors.goldPrimary }}
                            />
                            <span style={{
                                fontSize: 12,
                                color: colors.textTertiary,
                                fontWeight: 500,
                            }}>
                                {item.rank_count || 0}
                            </span>
                        </Space>
                        <span style={{
                            fontSize: 11,
                            color: colors.textTertiary,
                            fontWeight: 500,
                            letterSpacing: '0.02em',
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
                    background: colors.goldGradient,
                    boxShadow: colors.shadowGold,
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
