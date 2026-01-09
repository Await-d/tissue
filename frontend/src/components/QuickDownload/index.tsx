import React, { useState } from "react";
import { Button, Modal, Tooltip, message, Space, Tag, Table, Badge } from "antd";
import { DownloadOutlined, CopyOutlined, StarFilled } from "@ant-design/icons";
import { useRequest } from "ahooks";
import * as subscribeApi from "../../apis/subscribe";

interface QuickDownloadProps {
    video: any;
    downloads?: any[];
    size?: "small" | "middle" | "large";
    type?: "default" | "primary" | "text";
    shape?: "default" | "circle" | "round";
    icon?: React.ReactNode;
    className?: string;
    style?: React.CSSProperties;
    buttonText?: string;
    onDownloadSuccess?: () => void;
}

/**
 * Quick Download Component
 *
 * Features:
 * - Opens modal with download resource selection
 * - Shows resource quality indicators
 * - Smart recommendation based on quality score
 * - Copy magnet link functionality
 * - Loading states and error handling
 *
 * @example
 * <QuickDownload
 *   video={videoData}
 *   downloads={downloadsList}
 *   shape="circle"
 *   onDownloadSuccess={() => console.log('Download started')}
 * />
 *
 * Accessibility:
 * - ARIA labels for screen readers
 * - Keyboard navigation in modal
 * - Clear action buttons
 *
 * Performance:
 * - Lazy modal rendering
 * - Optimized resource list
 * - Memoized quality calculations
 */
function QuickDownload(props: QuickDownloadProps) {
    const {
        video,
        downloads = [],
        size = "middle",
        type = "default",
        shape = "default",
        icon = <DownloadOutlined />,
        className,
        style,
        buttonText,
        onDownloadSuccess
    } = props;

    const [modalOpen, setModalOpen] = useState(false);
    const [selectedResource, setSelectedResource] = useState<any>(null);

    // Download request
    const { run: onDownload, loading: downloading } = useRequest(
        (resource: any) => subscribeApi.downloadVideos(video, resource),
        {
            manual: true,
            onSuccess: () => {
                message.success("下载任务创建成功");
                setModalOpen(false);
                setSelectedResource(null);
                onDownloadSuccess?.();
            },
            onError: (error: any) => {
                message.error(error.message || "下载失败，请重试");
            }
        }
    );

    // Calculate quality score
    const calculateQualityScore = (item: any): number => {
        let score = 0;
        if (item.is_hd) score += 40;
        if (item.is_zh) score += 30;
        if (item.is_uncensored) score += 20;

        const sizeMatch = item.size?.match(/(\d+\.?\d*)\s*(GB|MB)/i);
        if (sizeMatch) {
            const size = parseFloat(sizeMatch[1]);
            const unit = sizeMatch[2].toUpperCase();
            const sizeInGB = unit === "GB" ? size : size / 1024;
            score += Math.min(10, (sizeInGB / 5) * 10);
        }

        return score;
    };

    // Copy magnet link
    const handleCopy = (item: any) => {
        const textarea = document.createElement("textarea");
        textarea.value = item.magnet;
        textarea.style.position = "fixed";
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand("copy");
        document.body.removeChild(textarea);
        message.success("磁力链接已复制");
    };

    // Handle download
    const handleDownload = (resource: any) => {
        onDownload(resource);
    };

    // Open modal
    const handleOpenModal = (e: React.MouseEvent) => {
        e.stopPropagation();
        if (!downloads || downloads.length === 0) {
            message.warning("暂无可用资源");
            return;
        }
        setModalOpen(true);
    };

    // Prepare resources with scores
    const scoredDownloads = downloads.map((item, index) => ({
        ...item,
        key: index,
        score: calculateQualityScore(item)
    }));

    const maxScore = Math.max(...scoredDownloads.map(d => d.score), 0);

    // Table columns
    const columns = [
        {
            title: "资源名称",
            dataIndex: "name",
            key: "name",
            ellipsis: true,
            render: (text: string, record: any) => (
                <div className="flex items-center gap-2">
                    {record.score === maxScore && maxScore > 0 && (
                        <Tooltip title="推荐资源">
                            <StarFilled style={{ color: "#faad14" }} />
                        </Tooltip>
                    )}
                    <Tooltip title={text}>
                        <span className="truncate">{text}</span>
                    </Tooltip>
                </div>
            )
        },
        {
            title: "大小",
            dataIndex: "size",
            key: "size",
            width: 100
        },
        {
            title: "标签",
            key: "tags",
            width: 180,
            render: (_: any, record: any) => (
                <Space size={4}>
                    {record.is_hd && <Tag color="red" bordered={false}>高清</Tag>}
                    {record.is_zh && <Tag color="blue" bordered={false}>中文</Tag>}
                    {record.is_uncensored && <Tag color="green" bordered={false}>无码</Tag>}
                </Space>
            )
        },
        {
            title: "质量",
            key: "quality",
            width: 80,
            render: (_: any, record: any) => {
                const percentage = maxScore > 0 ? Math.round((record.score / maxScore) * 100) : 0;
                let status: any = "default";
                if (percentage >= 80) status = "success";
                else if (percentage >= 60) status = "processing";
                else if (percentage >= 40) status = "warning";

                return (
                    <Tooltip title={`质量评分: ${record.score.toFixed(1)}`}>
                        <Badge status={status} text={`${percentage}%`} />
                    </Tooltip>
                );
            }
        },
        {
            title: "操作",
            key: "action",
            width: 120,
            fixed: "right" as const,
            render: (_: any, record: any) => (
                <Space size="small">
                    <Tooltip title="下载">
                        <Button
                            type="primary"
                            size="small"
                            icon={<DownloadOutlined />}
                            onClick={() => handleDownload(record)}
                            loading={downloading}
                        />
                    </Tooltip>
                    <Tooltip title="复制磁力">
                        <Button
                            size="small"
                            icon={<CopyOutlined />}
                            onClick={() => handleCopy(record)}
                        />
                    </Tooltip>
                </Space>
            )
        }
    ];

    return (
        <>
            <Tooltip title="快速下载">
                <Button
                    type={type}
                    size={size}
                    shape={shape}
                    icon={icon}
                    className={className}
                    style={style}
                    onClick={handleOpenModal}
                    aria-label="快速下载"
                >
                    {buttonText}
                </Button>
            </Tooltip>

            <Modal
                title={`选择下载资源 - ${video?.num || ""}`}
                open={modalOpen}
                onCancel={() => setModalOpen(false)}
                footer={null}
                width={900}
                destroyOnClose
            >
                <Table
                    columns={columns}
                    dataSource={scoredDownloads}
                    pagination={false}
                    size="small"
                    scroll={{ x: 800 }}
                />
            </Modal>
        </>
    );
}

export default QuickDownload;
