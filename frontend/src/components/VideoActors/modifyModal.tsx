import { Button, Form, Input, Modal, ModalProps, Avatar, Space, message } from "antd";
import { UserOutlined } from "@ant-design/icons";
import React, { useEffect, useState } from "react";
import * as api from "../../apis/video";
import { useThemeColors } from '../../hooks/useThemeColors';

interface Props extends ModalProps {
    data?: any,
    onOk?: (data: any) => void
    onDelete?: (data: any) => void
    onCancel?: () => void
}

function ModifyModal(props: Props) {
    const { data, onOk, onDelete, onCancel, ...otherProps } = props;
    const colors = useThemeColors();
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

    // 样式定义 - 暗黑电影美学
    const styles = {
        modal: {
            '.ant-modal-mask': {
                background: colors.modalOverlay,
            },
            '.ant-modal-content': {
                background: colors.modalBg,
                border: `1px solid ${colors.rgba('white', 0.08)}`,
                boxShadow: `0 24px 48px ${colors.rgba('black', 0.8)}, 0 0 0 1px ${colors.rgba('gold', 0.1)}`,
                backdropFilter: 'blur(20px)',
                borderRadius: '16px',
            },
            '.ant-modal-header': {
                background: 'transparent',
                borderBottom: `1px solid ${colors.rgba('white', 0.08)}`,
                padding: '20px 24px',
            },
            '.ant-modal-title': {
                color: colors.text,
                fontSize: '18px',
                fontWeight: '600',
                letterSpacing: '0.5px',
            },
            '.ant-modal-close': {
                color: colors.secondaryText,
                transition: 'all 0.3s ease',
            },
            '.ant-modal-close:hover': {
                color: colors.gold,
            },
            '.ant-modal-body': {
                padding: '24px',
            },
            '.ant-modal-footer': {
                borderTop: `1px solid ${colors.rgba('white', 0.08)}`,
                padding: '16px 24px',
                background: colors.rgba('black', 0.5),
            },
        } as React.CSSProperties,

        avatarContainer: {
            width: '100%',
            display: 'flex',
            flexDirection: 'column' as const,
            alignItems: 'center',
            marginBottom: 32,
            padding: '24px 0',
            background: `linear-gradient(135deg, ${colors.rgba('gold', 0.05)} 0%, transparent 100%)`,
            borderRadius: '12px',
            border: `1px solid ${colors.rgba('white', 0.04)}`,
            transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        },

        avatarWrapper: {
            position: 'relative' as const,
            transition: 'transform 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        },

        avatar: {
            border: `3px solid ${colors.rgba('gold', 0.3)}`,
            boxShadow: `
                0 0 0 4px ${colors.rgba('gold', 0.1)},
                0 0 24px ${colors.rgba('gold', 0.3)},
                0 8px 32px ${colors.rgba('black', 0.6)}
            `,
            transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
            background: `linear-gradient(135deg, ${colors.bgDark} 0%, ${colors.bgDarker} 100%)`,
        },

        avatarIcon: {
            color: colors.gold,
        },

        avatarLabel: {
            fontSize: 13,
            color: colors.tertiaryText,
            marginTop: 12,
            letterSpacing: '0.3px',
            transition: 'color 0.3s ease',
        },

        input: {
            background: colors.rgba('black', 0.6),
            border: `1px solid ${colors.rgba('white', 0.08)}`,
            color: colors.text,
            borderRadius: '8px',
            padding: '10px 14px',
            fontSize: '14px',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        } as React.CSSProperties,

        buttonDelete: {
            background: colors.rgba('red', 0.1),
            border: `1px solid ${colors.rgba('red', 0.3)}`,
            color: colors.red,
            borderRadius: '8px',
            height: '38px',
            padding: '0 20px',
            fontWeight: '500',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        } as React.CSSProperties,

        buttonCancel: {
            background: colors.rgba('white', 0.1),
            border: `1px solid ${colors.rgba('white', 0.08)}`,
            color: colors.secondaryText,
            borderRadius: '8px',
            height: '38px',
            padding: '0 20px',
            fontWeight: '500',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        } as React.CSSProperties,

        buttonPrimary: {
            background: `linear-gradient(135deg, ${colors.gold} 0%, ${colors.goldAlt} 100%)`,
            border: 'none',
            color: colors.background,
            borderRadius: '8px',
            height: '38px',
            padding: '0 24px',
            fontWeight: '600',
            boxShadow: `0 4px 12px ${colors.rgba('gold', 0.3)}`,
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        } as React.CSSProperties,
    };

    return (
        <Modal
            title={data ? '修改演员信息' : '添加新演员'}
            {...otherProps}
            width={480}
            forceRender
            onCancel={onCancel}
            styles={styles.modal}
            footer={[
                data && (
                    <Button
                        key="delete"
                        onClick={onDelete}
                        style={styles.buttonDelete}
                        className="actor-modal-btn-delete"
                    >
                        删除
                    </Button>
                ),
                <Button
                    key="cancel"
                    onClick={onCancel}
                    style={styles.buttonCancel}
                    className="actor-modal-btn-cancel"
                >
                    取消
                </Button>,
                <Button
                    key="submit"
                    type="primary"
                    onClick={() => form.submit()}
                    style={styles.buttonPrimary}
                    className="actor-modal-btn-primary"
                >
                    确定
                </Button>
            ]}
        >
            <style>
                {`
                    .actor-modal-btn-delete:hover {
                        background: ${colors.rgba('red', 0.2)} !important;
                        border-color: ${colors.rgba('red', 0.5)} !important;
                        color: ${colors.redLight} !important;
                        transform: translateY(-1px);
                        box-shadow: 0 4px 12px ${colors.rgba('red', 0.3)};
                    }

                    .actor-modal-btn-cancel:hover {
                        background: ${colors.rgba('white', 0.15)} !important;
                        border-color: ${colors.rgba('white', 0.12)} !important;
                        color: ${colors.text} !important;
                        transform: translateY(-1px);
                    }

                    .actor-modal-btn-primary:hover {
                        background: linear-gradient(135deg, ${colors.goldLight} 0%, ${colors.gold} 100%) !important;
                        transform: translateY(-2px);
                        box-shadow: 0 8px 20px ${colors.rgba('gold', 0.4)} !important;
                    }

                    .actor-avatar-wrapper:hover .ant-avatar {
                        transform: scale(1.05);
                        border-color: ${colors.rgba('gold', 0.6)};
                        box-shadow:
                            0 0 0 4px ${colors.rgba('gold', 0.2)},
                            0 0 32px ${colors.rgba('gold', 0.5)},
                            0 12px 40px ${colors.rgba('black', 0.7)};
                    }

                    .ant-input:hover,
                    .ant-input:focus {
                        background: ${colors.rgba('black', 0.8)} !important;
                        border-color: ${colors.rgba('gold', 0.4)} !important;
                        box-shadow: 0 0 0 2px ${colors.rgba('gold', 0.1)} !important;
                    }

                    .ant-input::placeholder {
                        color: ${colors.tertiaryText};
                    }

                    .ant-form-item-label > label.ant-form-item-required:not(.ant-form-item-required-mark-optional)::before {
                        color: ${colors.gold} !important;
                    }

                    .ant-form-item-label > label {
                        color: ${colors.secondaryText} !important;
                        font-size: 14px !important;
                        font-weight: 500 !important;
                        letter-spacing: 0.3px !important;
                    }

                    .ant-form-item-extra {
                        color: ${colors.tertiaryText} !important;
                        font-size: 12px !important;
                    }
                `}
            </style>

            <Form
                form={form}
                layout="vertical"
                onFinish={onSave}
                initialValues={data}
            >
                <Space
                    direction="vertical"
                    style={styles.avatarContainer}
                >
                    <div
                        style={styles.avatarWrapper}
                        className="actor-avatar-wrapper"
                    >
                        <Avatar
                            size={96}
                            icon={<UserOutlined style={styles.avatarIcon} />}
                            src={previewThumb && api.getVideoCover(previewThumb)}
                            onError={() => {
                                handlePreviewError();
                                return true;
                            }}
                            style={styles.avatar}
                        />
                    </div>
                    <div style={styles.avatarLabel}>
                        {previewThumb ? '预览头像' : '暂无头像'}
                    </div>
                </Space>

                <Form.Item
                    name="name"
                    label="演员姓名"
                    rules={[{ required: true, message: '请输入演员姓名' }]}
                >
                    <Input
                        placeholder="请输入演员姓名"
                        style={styles.input}
                    />
                </Form.Item>

                <Form.Item
                    name="thumb"
                    label="头像链接"
                    extra="输入完整的图片URL或相对路径"
                >
                    <Input
                        placeholder="请输入头像链接"
                        onChange={handleThumbChange}
                        style={styles.input}
                    />
                </Form.Item>
            </Form>
        </Modal>
    );
}

export default ModifyModal;
