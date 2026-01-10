import React, { useState } from 'react';
import { Card, Col, Row, List, Avatar, Tag, Space, Button, App, Tooltip, Empty, Spin, Modal, FloatButton, Badge, Statistic, Typography, Checkbox } from 'antd';
import { UserOutlined, DeleteOutlined, EyeOutlined, PlayCircleOutlined, CalendarOutlined, PlusOutlined, SyncOutlined, FileOutlined, EditOutlined, PauseOutlined, PlaySquareOutlined, DatabaseOutlined } from '@ant-design/icons';
import { createFileRoute, useNavigate } from '@tanstack/react-router';
import * as api from '../../../apis/video';
import * as subscribeApi from '../../../apis/subscribe';
import { useRequest } from 'ahooks';
import { createPortal } from 'react-dom';
import { useThemeColors } from '../../../hooks/useThemeColors';
import EditSubscribeModal from './-components/EditSubscribeModal';
import AllDownloadsModal from './-components/AllDownloadsModal';
import LoadingComponent from '@/components/Loading';
import './styles.css';

const { Title, Text } = Typography;

export const Route = createFileRoute('/_index/actor-subscribe/')({
    component: ActorSubscribe
});

function ActorSubscribe() {
    const { message, modal } = App.useApp();
    const navigate = useNavigate();
    const colors = useThemeColors();
    const [selectedActor, setSelectedActor] = useState<any>(null);
    const [downloadsVisible, setDownloadsVisible] = useState(false);
    const [actorDownloads, setActorDownloads] = useState<any[]>([]);
    const [loadingDownloads, setLoadingDownloads] = useState(false);
    const [editModalVisible, setEditModalVisible] = useState(false);
    const [editingSubscription, setEditingSubscription] = useState<any>(null);
    const [allDownloadsVisible, setAllDownloadsVisible] = useState(false);

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
        onSuccess: (res) => {
            message.success(res.data?.message || '订阅任务已在后台启动，请稍后查看结果');
        },
        onError: (err: any) => {
            // 即使出现504错误，也不提示错误，因为任务已在后台执行
            if (err.response && err.response.status === 504) {
                message.success('订阅任务已在后台启动，请稍后查看结果');
                console.log('演员订阅任务超时，但任务已在后台执行');
                return;
            }
            console.error('执行订阅任务失败:', err);
            message.error('执行订阅任务失败');
        }
    });

    // 更新订阅状态（暂停/恢复）
    const { run: updateSubscriptionStatus, loading: updatingStatus } = useRequest(subscribeApi.updateActorSubscriptionStatus, {
        manual: true,
        onSuccess: (_, [id, isPaused]) => {
            message.success(isPaused ? '已暂停订阅' : '已恢复订阅');
            refresh();
        },
        onError: (error) => {
            console.error('更新订阅状态失败:', error);
            message.error('更新订阅状态失败');
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
        let deleteDownloads = false;

        modal.confirm({
            title: '确认取消订阅',
            content: (
                <div>
                    <p>确定要取消订阅演员 <strong>{actor.actor_name}</strong> 吗？</p>
                    <div style={{ marginTop: '16px' }}>
                        <Checkbox
                            onChange={(e: any) => {
                                deleteDownloads = e.target.checked;
                            }}
                        >
                            同时删除已下载的资源（包括文件和下载任务）
                        </Checkbox>
                        <div style={{ fontSize: '12px', color: colors.textTertiary, marginTop: '4px' }}>
                            选中此项将从qBittorrent中删除该演员的所有下载任务和文件
                        </div>
                    </div>
                </div>
            ),
            okText: '确认取消订阅',
            cancelText: '取消',
            okType: 'danger',
            width: 450,
            onOk: () => deleteSubscription(actor.id, deleteDownloads)
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
        return <LoadingComponent tip="正在加载订阅列表..." minHeight="60vh" />;
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
        <div className="actor-subscribe-container">
            <Row gutter={[16, 16]}>
                <Col span={24}>
                    <Card className="actor-subscribe-header-card">
                        <Row align="middle" justify="space-between">
                            <Col>
                                <Title level={4} className="actor-subscribe-title">
                                    <UserOutlined className="actor-subscribe-icon" />
                                    演员订阅管理
                                </Title>
                                <Text className="actor-subscribe-subtitle">
                                    共 {subscriptions.length} 个订阅，系统将自动检查新作品并下载
                                </Text>
                            </Col>
                            <Col>
                                <Space>
                                    <Button
                                        type="primary"
                                        icon={<PlusOutlined />}
                                        onClick={() => navigate({ to: '/actor' })}
                                        className="actor-subscribe-primary-btn"
                                    >
                                        添加订阅
                                    </Button>
                                    <Button
                                        icon={<SyncOutlined />}
                                        loading={runningTask}
                                        onClick={() => runActorSubscribe()}
                                        className="actor-subscribe-action-btn"
                                    >
                                        立即检查更新
                                    </Button>
                                    <Button
                                        icon={<DatabaseOutlined />}
                                        onClick={() => setAllDownloadsVisible(true)}
                                        className="actor-subscribe-action-btn"
                                    >
                                        所有下载
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
                                    className="actor-subscribe-ribbon"
                                >
                                    <Card
                                        hoverable
                                        className="actor-subscribe-card"
                                        cover={
                                            <div className="actor-subscribe-cover-wrapper"
                                                onClick={() => viewActorDetail(item)}
                                            >
                                                {item.actor_thumb ? (
                                                    <img
                                                        alt={item.actor_name}
                                                        src={api.getVideoCover(item.actor_thumb)}
className="actor-subscribe-cover-img"
                                                    />
                                                ) : (
                                                    <Avatar
                                                        size={100}
                                                        icon={<UserOutlined />}
                                                        className="actor-subscribe-avatar"
                                                    />
                                                )}
                                                <div className="actor-subscribe-name-overlay"
                                                >
                                                    <Typography.Title level={5} className="actor-subscribe-name">
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
                                            <Tooltip title={item.is_paused ? "恢复订阅" : "暂停订阅"}>
                                                {item.is_paused ? (
                                                    <PlaySquareOutlined
                                                        key="resume"
                                                        style={{ color: colors.success }}
                                                        onClick={() => updateSubscriptionStatus(item.id, false)}
                                                    />
                                                ) : (
                                                    <PauseOutlined
                                                        key="pause"
                                                        style={{ color: colors.warning }}
                                                        onClick={() => updateSubscriptionStatus(item.id, true)}
                                                    />
                                                )}
                                            </Tooltip>,
                                            <Tooltip title="取消订阅">
                                                <DeleteOutlined
                                                    key="delete"
                                                    onClick={() => confirmDelete(item)}
                                                />
                                            </Tooltip>
                                        ]}
                                    >
                                        <div className="actor-subscribe-card-body">
                                            <Row gutter={[16, 8]}>
                                                <Col span={8}>
                                                    <Statistic
                                                        title="订阅日期"
                                                        value={item.from_date}
                                                        className="actor-subscribe-statistic"
                                                        prefix={<CalendarOutlined />}
                                                    />
                                                </Col>
                                                <Col span={8}>
                                                    <Statistic
                                                        title="已下载"
                                                        value={downloadCount}
                                                        suffix="部"
                                                        className="actor-subscribe-statistic"
                                                    />
                                                </Col>
                                                <Col span={8}>
                                                    <Statistic
                                                        title="订阅作品"
                                                        value={item.subscribed_works_count || 0}
                                                        suffix="部"
                                                        className="actor-subscribe-statistic"
                                                        prefix={<FileOutlined />}
                                                    />
                                                </Col>
                                            </Row>
                                            <div className="actor-subscribe-tags-container">
                                                <Space size={[0, 8]} wrap>
                                                    {item.is_paused && <Tag className="actor-subscribe-tag actor-subscribe-tag-paused">已暂停</Tag>}
                                                    {item.is_hd && <Tag className="actor-subscribe-tag actor-subscribe-tag-hd">高清</Tag>}
                                                    {item.is_zh && <Tag className="actor-subscribe-tag actor-subscribe-tag-zh">中文字幕</Tag>}
                                                    {item.is_uncensored && <Tag className="actor-subscribe-tag actor-subscribe-tag-uncensored">无码</Tag>}
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
                <Card className="actor-subscribe-empty-card">
                    <Empty
                        description={
                            <span className="actor-subscribe-empty-text">
                                暂无订阅的演员 <br />
                                <Button
                                    type="primary"
                                    icon={<PlusOutlined />}
                                    className="actor-subscribe-primary-btn actor-subscribe-empty-btn"
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
                    <div className="actor-subscribe-modal-title">
                        <PlayCircleOutlined className="actor-subscribe-modal-icon" />
                        {selectedActor ? `${selectedActor.actor_name} 的下载记录` : '下载记录'}
                    </div>
                }
open={downloadsVisible}
                onCancel={() => setDownloadsVisible(false)}
                footer={null}
                width={800}
                className="actor-subscribe-download-modal"
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
                                                    background: colors.bgSpotlight,
                                                    display: 'flex',
                                                    justifyContent: 'center',
                                                    alignItems: 'center',
                                                    borderRadius: '4px'
                                                }}>
                                                    <FileOutlined style={{ fontSize: 24, color: colors.textTertiary }} />
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

            {/* 所有下载记录模态框 */}
            <AllDownloadsModal
                open={allDownloadsVisible}
                onCancel={() => setAllDownloadsVisible(false)}
                onRefresh={refresh}
            />

            {/* 悬浮按钮 - 直接显示功能按钮，不使用设置按钮组 */}
            <FloatButton.Group style={{ right: 24, bottom: 24 }}>
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
                <FloatButton
                    icon={<DatabaseOutlined />}
                    tooltip="所有下载"
                    onClick={() => setAllDownloadsVisible(true)}
                />
            </FloatButton.Group>
        </div>
    );
}

export default ActorSubscribe; 