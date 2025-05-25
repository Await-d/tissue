import React, { useState } from 'react';
import { Card, Col, Row, List, Avatar, Tag, Space, Button, message, Tooltip, Empty, Spin, Modal, FloatButton } from 'antd';
import { UserOutlined, DeleteOutlined, EditOutlined, EyeOutlined } from '@ant-design/icons';
import { createFileRoute, useNavigate } from '@tanstack/react-router';
import * as api from '../../../apis/video';
import * as subscribeApi from '../../../apis/subscribe';
import { useRequest } from 'ahooks';
import { createPortal } from 'react-dom';

export const Route = createFileRoute('/_index/actor-subscribe/')({
    component: ActorSubscribe
});

function ActorSubscribe() {
    const navigate = useNavigate();
    const [selectedActor, setSelectedActor] = useState<any>(null);
    const [downloadsVisible, setDownloadsVisible] = useState(false);
    const [actorDownloads, setActorDownloads] = useState<any[]>([]);
    const [loadingDownloads, setLoadingDownloads] = useState(false);

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

    if (loading) {
        return (
            <Card>
                <div style={{ textAlign: 'center', padding: '30px 0' }}>
                    <Spin />
                    <div style={{ marginTop: 8 }}>加载中...</div>
                </div>
            </Card>
        );
    }

    return (
        <div>
            <Row gutter={[16, 16]}>
                <Col span={24}>
                    <Card title="演员订阅列表">
                        {subscriptions.length > 0 ? (
                            <List
                                grid={{ gutter: 16, xs: 1, sm: 2, md: 3, lg: 4, xl: 4, xxl: 6 }}
                                dataSource={subscriptions}
                                renderItem={(item: any) => (
                                    <List.Item>
                                        <Card
                                            hoverable
                                            actions={[
                                                <Tooltip title="查看演员详情">
                                                    <EyeOutlined key="view" onClick={() => viewActorDetail(item)} />
                                                </Tooltip>,
                                                <Tooltip title="查看下载记录">
                                                    <Button
                                                        type="link"
                                                        icon={<EyeOutlined />}
                                                        onClick={() => handleViewDownloads(item)}
                                                    />
                                                </Tooltip>,
                                                <Tooltip title="取消订阅">
                                                    <DeleteOutlined
                                                        key="delete"
                                                        onClick={() => confirmDelete(item)}
                                                    />
                                                </Tooltip>
                                            ]}
                                        >
                                            <Card.Meta
                                                avatar={
                                                    <Avatar
                                                        size={64}
                                                        icon={<UserOutlined />}
                                                        src={item.actor_thumb ? api.getVideoCover(item.actor_thumb) : undefined}
                                                    />
                                                }
                                                title={item.actor_name}
                                                description={
                                                    <Space direction="vertical" size="small">
                                                        <div>订阅日期: {item.from_date}</div>
                                                        <Space size={[0, 8]} wrap>
                                                            {item.is_hd && <Tag color="blue">高清</Tag>}
                                                            {item.is_zh && <Tag color="green">中文字幕</Tag>}
                                                            {item.is_uncensored && <Tag color="red">无码</Tag>}
                                                        </Space>
                                                    </Space>
                                                }
                                            />
                                        </Card>
                                    </List.Item>
                                )}
                            />
                        ) : (
                            <Empty description="暂无订阅的演员" />
                        )}
                    </Card>
                </Col>
            </Row>

            {/* 下载记录模态框 */}
            <Modal
                title={selectedActor ? `${selectedActor.actor_name} 的下载记录` : '下载记录'}
                open={downloadsVisible}
                onCancel={() => setDownloadsVisible(false)}
                footer={null}
                width={800}
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
                                <Card style={{ width: '100%' }}>
                                    <Card.Meta
                                        title={item.title || item.num}
                                        description={
                                            <Space direction="vertical" size="small">
                                                <div>番号: {item.num}</div>
                                                <div>下载时间: {item.download_time}</div>
                                                <div>
                                                    <Space size={[0, 8]} wrap>
                                                        {item.is_hd && <Tag color="blue">高清</Tag>}
                                                        {item.is_zh && <Tag color="green">中文字幕</Tag>}
                                                        {item.is_uncensored && <Tag color="red">无码</Tag>}
                                                    </Space>
                                                </div>
                                            </Space>
                                        }
                                    />
                                </Card>
                            </List.Item>
                        )}
                    />
                ) : (
                    <Empty description="暂无下载记录" />
                )}
            </Modal>
        </div>
    );
}

export default ActorSubscribe; 