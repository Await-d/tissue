/*
 * @Author: Await
 * @Date: 2025-05-24 17:05:38
 * @LastEditors: Await
 * @LastEditTime: 2025-05-27 16:19:27
 * @Description: 请填写简介
 */
import React, { useState } from "react";
import { Badge, Rate, Space, theme, Button, Tooltip, App } from "antd";
import { CloudDownloadOutlined, EyeOutlined } from "@ant-design/icons";
import VideoCover from "../../../../components/VideoCover";
import * as api from "../../../../apis/video";
import * as subscribeApi from "../../../../apis/subscribe";
import DownloadListModal from "../../../_index/search/-components/downloadListModal";
import { PreviewModal } from "../../../../components/VideoPreview";
import { useRequest } from "ahooks";

const { useToken } = theme

function JavDBItem(props: { item: any }) {
    const { token } = useToken();
    const { item } = props;
    const { message } = App.useApp(); // 使用App上下文获取message API

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
        e.stopPropagation(); // 阻止事件冒泡，避免触发卡片点击事件

        // 设置当前视频为加载状态
        const videoId = `${item.num}-${Math.random().toString(36).substring(2, 7)}`;
        setLoadingVideoId(videoId);

        // 显示加载消息
        message.loading({ content: '正在获取下载资源...', key: 'download' });

        // 确定source类型，首字母大写
        const source = 'JavDB'; // 首页推荐目前只有JavDB来源

        // 获取视频的详细信息（包括下载资源）
        api.getVideoDownloads(item.num, source.toLowerCase(), item.url)
            .then(detailData => {
                // 清除加载状态
                setLoadingVideoId(null);

                if (detailData && detailData.downloads && detailData.downloads.length > 0) {
                    // 如果有多个下载选项，显示下载列表模态框
                    setSelectedVideo(detailData);
                    setDownloadOptions(detailData.downloads);
                    setShowDownloadList(true);
                    message.destroy('download');
                } else {
                    // 如果没有下载选项，只显示提示信息
                    message.warning({ content: '没有找到可用的下载资源', key: 'download' });
                }
            })
            .catch(error => {
                // 清除加载状态
                setLoadingVideoId(null);

                console.error('获取下载资源失败:', error);
                message.error({ content: '获取下载资源失败', key: 'download' });
            });
    };

    // 处理模态框取消，阻止事件冒泡
    const handleModalCancel = (e: React.MouseEvent) => {
        // 确保事件不会冒泡到父元素
        if (e && e.stopPropagation) {
            e.stopPropagation();
        }
        setShowDownloadList(false);
    };

    // 处理下载操作，同样阻止事件冒泡
    const handleDownload = (video: any, downloadItem: any) => {
        // 执行下载操作
        onDownload(video, downloadItem);
        // 这里不需要显式阻止冒泡，因为这是回调函数而非事件处理函数
    };

    // 处理预览按钮点击
    const handlePreviewClick = (e: React.MouseEvent) => {
        e.stopPropagation(); // 阻止事件冒泡
        
        setLoadingPreview(true);
        message.loading({ content: '正在获取预览...', key: 'preview' });
        
        const source = 'JavDB';
        
        api.getVideoDownloads(item.num, source.toLowerCase(), item.url)
            .then(detailData => {
                setLoadingPreview(false);
                
                if (detailData && detailData.previews && detailData.previews.length > 0) {
                    // 获取第一个网站的预览数据
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

    // 处理预览模态框关闭
    const handlePreviewModalCancel = (e?: React.MouseEvent) => {
        if (e && e.stopPropagation) {
            e.stopPropagation();
        }
        setShowPreviewModal(false);
    };

    function render() {
        const videoId = `${item.num}-${Math.random().toString(36).substring(2, 7)}`;
        return (
            // 为整个卡片添加阻止冒泡的处理，优化视觉效果
            <div
                className="overflow-hidden rounded-lg transition-all duration-300"
                style={{
                    background: token.colorBorderBg,
                    border: `1px solid ${token.colorBorderSecondary}`,
                    cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-4px)';
                    e.currentTarget.style.boxShadow = '0 12px 24px rgba(0,0,0,0.15)';
                    e.currentTarget.style.borderColor = token.colorPrimary;
                }}
                onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = 'none';
                    e.currentTarget.style.borderColor = token.colorBorderSecondary;
                }}
            >
                <div style={{ position: 'relative' }}>
                    <VideoCover src={item.cover} />
                    <div style={{
                        position: 'absolute',
                        bottom: '10px',
                        right: '10px',
                        zIndex: 10,
                        display: 'flex',
                        gap: '8px'
                    }}>
                        <Tooltip title="预览图片">
                            <Button
                                type="default"
                                shape="circle"
                                icon={<EyeOutlined />}
                                size="middle"
                                loading={loadingPreview}
                                onClick={handlePreviewClick}
                                style={{ 
                                    boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
                                    background: 'rgba(255,255,255,0.9)'
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
                                style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.3)' }}
                            />
                        </Tooltip>
                    </div>
                </div>
                <div className={'p-3'}>
                    {/* 优化标题显示：使用多行+省略，最多显示2行 */}
                    <Tooltip title={`${item.num} ${item.title || ''}`}>
                        <div
                            style={{
                                fontSize: token.fontSizeHeading5,
                                fontWeight: token.fontWeightStrong,
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                display: '-webkit-box',
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: 'vertical',
                                lineHeight: '1.4',
                                minHeight: '2.8em',
                                marginBottom: '8px'
                            }}>
                            {item.num} {item.title || ''}
                        </div>
                    </Tooltip>
                    {/* 优化评分显示：更清晰的视觉层次 */}
                    <div className={'flex items-center justify-between my-2'}>
                        <Space size={4} align="center">
                            <Rate disabled allowHalf value={item.rank || 0} style={{ fontSize: '14px' }}></Rate>
                            <span style={{
                                fontSize: token.fontSize,
                                fontWeight: 600,
                                color: token.colorPrimary
                            }}>
                                {item.rank?.toFixed(2) || '0.00'}
                            </span>
                        </Space>
                    </div>
                    {/* 评价人数和发布日期 */}
                    <div style={{
                        fontSize: token.fontSizeSM,
                        color: token.colorTextSecondary,
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                    }}>
                        <span>{item.rank_count || 0}人评价</span>
                        <span>{item.publish_date || ''}</span>
                    </div>
                </div>

                {/* 添加下载列表模态框 */}
                <DownloadListModal
                    open={showDownloadList}
                    video={selectedVideo}
                    downloads={downloadOptions}
                    onCancel={handleModalCancel} // 使用自定义的处理函数
                    onDownload={handleDownload} // 使用自定义的处理函数
                    confirmLoading={onDownloading}
                    // 添加Modal的mouseDown和mouseUp事件处理，确保不冒泡
                    modalRender={(modal) => (
                        <div onClick={(e) => e.stopPropagation()} onMouseDown={(e) => e.stopPropagation()} onMouseUp={(e) => e.stopPropagation()}>
                            {modal}
                        </div>
                    )}
                />
                
                {/* 添加预览模态框 */}
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
            <Badge.Ribbon text={'中文'}>
                {render()}
            </Badge.Ribbon>
        ) : (
            render()
        )
    )
}

export default JavDBItem
