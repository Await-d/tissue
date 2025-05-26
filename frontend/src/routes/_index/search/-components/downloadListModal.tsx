import { List, Modal, ModalProps, Space, Tag, Button, Input, Typography, Card, Row, Col, Divider, Badge, Tooltip } from "antd";
import React, { useEffect, useState } from "react";
import { CloudDownloadOutlined, CheckCircleOutlined, CalendarOutlined, GlobalOutlined, FileOutlined, SettingOutlined } from "@ant-design/icons";

interface Props extends ModalProps {
    video?: any;
    downloads?: any[];
    onDownload: (video: any, item: any) => void;
    confirmLoading?: boolean;
}

function DownloadListModal(props: Props) {
    const { video, downloads, onDownload, confirmLoading, ...otherProps } = props;
    const [selectedItem, setSelectedItem] = useState<any>(null);
    const [savePath, setSavePath] = useState<string>("");

    useEffect(() => {
        // 重置选择状态和保存路径
        if (props.open) {
            setSelectedItem(null);
            setSavePath("");
        }
    }, [props.open]);

    const handleSelectItem = (item: any) => {
        setSelectedItem(item);
    };

    const handleDownload = () => {
        if (!selectedItem) {
            return;
        }

        const downloadItem = {
            ...selectedItem,
            savepath: savePath || undefined
        };

        onDownload(video, downloadItem);
    };

    // 根据文件大小选择背景颜色
    const getSizeColor = (size: string) => {
        if (!size) return "";

        if (size.includes("GB")) {
            const num = parseFloat(size);
            if (num > 10) return "#f5222d15"; // 红色背景，体积很大
            if (num > 5) return "#fa541c15";  // 橙色背景，体积较大
            return "#52c41a15"; // 绿色背景，体积适中
        }
        return "#1890ff15"; // 蓝色背景，体积较小
    };

    return (
        <Modal
            title={
                <div style={{ display: 'flex', alignItems: 'center' }}>
                    <CloudDownloadOutlined style={{ marginRight: 10, color: '#1890ff', fontSize: 22 }} />
                    <span>选择下载资源</span>
                    {video && video.title &&
                        <Tooltip title={video.title}>
                            <span style={{ marginLeft: 10, fontSize: '14px', color: '#888', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                - {video.num}
                            </span>
                        </Tooltip>
                    }
                </div>
            }
            {...otherProps}
            footer={[
                <Button key="cancel" onClick={props.onCancel}>
                    取消
                </Button>,
                <Button
                    key="download"
                    type="primary"
                    disabled={!selectedItem}
                    loading={confirmLoading}
                    icon={<CloudDownloadOutlined />}
                    onClick={handleDownload}
                >
                    下载
                </Button>
            ]}
            width={700}
            centered
            styles={{ body: { maxHeight: '60vh', overflowY: 'auto', padding: '12px 24px' } }}
        >
            <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography.Text>
                    共找到 <Typography.Text strong>{downloads?.length || 0}</Typography.Text> 个下载资源:
                </Typography.Text>

                <Space>
                    <Tag icon={<FileOutlined />} color="blue">文件大小</Tag>
                    <Tag icon={<CalendarOutlined />} color="purple">发布日期</Tag>
                    <Tag icon={<SettingOutlined />} color="orange">资源特性</Tag>
                </Space>
            </div>

            <Divider style={{ margin: '8px 0 16px' }} />

            <List
                dataSource={downloads || []}
                renderItem={(item: any) => (
                    <Badge.Ribbon
                        text={item.size}
                        color={item.is_hd ? "red" : "blue"}
                        style={{ opacity: 0.8, display: selectedItem === item ? 'block' : 'none' }}
                    >
                        <Card
                            hoverable
                            style={{
                                marginBottom: 16,
                                borderColor: selectedItem === item ? '#1890ff' : '#f0f0f0',
                                backgroundColor: selectedItem === item ? '#e6f7ff' : getSizeColor(item.size),
                                transition: 'all 0.3s'
                            }}
                            bodyStyle={{ padding: 16 }}
                            onClick={() => handleSelectItem(item)}
                        >
                            <Row gutter={16} align="middle">
                                <Col span={16}>
                                    <div style={{ display: 'flex', alignItems: 'center' }}>
                                        <CloudDownloadOutlined style={{
                                            fontSize: 20,
                                            marginRight: 12,
                                            color: selectedItem === item ? '#1890ff' : '#8c8c8c'
                                        }} />
                                        <Typography.Title level={5} style={{ margin: 0 }}>
                                            {item.name}
                                            {selectedItem === item &&
                                                <CheckCircleOutlined style={{ color: '#52c41a', marginLeft: 8, fontSize: 16 }} />
                                            }
                                        </Typography.Title>
                                    </div>

                                    <div style={{ marginTop: 8, marginLeft: 32 }}>
                                        <Space wrap>
                                            <Tag icon={<GlobalOutlined />} color="cyan">{item.website}</Tag>
                                            {item.publish_date &&
                                                <Tag icon={<CalendarOutlined />} color="purple">{item.publish_date}</Tag>
                                            }
                                        </Space>
                                    </div>
                                </Col>

                                <Col span={8}>
                                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'flex-end' }}>
                                        <Tag color="blue" style={{ minWidth: 60, textAlign: 'center' }}>{item.size}</Tag>
                                        {item.is_hd && <Tag color="red" bordered={false}>高清</Tag>}
                                        {item.is_zh && <Tag color="blue" bordered={false}>中文</Tag>}
                                        {item.is_uncensored && <Tag color="green" bordered={false}>无码</Tag>}
                                    </div>
                                </Col>
                            </Row>
                        </Card>
                    </Badge.Ribbon>
                )}
            />

            {selectedItem && (
                <div style={{ marginTop: 16, padding: '16px', backgroundColor: '#f9f9f9', borderRadius: '4px' }}>
                    <Typography.Text strong style={{ display: 'block', marginBottom: 8 }}>
                        下载设置
                    </Typography.Text>
                    <Input
                        placeholder="请输入保存路径（留空则使用默认路径）"
                        value={savePath}
                        onChange={(e) => setSavePath(e.target.value)}
                        addonBefore={<SettingOutlined />}
                        allowClear
                    />
                </div>
            )}
        </Modal>
    );
}

export default DownloadListModal; 