import React from "react";
import {Form, Input, Modal} from "antd";
import {FormModalProps} from "../../../../utils/useFormModal.ts";

function UserModal(props: FormModalProps) {

    const {form, initValues, ...otherProps} = props

    const id = initValues?.id

    return (
        <>
            <style>{`
                .user-modal .ant-modal-content {
                    background: #1a1a1d;
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.6);
                    backdrop-filter: blur(20px);
                }

                .user-modal .ant-modal-header {
                    background: transparent;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                }

                .user-modal .ant-modal-title {
                    color: #f0f0f2;
                    font-weight: 600;
                    font-size: 16px;
                }

                .user-modal .ant-modal-close {
                    color: #a0a0a8;
                }

                .user-modal .ant-modal-close:hover {
                    color: #f0f0f2;
                    background: rgba(255, 255, 255, 0.08);
                }

                .user-modal .ant-form-item-label > label {
                    color: #f0f0f2;
                    font-weight: 500;
                }

                .user-modal .ant-input,
                .user-modal .ant-input-password {
                    background: #141416 !important;
                    border: 1px solid rgba(255, 255, 255, 0.12) !important;
                    color: #f0f0f2 !important;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .user-modal .ant-input:hover,
                .user-modal .ant-input-password:hover {
                    border-color: rgba(212, 168, 82, 0.4) !important;
                }

                .user-modal .ant-input:focus,
                .user-modal .ant-input-password:focus,
                .user-modal .ant-input-focused {
                    border-color: #d4a852 !important;
                    box-shadow: 0 0 0 2px rgba(212, 168, 82, 0.15) !important;
                }

                .user-modal .ant-input::placeholder {
                    color: #6a6a72;
                }

                .user-modal .ant-input-password .ant-input {
                    background: transparent !important;
                    border: none !important;
                }

                .user-modal .ant-input-suffix {
                    color: #a0a0a8;
                }

                .user-modal .ant-modal-footer {
                    border-top: 1px solid rgba(255, 255, 255, 0.08);
                }

                .user-modal .ant-btn-primary {
                    background: #d4a852;
                    border-color: #d4a852;
                    color: #0d0d0f;
                    font-weight: 600;
                    box-shadow: 0 2px 8px rgba(212, 168, 82, 0.3);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .user-modal .ant-btn-primary:hover {
                    background: #e8c780 !important;
                    border-color: #e8c780 !important;
                    box-shadow: 0 4px 12px rgba(212, 168, 82, 0.4) !important;
                    transform: translateY(-1px);
                }

                .user-modal .ant-btn-default {
                    background: transparent;
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    color: #a0a0a8;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .user-modal .ant-btn-default:hover {
                    border-color: rgba(255, 255, 255, 0.2) !important;
                    color: #f0f0f2 !important;
                    background: rgba(255, 255, 255, 0.05) !important;
                }

                .user-modal .ant-form-item-explain-error {
                    color: #ff4d4f;
                }
            `}</style>
            <Modal 
                title={id ? '编辑用户' : '新建用户'} 
                {...otherProps}
                className="user-modal"
            >
                <Form layout={'vertical'} form={form}>
                    <Form.Item name={'name'} label={'名称'} rules={[{required: true, message: '请输入名称'}]}>
                        <Input/>
                    </Form.Item>
                    <Form.Item name={'username'} label={'用户名'} rules={[{required: true, message: '请输入用户名'}]}>
                        <Input/>
                    </Form.Item>
                    <Form.Item name={'password'} label={'新密码'} rules={[{required: !id}]}>
                        <Input.Password/>
                    </Form.Item>
                    <Form.Item name={'confirmPassword'} label={'确认新密码'} rules={[{required: !id}]}>
                        <Input.Password/>
                    </Form.Item>
                </Form>
            </Modal>
        </>
    )
}

export default UserModal
