import React, { useEffect } from 'react';
import { Modal, Form, DatePicker, Button, Row, Col, Avatar, Space, Tooltip, Checkbox, Input, Switch, InputNumber, App } from 'antd';
import { UserOutlined, InfoCircleOutlined, StarOutlined, MessageOutlined } from '@ant-design/icons';
import * as api from '../../../../apis/video';
import * as subscribeApi from '../../../../apis/subscribe';
import { useRequest } from 'ahooks';
import dayjs from 'dayjs';
import './EditSubscribeModal.css';

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
    const { message } = App.useApp();
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
                id: subscription.id,
                actor_name: subscription.actor_name,
                actor_url: subscription.actor_url,
                actor_thumb: subscription.actor_thumb,
                from_date: values.from_date ? values.from_date.format('YYYY-MM-DD') : null,
                is_hd: values.is_hd ?? false,
                is_zh: values.is_zh ?? false,
                is_uncensored: values.is_uncensored ?? false,
                is_paused: values.is_paused ?? false,
                min_rating: values.min_rating ?? 0.0,
                min_comments: values.min_comments ?? 0,
            };

            await updateSubscription(formData);
        } catch (error) {
            console.error('保存失败:', error);
            message.error('保存失败');
        }
    };

    return (
        <Modal
            title="编辑订阅设置"
            open={open}
            forceRender
            onCancel={onCancel}
            confirmLoading={confirmLoading || loading}
            className="edit-subscribe-modal"
            footer={[
                <Button key="cancel" onClick={onCancel} className="edit-subscribe-modal-cancel-btn">
                    取消
                </Button>,
                <Button key="submit" type="primary" loading={confirmLoading || loading} onClick={handleSubmit} className="edit-subscribe-modal-submit-btn">
                    保存
                </Button>
            ]}
        >
            <Form
                form={form}
                layout="vertical"
                className="edit-subscribe-modal-form"
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
                    <div className="edit-subscribe-modal-actor-info">
                        <Avatar
                            size={64}
                            icon={<UserOutlined />}
                            src={subscription.actor_thumb ? api.getVideoCover(subscription.actor_thumb) : undefined}
                            className="edit-subscribe-modal-avatar"
                        />
                        <h2 className="edit-subscribe-modal-actor-name">{subscription.actor_name}</h2>
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
                                <InfoCircleOutlined className="edit-subscribe-modal-info-icon" />
                            </Tooltip>
                        </Space>
                    }
                    name="from_date"
                    rules={[{ required: true, message: '请选择订阅起始日期' }]}
                >
                    <DatePicker
                        style={{ width: '100%' }}
                        format="YYYY-MM-DD"
                        className="edit-subscribe-modal-datepicker"
                    />
                </Form.Item>

                <Row gutter={16}>
                    <Col span={8}>
                        <Form.Item
                            label="高清"
                            name="is_hd"
                            valuePropName="checked"
                        >
                            <Switch className="edit-subscribe-modal-switch" />
                        </Form.Item>
                    </Col>
                    <Col span={8}>
                        <Form.Item
                            label="中文字幕"
                            name="is_zh"
                            valuePropName="checked"
                        >
                            <Switch className="edit-subscribe-modal-switch" />
                        </Form.Item>
                    </Col>
                    <Col span={8}>
                        <Form.Item
                            label="无码"
                            name="is_uncensored"
                            valuePropName="checked"
                        >
                            <Switch className="edit-subscribe-modal-switch" />
                        </Form.Item>
                    </Col>
                </Row>

                <Row gutter={16}>
                    <Col span={12}>
                        <Form.Item
                            label={
                                <Space>
                                    <StarOutlined className="edit-subscribe-modal-label-icon" />
                                    <span>最低评分</span>
                                    <Tooltip title="只订阅评分不低于此值的作品，0表示不限制">
                                        <InfoCircleOutlined className="edit-subscribe-modal-info-icon" />
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
                                className="edit-subscribe-modal-input-number"
                            />
                        </Form.Item>
                    </Col>
                    <Col span={12}>
                        <Form.Item
                            label={
                                <Space>
                                    <MessageOutlined className="edit-subscribe-modal-label-icon" />
                                    <span>最低评论数</span>
                                    <Tooltip title="只订阅评论数不少于此值的作品，0表示不限制">
                                        <InfoCircleOutlined className="edit-subscribe-modal-info-icon" />
                                    </Tooltip>
                                </Space>
                            }
                            name="min_comments"
                        >
                            <InputNumber
                                min={0}
                                placeholder="0"
                                style={{ width: '100%' }}
                                className="edit-subscribe-modal-input-number"
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
                    <Switch className="edit-subscribe-modal-switch" />
                </Form.Item>

                <div className="edit-subscribe-modal-help-text">
                    <div className="edit-subscribe-modal-help-title">筛选条件说明：</div>
                    <div>• 评分和评论数筛选可以帮助你只订阅高质量作品</div>
                    <div>• 设置为 0 表示不启用该筛选条件</div>
                    <div>• 更改设置后，系统将根据新的条件进行下载</div>
                </div>
            </Form>
        </Modal>
    );
};

export default EditSubscribeModal; 