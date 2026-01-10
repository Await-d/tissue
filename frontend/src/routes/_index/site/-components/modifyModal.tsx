import {Checkbox, Form, Input, Modal, Select} from "antd";
import {FormModalProps} from "../../../../utils/useFormModal.ts";
import React from "react";

function ModifyModal(props: FormModalProps) {

    const {form, initValues, ...otherProps} = props

    return (
        <>
            <style>{`
                .site-modify-modal .ant-modal-content {
                    background: #1a1a1d;
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.6);
                    backdrop-filter: blur(20px);
                }

                .site-modify-modal .ant-modal-header {
                    background: transparent;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                }

                .site-modify-modal .ant-modal-title {
                    color: #f0f0f2;
                    font-weight: 600;
                    font-size: 16px;
                }

                .site-modify-modal .ant-modal-close {
                    color: #a0a0a8;
                }

                .site-modify-modal .ant-modal-close:hover {
                    color: #f0f0f2;
                    background: rgba(255, 255, 255, 0.08);
                }

                .site-modify-modal .ant-form-item-label > label {
                    color: #f0f0f2;
                    font-weight: 500;
                }

                .site-modify-modal .ant-input,
                .site-modify-modal .ant-select-selector {
                    background: #141416 !important;
                    border: 1px solid rgba(255, 255, 255, 0.12) !important;
                    color: #f0f0f2 !important;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .site-modify-modal .ant-input:hover,
                .site-modify-modal .ant-select-selector:hover {
                    border-color: rgba(212, 168, 82, 0.4) !important;
                }

                .site-modify-modal .ant-input:focus,
                .site-modify-modal .ant-select-focused .ant-select-selector {
                    border-color: #d4a852 !important;
                    box-shadow: 0 0 0 2px rgba(212, 168, 82, 0.15) !important;
                }

                .site-modify-modal .ant-input::placeholder {
                    color: #6a6a72;
                }

                .site-modify-modal .ant-select-arrow {
                    color: #a0a0a8;
                }

                .site-modify-modal .ant-checkbox-wrapper {
                    color: #f0f0f2;
                }

                .site-modify-modal .ant-checkbox-inner {
                    background: #141416;
                    border-color: rgba(255, 255, 255, 0.12);
                }

                .site-modify-modal .ant-checkbox-checked .ant-checkbox-inner {
                    background: #d4a852;
                    border-color: #d4a852;
                }

                .site-modify-modal .ant-checkbox-wrapper:hover .ant-checkbox-inner {
                    border-color: rgba(212, 168, 82, 0.4);
                }

                .site-modify-modal .ant-modal-footer {
                    border-top: 1px solid rgba(255, 255, 255, 0.08);
                }

                .site-modify-modal .ant-btn-primary {
                    background: #d4a852;
                    border-color: #d4a852;
                    color: #0d0d0f;
                    font-weight: 600;
                    box-shadow: 0 2px 8px rgba(212, 168, 82, 0.3);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .site-modify-modal .ant-btn-primary:hover {
                    background: #e8c780 !important;
                    border-color: #e8c780 !important;
                    box-shadow: 0 4px 12px rgba(212, 168, 82, 0.4) !important;
                    transform: translateY(-1px);
                }

                .site-modify-modal .ant-btn-default {
                    background: transparent;
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    color: #a0a0a8;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .site-modify-modal .ant-btn-default:hover {
                    border-color: rgba(255, 255, 255, 0.2) !important;
                    color: #f0f0f2 !important;
                    background: rgba(255, 255, 255, 0.05) !important;
                }

                .site-modify-modal .ant-select-dropdown {
                    background: #1a1a1d;
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
                }

                .site-modify-modal .ant-select-item {
                    color: #a0a0a8;
                }

                .site-modify-modal .ant-select-item-option-selected {
                    background: rgba(212, 168, 82, 0.15);
                    color: #d4a852;
                    font-weight: 500;
                }

                .site-modify-modal .ant-select-item-option-active {
                    background: rgba(255, 255, 255, 0.05);
                }
            `}</style>
            <Modal 
                {...otherProps} 
                title={initValues.name}
                className="site-modify-modal"
            >
                <Form form={form} layout={'vertical'}>
                    <Form.Item noStyle name={'id'}>
                        <Input style={{display: 'none'}}/>
                    </Form.Item>
                    <Form.Item name={'alternate_host'} label={'替代域名'}>
                        <Input placeholder={'当域名失效或替代域名时填写'}/>
                    </Form.Item>
                    <Form.Item name={'priority'} label={'优先级'} initialValue={0}>
                        <Select>{Array(101).fill(0).map((_, index) => (
                            <Select.Option key={index} value={index}>{index}</Select.Option>))}</Select>
                    </Form.Item>
                    <Form.Item name={'status'} label={'状态'} valuePropName={'checked'}>
                        <Checkbox>启用</Checkbox>
                    </Form.Item>
                </Form>
            </Modal>
        </>
    )
}

export default ModifyModal
