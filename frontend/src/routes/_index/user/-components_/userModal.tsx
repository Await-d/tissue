import React from "react";
import { Form, Input, Modal, Switch, Space, Divider } from "antd";
import { UserOutlined, LockOutlined, CrownOutlined } from "@ant-design/icons";
import { FormModalProps } from "../../../../utils/useFormModal.ts";

function UserModal(props: FormModalProps) {
    const { form, initValues, ...otherProps } = props;
    const id = initValues?.id;

    return (
        <Modal
            title={
                <Space>
                    <UserOutlined />
                    <span>{id ? '编辑用户' : '新建用户'}</span>
                </Space>
            }
            width={520}
            {...otherProps}
        >
            <Form layout="vertical" form={form}>
                {/* Basic Information */}
                <Form.Item
                    name="name"
                    label="姓名"
                    rules={[
                        { required: true, message: '请输入姓名' },
                        { min: 2, message: '姓名至少2个字符' },
                        { max: 50, message: '姓名最多50个字符' }
                    ]}
                >
                    <Input
                        prefix={<UserOutlined style={{ color: '#bfbfbf' }} />}
                        placeholder="请输入用户姓名"
                        size="large"
                    />
                </Form.Item>

                <Form.Item
                    name="username"
                    label="用户名"
                    rules={[
                        { required: true, message: '请输入用户名' },
                        { min: 3, message: '用户名至少3个字符' },
                        { max: 30, message: '用户名最多30个字符' },
                        {
                            pattern: /^[a-zA-Z0-9_]+$/,
                            message: '用户名只能包含字母、数字和下划线'
                        }
                    ]}
                >
                    <Input
                        prefix={<UserOutlined style={{ color: '#bfbfbf' }} />}
                        placeholder="请输入登录用户名"
                        size="large"
                        disabled={!!id}
                    />
                </Form.Item>

                <Divider orientation="left" plain>
                    密码设置
                </Divider>

                <Form.Item
                    name="password"
                    label={id ? '新密码（留空则不修改）' : '密码'}
                    rules={[
                        { required: !id, message: '请输入密码' },
                        { min: 6, message: '密码至少6个字符' }
                    ]}
                >
                    <Input.Password
                        prefix={<LockOutlined style={{ color: '#bfbfbf' }} />}
                        placeholder={id ? '留空则不修改密码' : '请输入密码'}
                        size="large"
                    />
                </Form.Item>

                <Form.Item
                    name="confirmPassword"
                    label="确认密码"
                    dependencies={['password']}
                    rules={[
                        { required: !id, message: '请确认密码' },
                        ({ getFieldValue }) => ({
                            validator(_, value) {
                                const password = getFieldValue('password');
                                if (!password && !value) {
                                    return Promise.resolve();
                                }
                                if (!value && password) {
                                    return Promise.reject(new Error('请确认密码'));
                                }
                                if (password && value && password !== value) {
                                    return Promise.reject(new Error('两次输入的密码不一致'));
                                }
                                return Promise.resolve();
                            }
                        })
                    ]}
                >
                    <Input.Password
                        prefix={<LockOutlined style={{ color: '#bfbfbf' }} />}
                        placeholder="请再次输入密码"
                        size="large"
                    />
                </Form.Item>

                <Divider orientation="left" plain>
                    权限设置
                </Divider>

                <Form.Item
                    name="is_admin"
                    label="管理员权限"
                    valuePropName="checked"
                    extra="管理员拥有系统的完全访问权限"
                >
                    <Switch
                        checkedChildren={<CrownOutlined />}
                        unCheckedChildren="普通"
                    />
                </Form.Item>
            </Form>
        </Modal>
    );
}

export default UserModal;
