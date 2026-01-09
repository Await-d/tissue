import React from 'react';
import { Modal, Form, Input, Checkbox, DatePicker, Button, Row, Col, Avatar, Space, Tooltip, App, InputNumber } from 'antd';
import { UserOutlined, InfoCircleOutlined, StarOutlined, MessageOutlined } from '@ant-design/icons';
import * as api from '../../../../apis/video';
import * as subscribeApi from '../../../../apis/subscribe';
import { useRequest } from 'ahooks';
import dayjs from 'dayjs';

interface ActorSubscribeModalProps {
    open: boolean;
    actor: any;
    onCancel: () => void;
    onOk: () => void;
    confirmLoading?: boolean;
}

const ActorSubscribeModal: React.FC<ActorSubscribeModalProps> = ({
    open,
    actor,
    onCancel,
    onOk,
    confirmLoading = false
}) => {
    const [form] = Form.useForm();
    const { message } = App.useApp();

    // 当演员信息变化时，更新表单数据
    React.useEffect(() => {
        if (actor && open) {
            form.setFieldsValue({
                actor_name: actor.name,
                actor_url: actor.url,
                actor_thumb: actor.thumb,
                from_date: dayjs(),
                is_hd: true,
                is_zh: false,
                is_uncensored: false,
                min_rating: 0.0,
                min_comments: 0
            });
        }
    }, [actor, open, form]);

    const { run: subscribe, loading } = useRequest(subscribeApi.subscribeActor, {
        manual: true,
        onSuccess: (response: { data?: { is_update?: boolean } }) => {
            // 根据返回结果显示不同消息
            if (response && response.data && response.data.is_update) {
                message.success(`已更新演员 ${actor.name} 的订阅设置`);
            } else {
                message.success(`已成功订阅演员 ${actor.name}`);
            }
            onOk();
        },
        onError: (error) => {
            console.error('订阅失败:', error);
            message.error('订阅失败，请稍后重试');
        }
    });

    const handleSubmit = () => {
        form.validateFields().then(values => {
            subscribe({
                ...values,
                from_date: values.from_date.format('YYYY-MM-DD')
            });
        });
    };

    return (
        <Modal
            title="订阅演员"
            open={open}
            onCancel={onCancel}
            confirmLoading={confirmLoading || loading}
            footer={[
                <Button key="cancel" onClick={onCancel}>
                    取消
                </Button>,
                <Button key="submit" type="primary" loading={confirmLoading || loading} onClick={handleSubmit}>
                    确定
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
                    from_date: dayjs()
                }}
            >
                {actor && (
                    <div style={{ textAlign: 'center', marginBottom: '24px' }}>
                        <Avatar
                            size={64}
                            icon={<UserOutlined />}
                            src={actor.thumb ? api.getVideoCover(actor.thumb) : undefined}
                        />
                        <h2 style={{ marginTop: 8 }}>{actor.name}</h2>
                    </div>
                )}

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
                            <Checkbox />
                        </Form.Item>
                    </Col>
                    <Col span={8}>
                        <Form.Item
                            label="中文字幕"
                            name="is_zh"
                            valuePropName="checked"
                        >
                            <Checkbox />
                        </Form.Item>
                    </Col>
                    <Col span={8}>
                        <Form.Item
                            label="无码"
                            name="is_uncensored"
                            valuePropName="checked"
                        >
                            <Checkbox />
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

                <div style={{ marginTop: '16px', color: '#888', fontSize: '14px' }}>
                    <div style={{ marginBottom: '8px' }}>订阅设置说明：</div>
                    <div>• 系统将自动监控该演员的新作品，并根据设置的条件进行下载</div>
                    <div>• 评分和评论数筛选可以帮助你只订阅高质量作品</div>
                    <div>• 设置为 0 表示不启用该筛选条件</div>
                </div>
            </Form>
        </Modal>
    );
};

export default ActorSubscribeModal; 