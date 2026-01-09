import React, { useEffect } from 'react';
import { Modal, Form, DatePicker, Button, Row, Col, Avatar, Space, Tooltip, Checkbox, Input, Switch, InputNumber } from 'antd';
import { UserOutlined, InfoCircleOutlined, StarOutlined, MessageOutlined } from '@ant-design/icons';
import * as api from '../../../../apis/video';
import * as subscribeApi from '../../../../apis/subscribe';
import { useRequest } from 'ahooks';
import dayjs from 'dayjs';
import { message } from 'antd';

interface EditSubscribeModalProps {
    open: boolean;
    subscription: any;
    onCancel: () => void;
    onOk: () => void;
    confirmLoading?: boolean;
}

const EditSubscribeModal: React.FC<EditSubscribeModalProps> = ({
    open,
    subscription,
    onCancel,
    onOk,
    confirmLoading = false
}) => {
    const [form] = Form.useForm();

    // 当订阅信息变化时，更新表单数据
    useEffect(() => {
        if (subscription && open) {
            form.setFieldsValue({
                ...subscription,
                from_date: subscription.from_date ? dayjs(subscription.from_date) : null,
                // 确保数字类型字段被正确转换
                min_rating: subscription.min_rating !== null && subscription.min_rating !== undefined
                    ? Number(subscription.min_rating)
                    : 0.0,
                min_comments: subscription.min_comments !== null && subscription.min_comments !== undefined
                    ? Number(subscription.min_comments)
                    : 0,
            });
        }
    }, [subscription, open, form]);

    const { run: updateSubscription, loading } = useRequest(subscribeApi.updateActorSubscription, {
        manual: true,
        onSuccess: () => {
            onOk();
        }
    });

    const handleSubmit = async () => {
        try {
            const values = await form.validateFields();
            const formData = {
                ...values,
                id: subscription.id,
                from_date: values.from_date ? values.from_date.format('YYYY-MM-DD') : null,
            };

            await updateSubscription(formData);
        } catch (error) {
            message.error('保存失败');
        }
    };

    return (
        <Modal
            title="编辑订阅设置"
            open={open}
            onCancel={onCancel}
            confirmLoading={confirmLoading || loading}
            footer={[
                <Button key="cancel" onClick={onCancel}>
                    取消
                </Button>,
                <Button key="submit" type="primary" loading={confirmLoading || loading} onClick={handleSubmit}>
                    保存
                </Button>
            ]}
        >
            <Form
                form={form}
                layout="vertical"
                initialValues={{
                    is_hd: true,
                    is_zh: false,
                    is_uncensored: false,
                    min_rating: 0.0,
                    min_comments: 0,
                    from_date: dayjs()
                }}
            >
                {subscription && (
                    <div style={{ textAlign: 'center', marginBottom: '24px' }}>
                        <Avatar
                            size={64}
                            icon={<UserOutlined />}
                            src={subscription.actor_thumb ? api.getVideoCover(subscription.actor_thumb) : undefined}
                        />
                        <h2 style={{ marginTop: 8 }}>{subscription.actor_name}</h2>
                    </div>
                )}

                <Form.Item name="id" hidden>
                    <Input />
                </Form.Item>

                <Form.Item name="actor_name" hidden>
                    <Input />
                </Form.Item>

                <Form.Item name="actor_url" hidden>
                    <Input />
                </Form.Item>

                <Form.Item name="actor_thumb" hidden>
                    <Input />
                </Form.Item>

                <Form.Item
                    label={
                        <Space>
                            <span>订阅起始日期</span>
                            <Tooltip title="系统将从该日期之后的新作品中进行订阅">
                                <InfoCircleOutlined />
                            </Tooltip>
                        </Space>
                    }
                    name="from_date"
                    rules={[{ required: true, message: '请选择订阅起始日期' }]}
                >
                    <DatePicker
                        style={{ width: '100%' }}
                        format="YYYY-MM-DD"
                    />
                </Form.Item>

                <Row gutter={16}>
                    <Col span={8}>
                        <Form.Item
                            label="高清"
                            name="is_hd"
                            valuePropName="checked"
                        >
                            <Switch />
                        </Form.Item>
                    </Col>
                    <Col span={8}>
                        <Form.Item
                            label="中文字幕"
                            name="is_zh"
                            valuePropName="checked"
                        >
                            <Switch />
                        </Form.Item>
                    </Col>
                    <Col span={8}>
                        <Form.Item
                            label="无码"
                            name="is_uncensored"
                            valuePropName="checked"
                        >
                            <Switch />
                        </Form.Item>
                    </Col>
                </Row>

                <Row gutter={16}>
                    <Col span={12}>
                        <Form.Item
                            label={
                                <Space>
                                    <StarOutlined />
                                    <span>最低评分</span>
                                    <Tooltip title="只订阅评分不低于此值的作品，0表示不限制">
                                        <InfoCircleOutlined />
                                    </Tooltip>
                                </Space>
                            }
                            name="min_rating"
                        >
                            <InputNumber
                                min={0}
                                max={10}
                                step={0.1}
                                precision={1}
                                placeholder="0.0"
                                style={{ width: '100%' }}
                            />
                        </Form.Item>
                    </Col>
                    <Col span={12}>
                        <Form.Item
                            label={
                                <Space>
                                    <MessageOutlined />
                                    <span>最低评论数</span>
                                    <Tooltip title="只订阅评论数不少于此值的作品，0表示不限制">
                                        <InfoCircleOutlined />
                                    </Tooltip>
                                </Space>
                            }
                            name="min_comments"
                        >
                            <InputNumber
                                min={0}
                                placeholder="0"
                                style={{ width: '100%' }}
                            />
                        </Form.Item>
                    </Col>
                </Row>

                <Form.Item
                    label="暂停订阅"
                    name="is_paused"
                    valuePropName="checked"
                    extra="暂停后将不会自动检查和下载新作品"
                >
                    <Switch />
                </Form.Item>

                <div style={{ marginTop: '16px', color: '#888', fontSize: '14px' }}>
                    <div style={{ marginBottom: '8px' }}>筛选条件说明：</div>
                    <div>• 评分和评论数筛选可以帮助你只订阅高质量作品</div>
                    <div>• 设置为 0 表示不启用该筛选条件</div>
                    <div>• 更改设置后，系统将根据新的条件进行下载</div>
                </div>
            </Form>
        </Modal>
    );
};

export default EditSubscribeModal; 