import React, { useState } from 'react';
import { Card, Col, Row, List, Avatar, Tag, Space, Button, message, Tooltip, Empty, Spin, Modal, FloatButton, Badge, Statistic, Typography } from 'antd';
import { UserOutlined, DeleteOutlined, EyeOutlined, PlayCircleOutlined, CalendarOutlined, SettingOutlined, PlusOutlined, SyncOutlined, FileOutlined, EditOutlined } from '@ant-design/icons';
import { createFileRoute, useNavigate } from '@tanstack/react-router';
import * as api from '../../../apis/video';
import * as subscribeApi from '../../../apis/subscribe';
import { useRequest } from 'ahooks';
import { createPortal } from 'react-dom';
import EditSubscribeModal from './-components/EditSubscribeModal';

const { Title, Text } = Typography;

export const Route = createFileRoute('/_index/actor-subscribe/')({
    component: ActorSubscribe
});

function ActorSubscribe() {
    const navigate = useNavigate();
    const [selectedActor, setSelectedActor] = useState<any>(null);
    const [downloadsVisible, setDownloadsVisible] = useState(false);
    const [actorDownloads, setActorDownloads] = useState<any[]>([]);
    const [loadingDownloads, setLoadingDownloads] = useState(false);
    const [editModalVisible, setEditModalVisible] = useState(false);
    const [editingSubscription, setEditingSubscription] = useState<any>(null);

    // 获取订阅的演员列表
    const { data: subscriptions = [], loading, refresh } = useRequest(subscribeApi.getActorSubscriptions, {
        onError: (error) => {
            console.error('获取演员订阅列表失败:', error);
            message.error('获取演员订阅列表失败');
        }
    });

    // 删除订阅
    const { run: deleteSubscription, loading: deleting } = useRequest(subscribeApi.deleteActorSubscription, {
        manual: true,
        onSuccess: () => {
            message.success('已取消订阅');
            refresh();
        },
        onError: (error) => {
            console.error('取消订阅失败:', error);
            message.error('取消订阅失败');
        }
    });

    // 执行演员订阅任务
    const { run: runActorSubscribe, loading: runningTask } = useRequest(subscribeApi.runActorSubscribe, {
        manual: true,
        onSuccess: () => {
            message.success('订阅任务执行成功，请稍后查看下载结果');
        },
        onError: (error) => {
            console.error('执行订阅任务失败:', error);
            message.error('执行订阅任务失败');
        }
    });

    // 查看下载记录
    const handleViewDownloads = async (actor: any) => {
        setSelectedActor(actor);
        setLoadingDownloads(true);
        setDownloadsVisible(true);

        try {
            const downloads = await subscribeApi.getActorSubscriptionDownloads(actor.id);
            setActorDownloads(downloads || []);
        } catch (error) {
            console.error('获取下载记录失败:', error);
            message.error('获取下载记录失败');
        } finally {
            setLoadingDownloads(false);
        }
    };

    // 确认删除
    const confirmDelete = (actor: any) => {
        Modal.confirm({
            title: '确认取消订阅',
            content: `确定要取消订阅演员 ${actor.actor_name} 吗？`,
            okText: '确认',
            cancelText: '取消',
            onOk: () => deleteSubscription(actor.id)
        });
    };

    // 查看演员详情
    const viewActorDetail = (actor: any) => {
        navigate({ to: '/actor', search: { actorName: actor.actor_name } });
    };

    // 编辑订阅
    const handleEditSubscription = (subscription: any) => {
        setEditingSubscription(subscription);
        setEditModalVisible(true);
    };

    // 完成编辑
    const handleEditComplete = () => {
        setEditModalVisible(false);
        setEditingSubscription(null);
        message.success('订阅设置已更新');
        refresh();
    };

    if (loading) {
        return (
            <div className="loading-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '70vh' }}>
                <Spin size="large" tip="加载中..." spinning={true}>
                    <div style={{ padding: '50px', minHeight: '200px' }}></div>
                </Spin>
            </div>
        );
    }

    // 根据最后更新时间获取状态颜色
    const getStatusColor = (lastUpdated: string | null) => {
        if (!lastUpdated) return 'default';

        const lastUpdateDate = new Date(lastUpdated);
        const now = new Date();
        const diffDays = Math.floor((now.getTime() - lastUpdateDate.getTime()) / (1000 * 60 * 60 * 24));

        if (diffDays < 1) return 'success';
        if (diffDays < 3) return 'processing';
        if (diffDays < 7) return 'warning';
        return 'default';
    };

    return (
        <div className="actor-subscribe-container" style={{ padding: '16px' }}>
            <Row gutter={[16, 16]}>
                <Col span={24}>
                    <Card
                        className="header-card"
                        style={{
                            marginBottom: 24,
                            boxShadow: '0 2px 8px rgba(0,0,0,0.09)'
                        }}
                    >
                        <Row align="middle" justify="space-between">
                            <Col>
                                <Title level={4} style={{ margin: 0 }}>
                                    <UserOutlined style={{ marginRight: 8 }} />
                                    演员订阅管理
                                </Title>
                                <Text type="secondary">
                                    共 {subscriptions.length} 个订阅，系统将自动检查新作品并下载
                                </Text>
                            </Col>
                            <Col>
                                <Space>
                                    <Button
                                        type="primary"
                                        icon={<PlusOutlined />}
                                        onClick={() => navigate({ to: '/actor' })}
                                    >
                                        添加订阅
                                    </Button>
                                    <Button
                                        type="default"
                                        icon={<SyncOutlined />}
                                        loading={runningTask}
                                        onClick={() => runActorSubscribe()}
                                    >
                                        立即检查更新
                                    </Button>
                                </Space>
                            </Col>
                        </Row>
                    </Card>
                </Col>
            </Row>

            {subscriptions.length > 0 ? (
                <List
                    grid={{ gutter: 24, xs: 1, sm: 2, md: 3, lg: 3, xl: 4, xxl: 6 }}
                    dataSource={subscriptions}
                    renderItem={(item: any) => {
                        const downloadCount = item.download_count || 0;
                        const statusColor = getStatusColor(item.last_updated);
                        return (
                            <List.Item>
                                <Badge.Ribbon
                                    text={item.last_updated ? `${new Date(item.last_updated).toLocaleDateString()}更新` : '未更新'}
                                    color={statusColor}
                                    style={{ opacity: 0.85 }}
                                >
                                    <Card
                                        hoverable
                                        className="actor-card"
                                        style={{
                                            overflow: 'hidden',
                                            transition: 'all 0.3s',
                                            borderRadius: '8px',
                                            boxShadow: '0 2px 8px rgba(0,0,0,0.09)'
                                        }}
                                        cover={
                                            <div
                                                style={{
                                                    height: '180px',
                                                    display: 'flex',
                                                    justifyContent: 'center',
                                                    alignItems: 'center',
                                                    overflow: 'hidden',
                                                    background: '#f5f5f5',
                                                    position: 'relative'
                                                }}
                                                onClick={() => viewActorDetail(item)}
                                            >
                                                {item.actor_thumb ? (
                                                    <img
                                                        alt={item.actor_name}
                                                        src={api.getVideoCover(item.actor_thumb)}
                                                        style={{
                                                            width: '100%',
                                                            height: '100%',
                                                            objectFit: 'cover',
                                                            transition: 'transform 0.3s'
                                                        }}
                                                    />
                                                ) : (
                                                    <Avatar
                                                        size={100}
                                                        icon={<UserOutlined />}
                                                        style={{ backgroundColor: '#1890ff' }}
                                                    />
                                                )}
                                                <div
                                                    style={{
                                                        position: 'absolute',
                                                        bottom: 0,
                                                        left: 0,
                                                        right: 0,
                                                        padding: '30px 12px 12px',
                                                        background: 'linear-gradient(to top, rgba(0,0,0,0.7), transparent)',
                                                        color: 'white'
                                                    }}
                                                >
                                                    <Typography.Title level={5} style={{ color: 'white', margin: 0 }}>
                                                        {item.actor_name}
                                                    </Typography.Title>
                                                </div>
                                            </div>
                                        }
                                        actions={[
                                            <Tooltip title="查看演员详情">
                                                <EyeOutlined key="view" onClick={() => viewActorDetail(item)} />
                                            </Tooltip>,
                                            <Tooltip title="查看下载记录">
                                                <PlayCircleOutlined key="download" onClick={() => handleViewDownloads(item)} />
                                            </Tooltip>,
                                            <Tooltip title="编辑订阅">
                                                <EditOutlined key="edit" onClick={() => handleEditSubscription(item)} />
                                            </Tooltip>,
                                            <Tooltip title="取消订阅">
                                                <DeleteOutlined
                                                    key="delete"
                                                    onClick={() => confirmDelete(item)}
                                                />
                                            </Tooltip>
                                        ]}
                                    >
                                        <div style={{ padding: '0 4px' }}>
                                            <Row gutter={[16, 8]}>
                                                <Col span={12}>
                                                    <Statistic
                                                        title="订阅日期"
                                                        value={item.from_date}
                                                        valueStyle={{ fontSize: '14px' }}
                                                        prefix={<CalendarOutlined />}
                                                    />
                                                </Col>
                                                <Col span={12}>
                                                    <Statistic
                                                        title="已下载"
                                                        value={downloadCount}
                                                        suffix="部"
                                                        valueStyle={{ fontSize: '14px' }}
                                                    />
                                                </Col>
                                            </Row>
                                            <div style={{ marginTop: 12 }}>
                                                <Space size={[0, 8]} wrap>
                                                    {item.is_hd && <Tag color="blue">高清</Tag>}
                                                    {item.is_zh && <Tag color="green">中文字幕</Tag>}
                                                    {item.is_uncensored && <Tag color="red">无码</Tag>}
                                                </Space>
                                            </div>
                                        </div>
                                    </Card>
                                </Badge.Ribbon>
                            </List.Item>
                        );
                    }}
                />
            ) : (
                <Card style={{ textAlign: 'center', padding: '40px 0' }}>
                    <Empty
                        description={
                            <span>
                                暂无订阅的演员 <br />
                                <Button
                                    type="primary"
                                    icon={<PlusOutlined />}
                                    style={{ marginTop: 16 }}
                                    onClick={() => navigate({ to: '/actor' })}
                                >
                                    添加订阅
                                </Button>
                            </span>
                        }
                    />
                </Card>
            )}

            {/* 下载记录模态框 */}
            <Modal
                title={
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                        <PlayCircleOutlined style={{ marginRight: 8, color: '#1890ff' }} />
                        {selectedActor ? `${selectedActor.actor_name} 的下载记录` : '下载记录'}
                    </div>
                }
                open={downloadsVisible}
                onCancel={() => setDownloadsVisible(false)}
                footer={null}
                width={800}
                styles={{ body: { maxHeight: '70vh', overflowY: 'auto' } }}
            >
                {loadingDownloads ? (
                    <div style={{ textAlign: 'center', padding: '30px 0' }}>
                        <Spin />
                        <div style={{ marginTop: 8 }}>加载中...</div>
                    </div>
                ) : actorDownloads.length > 0 ? (
                    <List
                        dataSource={actorDownloads}
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
                                                    src={api.getVideoCover(item.cover)}
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
                                        <Col span={20}>
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
                                    </Row>
                                </Card>
                            </List.Item>
                        )}
                    />
                ) : (
                    <Empty description="暂无下载记录" />
                )}
            </Modal>

            {/* 编辑订阅模态框 */}
            <EditSubscribeModal
                open={editModalVisible}
                subscription={editingSubscription}
                onCancel={() => setEditModalVisible(false)}
                onOk={handleEditComplete}
            />

            {/* 悬浮按钮 */}
            <FloatButton.Group
                trigger="hover"
                style={{ right: 24, bottom: 24 }}
                icon={<SettingOutlined />}
            >
                <FloatButton
                    icon={<PlusOutlined />}
                    tooltip="添加订阅"
                    onClick={() => navigate({ to: '/actor' })}
                />
                <FloatButton
                    icon={runningTask ? <SyncOutlined spin /> : <SyncOutlined />}
                    tooltip="立即检查更新"
                    onClick={() => runActorSubscribe()}
                />
            </FloatButton.Group>
        </div>
    );
}

export default ActorSubscribe; 