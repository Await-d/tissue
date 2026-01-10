import {Checkbox, Form, Input, Modal, Select} from "antd";
import {FormModalProps} from "../../../../utils/useFormModal.ts";
import React from "react";
import { useThemeColors } from '../../../../hooks/useThemeColors';

function ModifyModal(props: FormModalProps) {

    const {form, initValues, ...otherProps} = props
    const colors = useThemeColors()

    return (
        <>
            <style>{`
                .site-modify-modal .ant-modal-content {
                    background: ${colors.modalBg};
                    border: 1px solid ${colors.borderPrimary};
                    box-shadow: 0 12px 48px ${colors.rgba('black', 0.6)};
                    backdrop-filter: blur(20px);
                }

                .site-modify-modal .ant-modal-mask {
                    background: ${colors.modalOverlay};
                }

                .site-modify-modal .ant-modal-header {
                    background: transparent;
                    border-bottom: 1px solid ${colors.borderPrimary};
                }

                .site-modify-modal .ant-modal-title {
                    color: ${colors.textPrimary};
                    font-weight: 600;
                    font-size: 16px;
                }

                .site-modify-modal .ant-modal-close {
                    color: ${colors.textSecondary};
                }

                .site-modify-modal .ant-modal-close:hover {
                    color: ${colors.textPrimary};
                    background: ${colors.borderPrimary};
                }

                .site-modify-modal .ant-form-item-label > label {
                    color: ${colors.textPrimary};
                    font-weight: 500;
                }

                .site-modify-modal .ant-input,
                .site-modify-modal .ant-select-selector {
                    background: ${colors.bgElevated} !important;
                    border: 1px solid ${colors.borderPrimary} !important;
                    color: ${colors.textPrimary} !important;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .site-modify-modal .ant-input:hover,
                .site-modify-modal .ant-select-selector:hover {
                    border-color: ${colors.rgba('gold', 0.4)} !important;
                }

                .site-modify-modal .ant-input:focus,
                .site-modify-modal .ant-select-focused .ant-select-selector {
                    border-color: ${colors.goldPrimary} !important;
                    box-shadow: 0 0 0 2px ${colors.goldGlow} !important;
                }

                .site-modify-modal .ant-input::placeholder {
                    color: ${colors.textTertiary};
                }

                .site-modify-modal .ant-select-arrow {
                    color: ${colors.textSecondary};
                }

                .site-modify-modal .ant-checkbox-wrapper {
                    color: ${colors.textPrimary};
                }

                .site-modify-modal .ant-checkbox-inner {
                    background: ${colors.bgElevated};
                    border-color: ${colors.borderPrimary};
                }

                .site-modify-modal .ant-checkbox-checked .ant-checkbox-inner {
                    background: ${colors.goldPrimary};
                    border-color: ${colors.goldPrimary};
                }

                .site-modify-modal .ant-checkbox-wrapper:hover .ant-checkbox-inner {
                    border-color: ${colors.rgba('gold', 0.4)};
                }

                .site-modify-modal .ant-modal-footer {
                    border-top: 1px solid ${colors.borderPrimary};
                }

                .site-modify-modal .ant-btn-primary {
                    background: ${colors.goldPrimary};
                    border-color: ${colors.goldPrimary};
                    color: ${colors.bgBase};
                    font-weight: 600;
                    box-shadow: 0 2px 8px ${colors.rgba('gold', 0.3)};
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .site-modify-modal .ant-btn-primary:hover {
                    background: ${colors.goldLight} !important;
                    border-color: ${colors.goldLight} !important;
                    box-shadow: 0 4px 12px ${colors.rgba('gold', 0.4)} !important;
                    transform: translateY(-1px);
                }

                .site-modify-modal .ant-btn-default {
                    background: transparent;
                    border: 1px solid ${colors.borderPrimary};
                    color: ${colors.textSecondary};
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .site-modify-modal .ant-btn-default:hover {
                    border-color: ${colors.rgba('white', 0.2)} !important;
                    color: ${colors.textPrimary} !important;
                    background: ${colors.rgba('white', 0.05)} !important;
                }

                .site-modify-modal .ant-select-dropdown {
                    background: ${colors.bgContainer};
                    border: 1px solid ${colors.borderPrimary};
                    box-shadow: 0 8px 24px ${colors.rgba('black', 0.5)};
                }

                .site-modify-modal .ant-select-item {
                    color: ${colors.textSecondary};
                }

                .site-modify-modal .ant-select-item-option-selected {
                    background: ${colors.goldGlow};
                    color: ${colors.goldPrimary};
                    font-weight: 500;
                }

                .site-modify-modal .ant-select-item-option-active {
                    background: ${colors.rgba('white', 0.05)};
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
