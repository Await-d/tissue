import { List, Modal, ModalProps, Space, Tag, Button, Input, Typography } from "antd";
import React, { useEffect, useState } from "react";
import { CloudDownloadOutlined } from "@ant-design/icons";

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

    return (
        <Modal
            title="选择下载资源"
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
                    onClick={handleDownload}
                >
                    下载
                </Button>
            ]}
            width={600}
        >
            <Typography.Paragraph>
                共找到 {downloads?.length || 0} 个下载资源，请选择一个资源进行下载：
            </Typography.Paragraph>

            <List
                dataSource={downloads || []}
                renderItem={(item: any) => (
                    <List.Item
                        className="cursor-pointer"
                        style={{
                            background: selectedItem === item ? '#e6f7ff' : 'transparent',
                            border: selectedItem === item ? '1px solid #1890ff' : '1px solid transparent',
                            borderRadius: '4px',
                            padding: '8px',
                            marginBottom: '8px'
                        }}
                        onClick={() => handleSelectItem(item)}
                    >
                        <List.Item.Meta
                            title={
                                <div style={{ display: 'flex', alignItems: 'center' }}>
                                    <CloudDownloadOutlined style={{ marginRight: 8, color: '#1890ff' }} />
                                    <span>{item.name}</span>
                                </div>
                            }
                            description={(
                                <Space direction="vertical" size="small">
                                    <div>
                                        <Tag>{item.website}</Tag>
                                        <Tag>{item.size}</Tag>
                                        {item.publish_date && <Tag>{item.publish_date}</Tag>}
                                    </div>
                                    <div>
                                        {item.is_hd && <Tag color="red" bordered={false}>高清</Tag>}
                                        {item.is_zh && <Tag color="blue" bordered={false}>中文</Tag>}
                                        {item.is_uncensored && <Tag color="green" bordered={false}>无码</Tag>}
                                    </div>
                                </Space>
                            )}
                        />
                    </List.Item>
                )}
            />

            {selectedItem && (
                <div style={{ marginTop: 16 }}>
                    <Input
                        placeholder="请输入保存路径（留空则使用默认路径）"
                        value={savePath}
                        onChange={(e) => setSavePath(e.target.value)}
                        addonBefore="保存路径"
                    />
                </div>
            )}
        </Modal>
    );
}

export default DownloadListModal; 