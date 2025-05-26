import React, { useEffect } from 'react';
import { Modal, Form, DatePicker, Button, Row, Col, Avatar, Space, Tooltip, Checkbox, Input } from 'antd';
import { UserOutlined, InfoCircleOutlined } from '@ant-design/icons';
import * as api from '../../../../apis/video';
import * as subscribeApi from '../../../../apis/subscribe';
import { useRequest } from 'ahooks';
import dayjs from 'dayjs';

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
                id: subscription.id,
                actor_name: subscription.actor_name,
                actor_url: subscription.actor_url,
                actor_thumb: subscription.actor_thumb,
                from_date: subscription.from_date ? dayjs(subscription.from_date) : dayjs(),
                is_hd: subscription.is_hd,
                is_zh: subscription.is_zh,
                is_uncensored: subscription.is_uncensored
            });
        }
    }, [subscription, open, form]);

    const { run: updateSubscription, loading } = useRequest(subscribeApi.updateActorSubscription, {
        manual: true,
        onSuccess: () => {
            onOk();
        }
    });

    const handleSubmit = () => {
        form.validateFields().then(values => {
            updateSubscription({
                ...values,
                from_date: values.from_date.format('YYYY-MM-DD')
            });
        });
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

                <div style={{ marginTop: '16px', color: '#888', fontSize: '14px' }}>
                    更改订阅设置后，系统将根据新的条件进行下载。
                </div>
            </Form>
        </Modal>
    );
};

export default EditSubscribeModal; 