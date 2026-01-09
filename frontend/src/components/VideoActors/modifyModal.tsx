import { Button, Form, Input, Modal, ModalProps, Avatar, Space, message } from "antd";
import { UserOutlined } from "@ant-design/icons";
import React, { useEffect, useState } from "react";
import * as api from "../../apis/video";

interface Props extends ModalProps {
    data?: any,
    onOk?: (data: any) => void
    onDelete?: (data: any) => void
    onCancel?: () => void
}

function ModifyModal(props: Props) {
    const { data, onOk, onDelete, onCancel, ...otherProps } = props;
    const [form] = Form.useForm();
    const [previewThumb, setPreviewThumb] = useState<string | undefined>(data?.thumb);

    useEffect(() => {
        if (props.open) {
            form.setFieldsValue(data);
            setPreviewThumb(data?.thumb);
        } else {
            form.resetFields();
            setPreviewThumb(undefined);
        }
    }, [props.open, data]);

    function onSave(value: any) {
        onOk?.(value);
    }

    const handleThumbChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setPreviewThumb(value);
    };

    const handlePreviewError = () => {
        message.error("头像链接无效，请检查URL是否正确");
    };

    return (
        <Modal
            title={data ? '修改演员信息' : '添加新演员'}
            {...otherProps}
            width={420}
            onCancel={onCancel}
            footer={[
                data && (
                    <Button key="delete" danger onClick={onDelete}>
                        删除
                    </Button>
                ),
                <Button key="cancel" onClick={onCancel}>
                    取消
                </Button>,
                <Button key="submit" type="primary" onClick={() => form.submit()}>
                    确定
                </Button>
            ]}
        >
            <Form
                form={form}
                layout="vertical"
                onFinish={onSave}
                initialValues={data}
            >
                <Space
                    direction="vertical"
                    style={{
                        width: '100%',
                        display: 'flex',
                        alignItems: 'center',
                        marginBottom: 24
                    }}
                >
                    <Avatar
                        size={80}
                        icon={<UserOutlined />}
                        src={previewThumb && api.getVideoCover(previewThumb)}
                        onError={() => {
                            handlePreviewError();
                            return true;
                        }}
                        style={{
                            border: '2px solid #f0f0f0',
                            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                        }}
                    />
                    <div style={{ fontSize: 12, color: '#888', marginTop: 8 }}>
                        {previewThumb ? '预览头像' : '暂无头像'}
                    </div>
                </Space>

                <Form.Item
                    name="name"
                    label="演员姓名"
                    rules={[{ required: true, message: '请输入演员姓名' }]}
                >
                    <Input placeholder="请输入演员姓名" />
                </Form.Item>

                <Form.Item
                    name="thumb"
                    label="头像链接"
                    extra="输入完整的图片URL或相对路径"
                >
                    <Input
                        placeholder="请输入头像链接"
                        onChange={handleThumbChange}
                    />
                </Form.Item>
            </Form>
        </Modal>
    );
}

export default ModifyModal;
