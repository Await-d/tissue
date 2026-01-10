import { List, Modal, ModalProps, Space, Tag, Button, Input, Typography, Card, Row, Col, Divider, Badge, Tooltip } from "antd";
import React, { useEffect, useState } from "react";
import { CloudDownloadOutlined, CheckCircleOutlined, CalendarOutlined, GlobalOutlined, FileOutlined, SettingOutlined } from "@ant-design/icons";
import { useThemeColors } from '../../../../hooks/useThemeColors';

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
    const colors = useThemeColors()

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
                    <CloudDownloadOutlined style={{ marginRight: 10, color: colors.goldPrimary, fontSize: 22 }} />
                    <span style={{ color: colors.goldLight, fontWeight: 600 }}>选择下载资源</span>
                    {video && video.title &&
                        <Tooltip title={video.title}>
                            <span style={{ marginLeft: 10, fontSize: '14px', color: colors.textTertiary, maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                - {video.num}
                            </span>
                        </Tooltip>
                    }
                </div>
            }
            {...otherProps}
            footer={[
                <Button
                    key="cancel"
                    onClick={props.onCancel}
                    style={{
                        background: colors.bgContainer,
                        border: `1px solid ${colors.borderPrimary}`,
                        color: colors.textSecondary
                    }}
                >
                    取消
                </Button>,
                <Button
                    key="download"
                    type="primary"
                    disabled={!selectedItem}
                    loading={confirmLoading}
                    icon={<CloudDownloadOutlined />}
                    onClick={handleDownload}
                    style={{
                        background: selectedItem ? colors.goldGradientHover : colors.bgSpotlight,
                        border: 'none',
                        color: selectedItem ? colors.bgBase : colors.textTertiary,
                        fontWeight: 600
                    }}
                >
                    下载
                </Button>
            ]}
            width={700}
            centered
            styles={{
                mask: { backdropFilter: 'blur(8px)', background: colors.modalOverlay },
                content: {
                    background: colors.modalBg,
                    border: `1px solid ${colors.borderPrimary}`,
                    boxShadow: '0 12px 48px rgba(0, 0, 0, 0.6)'
                },
                body: { maxHeight: '60vh', overflowY: 'auto', padding: '12px 24px' }
            }}
        >
            <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography.Text style={{ color: colors.textPrimary }}>
                    共找到 <Typography.Text strong style={{ color: colors.goldLight }}>{downloads?.length || 0}</Typography.Text> 个下载资源:
                </Typography.Text>

                <Space>
                    <Tag
                        icon={<FileOutlined />}
                        style={{ background: colors.bgSpotlight, border: `1px solid ${colors.borderPrimary}`, color: colors.textSecondary }}
                    >文件大小</Tag>
                    <Tag
                        icon={<CalendarOutlined />}
                        style={{ background: colors.bgSpotlight, border: `1px solid ${colors.borderPrimary}`, color: colors.textSecondary }}
                    >发布日期</Tag>
                    <Tag
                        icon={<SettingOutlined />}
                        style={{ background: colors.bgSpotlight, border: `1px solid ${colors.borderPrimary}`, color: colors.textSecondary }}
                    >资源特性</Tag>
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
                                borderColor: selectedItem === item ? colors.goldPrimary : colors.borderPrimary,
                                backgroundColor: selectedItem === item ? colors.bgSpotlight : colors.bgContainer,
                                transition: 'all 0.3s',
                                cursor: 'pointer',
                                boxShadow: selectedItem === item ? colors.shadowGold : 'none'
                            }}
                            styles={{ body: { padding: 16 } }}
                            onClick={() => handleSelectItem(item)}
                            onMouseEnter={(e) => {
                                if (selectedItem !== item) {
                                    e.currentTarget.style.borderColor = colors.goldPrimary;
                                    e.currentTarget.style.transform = 'translateY(-2px)';
                                }
                            }}
                            onMouseLeave={(e) => {
                                if (selectedItem !== item) {
                                    e.currentTarget.style.borderColor = colors.borderPrimary;
                                    e.currentTarget.style.transform = 'translateY(0)';
                                }
                            }}
                        >
                            <Row gutter={16} align="middle">
                                <Col span={16}>
                                    <div style={{ display: 'flex', alignItems: 'center' }}>
                                        <CloudDownloadOutlined style={{
                                            fontSize: 20,
                                            marginRight: 12,
                                            color: selectedItem === item ? colors.goldPrimary : colors.textTertiary
                                        }} />
                                        <Typography.Title level={5} style={{ margin: 0, color: colors.textPrimary }}>
                                            {item.name}
                                            {selectedItem === item &&
                                                <CheckCircleOutlined style={{ color: colors.goldPrimary, marginLeft: 8, fontSize: 16 }} />
                                            }
                                        </Typography.Title>
                                    </div>

                                    <div style={{ marginTop: 8, marginLeft: 32 }}>
                                        <Space wrap>
                                            <Tag
                                                icon={<GlobalOutlined />}
                                                style={{ background: colors.bgBase, border: `1px solid ${colors.borderPrimary}`, color: colors.textSecondary }}
                                            >{item.website}</Tag>
                                            {item.publish_date &&
                                                <Tag
                                                    icon={<CalendarOutlined />}
                                                    style={{ background: colors.bgBase, border: `1px solid ${colors.borderPrimary}`, color: colors.textSecondary }}
                                                >{item.publish_date}</Tag>
                                            }
                                        </Space>
                                    </div>
                                </Col>

                                <Col span={8}>
                                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'flex-end' }}>
                                        <Tag
                                            style={{
                                                minWidth: 60,
                                                textAlign: 'center',
                                                background: colors.bgSpotlight,
                                                border: `1px solid ${colors.borderPrimary}`,
                                                color: colors.goldLight,
                                                fontWeight: 600
                                            }}
                                        >{item.size}</Tag>
                                        {item.is_hd && <Tag style={{ background: colors.goldGlow, border: `1px solid ${colors.goldPrimary}`, color: colors.goldLight }}>高清</Tag>}
                                        {item.is_zh && <Tag style={{ background: colors.goldGlow, border: `1px solid ${colors.goldPrimary}`, color: colors.goldLight }}>中文</Tag>}
                                        {item.is_uncensored && <Tag style={{ background: colors.goldGlow, border: `1px solid ${colors.goldPrimary}`, color: colors.goldLight }}>无码</Tag>}
                                    </div>
                                </Col>
                            </Row>
                        </Card>
                    </Badge.Ribbon>
                )}
            />

            {selectedItem && (
                <div style={{
                    marginTop: 16,
                    padding: '16px',
                    backgroundColor: colors.bgBase,
                    borderRadius: '8px',
                    border: `1px solid ${colors.borderPrimary}`
                }}>
                    <Typography.Text strong style={{ display: 'block', marginBottom: 8, color: colors.goldLight }}>
                        下载设置
                    </Typography.Text>
                    <Space.Compact style={{ width: '100%' }}>
                        <Button
                            disabled
                            icon={<SettingOutlined />}
                            style={{
                                background: colors.bgContainer,
                                border: `1px solid ${colors.borderPrimary}`,
                                color: colors.textTertiary
                            }}
                        />
                        <Input
                            placeholder="请输入保存路径（留空则使用默认路径）"
                            value={savePath}
                            onChange={(e) => setSavePath(e.target.value)}
                            allowClear
                            style={{
                                background: colors.bgElevated,
                                border: `1px solid ${colors.borderPrimary}`,
                                color: colors.textPrimary
                            }}
                            onFocus={(e) => {
                                e.currentTarget.style.borderColor = colors.goldPrimary;
                                e.currentTarget.style.boxShadow = colors.rgba('gold', 0.1);
                            }}
                            onBlur={(e) => {
                                e.currentTarget.style.borderColor = colors.borderPrimary;
                                e.currentTarget.style.boxShadow = 'none';
                            }}
                        />
                    </Space.Compact>
                </div>
            )}
        </Modal>
    );
}

export default DownloadListModal; 