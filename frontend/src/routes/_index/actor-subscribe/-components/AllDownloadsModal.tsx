import React, { useState, useEffect } from 'react';
import { Modal, List, Card, Row, Col, Space, Tag, Typography, Button, Tooltip, Avatar, message, Checkbox, Empty, Spin, Input, Select, Radio } from 'antd';
import { DeleteOutlined, UserOutlined, FileOutlined, FilterOutlined, SearchOutlined } from '@ant-design/icons';
import * as api from '../../../../apis/subscribe';
import * as videoApi from '../../../../apis/video';

const { Text } = Typography;
const { Search } = Input;

interface AllDownloadsModalProps {
    open: boolean;
    onCancel: () => void;
    onRefresh: () => void;
}

const AllDownloadsModal: React.FC<AllDownloadsModalProps> = ({ open, onCancel, onRefresh }) => {
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

        Modal.confirm({
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
                <div style={{ display: 'flex', alignItems: 'center' }}>
                    <FileOutlined style={{ marginRight: 8, color: '#1890ff' }} />
                    所有下载记录
                </div>
            }
            open={open}
            onCancel={onCancel}
            footer={null}
            width={800}
            styles={{ body: { maxHeight: '70vh', overflowY: 'auto' } }}
        >
            <div style={{ marginBottom: 16 }}>
                <Row gutter={[16, 16]}>
                    <Col span={24}>
                        <Search
                            placeholder="搜索番号或标题"
                            allowClear
                            enterButton={<SearchOutlined />}
                            onSearch={(value) => setSearchText(value)}
                            style={{ width: '100%' }}
                        />
                    </Col>
                    <Col span={24}>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                            <Select
                                placeholder="按演员筛选"
                                style={{ width: 160 }}
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
                            <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
                                <Tag.CheckableTag
                                    checked={filters.isHd}
                                    onChange={checked => setFilters(prev => ({ ...prev, isHd: checked }))}
                                    style={{ border: '1px solid #d9d9d9', padding: '0 8px' }}
                                >
                                    高清
                                </Tag.CheckableTag>
                                <Tag.CheckableTag
                                    checked={filters.isZh}
                                    onChange={checked => setFilters(prev => ({ ...prev, isZh: checked }))}
                                    style={{ border: '1px solid #d9d9d9', padding: '0 8px' }}
                                >
                                    中文字幕
                                </Tag.CheckableTag>
                                <Tag.CheckableTag
                                    checked={filters.isUncensored}
                                    onChange={checked => setFilters(prev => ({ ...prev, isUncensored: checked }))}
                                    style={{ border: '1px solid #d9d9d9', padding: '0 8px' }}
                                >
                                    无码
                                </Tag.CheckableTag>
                            </div>
                        </div>
                    </Col>
                </Row>
            </div>
            {loading ? (
                <div style={{ textAlign: 'center', padding: '30px 0' }}>
                    <Spin />
                    <div style={{ marginTop: 8 }}>加载中...</div>
                </div>
            ) : filteredDownloads.length > 0 ? (
                <List
                    dataSource={filteredDownloads}
                    renderItem={(item) => (
                        <List.Item>
                            <Card
                                style={{
                                    width: '100%',
                                    borderRadius: '8px',
                                    overflow: 'hidden'
                                }}
                                hoverable
                            >
                                <Row gutter={16} align="middle">
                                    <Col span={4}>
                                        {item.cover ? (
                                            <img
                                                alt={item.title || item.num}
                                                src={videoApi.getVideoCover(item.cover)}
                                                style={{ width: '100%', borderRadius: '4px' }}
                                            />
                                        ) : (
                                            <div style={{
                                                width: '100%',
                                                height: '80px',
                                                background: '#f0f0f0',
                                                display: 'flex',
                                                justifyContent: 'center',
                                                alignItems: 'center',
                                                borderRadius: '4px'
                                            }}>
                                                <FileOutlined style={{ fontSize: 24, color: '#999' }} />
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
                                    <Col span={4} style={{ textAlign: 'right' }}>
                                        <Button
                                            danger
                                            icon={<DeleteOutlined />}
                                            onClick={() => handleDelete(item)}
                                            loading={deleting === item.id}
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