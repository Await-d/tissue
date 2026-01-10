import React, { useState, useEffect } from 'react';
import { Modal, List, Card, Row, Col, Space, Tag, Typography, Button, Tooltip, Avatar, App, Checkbox, Empty, Spin, Input, Select, Radio } from 'antd';
import { DeleteOutlined, UserOutlined, FileOutlined, FilterOutlined, SearchOutlined } from '@ant-design/icons';
import * as api from '../../../../apis/subscribe';
import * as videoApi from '../../../../apis/video';
import './AllDownloadsModal.css';

const { Text } = Typography;

interface AllDownloadsModalProps {
    open: boolean;
    onCancel: () => void;
    onRefresh: () => void;
}

const AllDownloadsModal: React.FC<AllDownloadsModalProps> = ({ open, onCancel, onRefresh }) => {
    const { message, modal } = App.useApp();
    const [downloads, setDownloads] = useState<any[]>([]);
    const [filteredDownloads, setFilteredDownloads] = useState<any[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [deleting, setDeleting] = useState<number | null>(null);
    const [searchText, setSearchText] = useState<string>('');
    const [filters, setFilters] = useState({
        actor: '',
        isHd: false,
        isZh: false,
        isUncensored: false
    });

    useEffect(() => {
        if (open) {
            loadDownloads();
        }
    }, [open]);

    // 当下载列表或筛选条件变化时，应用筛选
    useEffect(() => {
        applyFilters();
    }, [downloads, filters, searchText]);

    const loadDownloads = async () => {
        setLoading(true);
        try {
            const data = await api.getAllSubscriptionDownloads();
            setDownloads(data || []);
            setFilteredDownloads(data || []);
        } catch (error) {
            console.error('获取下载记录失败:', error);
            message.error('获取下载记录失败');
        } finally {
            setLoading(false);
        }
    };

    // 应用筛选条件
    const applyFilters = () => {
        if (!downloads.length) return;

        let result = [...downloads];

        // 按演员名称筛选
        if (filters.actor) {
            result = result.filter(item =>
                item.actor_name.toLowerCase().includes(filters.actor.toLowerCase())
            );
        }

        // 按标签筛选
        if (filters.isHd) {
            result = result.filter(item => item.is_hd);
        }

        if (filters.isZh) {
            result = result.filter(item => item.is_zh);
        }

        if (filters.isUncensored) {
            result = result.filter(item => item.is_uncensored);
        }

        // 按搜索文本筛选（番号或标题）
        if (searchText) {
            result = result.filter(item =>
                (item.num && item.num.toLowerCase().includes(searchText.toLowerCase())) ||
                (item.title && item.title.toLowerCase().includes(searchText.toLowerCase()))
            );
        }

        setFilteredDownloads(result);
    };

    const handleDelete = (download: any) => {
        let deleteFiles = false;

        modal.confirm({
            title: '确认删除下载记录',
            content: (
                <div>
                    <p>确定要删除 <strong>{download.num}</strong> 的下载记录吗？</p>
                    <div style={{ marginTop: '16px' }}>
                        <Checkbox
                            onChange={(e: any) => {
                                deleteFiles = e.target.checked;
                            }}
                        >
                            同时删除已下载的文件和下载任务
                        </Checkbox>
                        <div style={{ fontSize: '12px', color: '#999', marginTop: '4px' }}>
                            选中此项将从qBittorrent中删除该下载任务和文件
                        </div>
                    </div>
                </div>
            ),
            okText: '确认删除',
            cancelText: '取消',
            okType: 'danger',
            width: 450,
            onOk: async () => {
                setDeleting(download.id);
                try {
                    await api.deleteSubscriptionDownload(download.id, deleteFiles);
                    message.success('删除成功');
                    loadDownloads();
                    onRefresh();
                } catch (error) {
                    console.error('删除失败:', error);
                    message.error('删除失败');
                } finally {
                    setDeleting(null);
                }
            }
        });
    };

    return (
        <Modal
            title={
                <div className="all-downloads-modal-title">
                    <FileOutlined className="all-downloads-modal-icon" />
                    所有下载记录
                </div>
            }
            open={open}
            onCancel={onCancel}
            footer={null}
            width={800}
            className="all-downloads-modal"
        >
            <div className="all-downloads-filter-section">
                <Row gutter={[16, 16]}>
                    <Col span={24}>
                        <Space.Compact style={{ width: '100%' }}>
                            <Input
                                placeholder="搜索番号或标题"
                                allowClear
                                value={searchText}
                                onChange={(e) => setSearchText(e.target.value)}
                                onPressEnter={() => applyFilters()}
                                className="all-downloads-search"
                            />
                            <Button
                                type="primary"
                                icon={<SearchOutlined />}
                                onClick={() => applyFilters()}
                            />
                        </Space.Compact>
                    </Col>
                    <Col span={24}>
                        <div className="all-downloads-filter-tags">
                            <Select
                                placeholder="按演员筛选"
                                className="all-downloads-select"
                                allowClear
                                onChange={(value) => setFilters(prev => ({ ...prev, actor: value || '' }))}
                                options={Array.from(new Set((downloads || [])
                                    .filter(item => item?.actor_name)
                                    .map(item => item.actor_name)
                                )).map(name => ({
                                    label: name,
                                    value: name
                                }))}
                            />
                            <div className="all-downloads-checkable-tags">
                                <Tag.CheckableTag
                                    checked={filters.isHd}
                                    onChange={checked => setFilters(prev => ({ ...prev, isHd: checked }))}
                                    className="all-downloads-tag"
                                >
                                    高清
                                </Tag.CheckableTag>
                                <Tag.CheckableTag
                                    checked={filters.isZh}
                                    onChange={checked => setFilters(prev => ({ ...prev, isZh: checked }))}
                                    className="all-downloads-tag"
                                >
                                    中文字幕
                                </Tag.CheckableTag>
                                <Tag.CheckableTag
                                    checked={filters.isUncensored}
                                    onChange={checked => setFilters(prev => ({ ...prev, isUncensored: checked }))}
                                    className="all-downloads-tag"
                                >
                                    无码
                                </Tag.CheckableTag>
                            </div>
                        </div>
                    </Col>
                </Row>
            </div>
            {loading ? (
                <div className="all-downloads-loading">
                    <Spin />
                    <div className="all-downloads-loading-text">加载中...</div>
                </div>
            ) : filteredDownloads.length > 0 ? (
                <List
                    dataSource={filteredDownloads}
                    renderItem={(item) => (
                        <List.Item>
                            <Card
                                className="all-downloads-card"
                                hoverable
                            >
                                <Row gutter={16} align="middle">
                                    <Col span={4}>
                                        {item.cover ? (
                                            <img
                                                alt={item.title || item.num}
                                                src={videoApi.getVideoCover(item.cover)}
                                                className="all-downloads-cover"
                                            />
                                        ) : (
                                            <div className="all-downloads-placeholder">
                                                <FileOutlined className="all-downloads-placeholder-icon" />
                                            </div>
                                        )}
                                    </Col>
                                    <Col span={16}>
                                        <Card.Meta
                                            title={
                                                <Tooltip title={item.title}>
                                                    <div style={{
                                                        whiteSpace: 'nowrap',
                                                        overflow: 'hidden',
                                                        textOverflow: 'ellipsis'
                                                    }}>
                                                        {item.title || item.num}
                                                    </div>
                                                </Tooltip>
                                            }
                                            description={
                                                <Space direction="vertical" size="small" style={{ width: '100%' }}>
                                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                                        <Text strong>番号: {item.num}</Text>
                                                        <Text type="secondary">下载时间: {new Date(item.download_time).toLocaleString()}</Text>
                                                    </div>
                                                    <div>
                                                        <Space>
                                                            <Tag color="purple">{item.actor_name}</Tag>
                                                            {item.size && <Tag color="blue">{item.size}</Tag>}
                                                            {item.is_hd && <Tag color="blue">高清</Tag>}
                                                            {item.is_zh && <Tag color="green">中文字幕</Tag>}
                                                            {item.is_uncensored && <Tag color="red">无码</Tag>}
                                                        </Space>
                                                    </div>
                                                </Space>
                                            }
                                        />
                                    </Col>
                                    <Col span={4} className="all-downloads-action-col">
                                        <Button
                                            danger
                                            icon={<DeleteOutlined />}
                                            onClick={() => handleDelete(item)}
                                            loading={deleting === item.id}
                                            className="all-downloads-delete-btn"
                                        >
                                            删除
                                        </Button>
                                    </Col>
                                </Row>
                            </Card>
                        </List.Item>
                    )}
                />
            ) : downloads.length > 0 ? (
                <Empty description="没有符合筛选条件的下载记录" />
            ) : (
                <Empty description="暂无下载记录" />
            )}
        </Modal>
    );
};

export default AllDownloadsModal; 