import {Button, Checkbox, Form, Input, Modal, ModalProps, Space} from "antd";
import {FilterOutlined} from "@ant-design/icons";
import {useThemeColors} from "../../../../hooks/useThemeColors";

export interface FilterParams {
    title?: string
    actors?: string[]
}

interface Props extends ModalProps {
    actors: any[]
    initialValues: any
    onFilter: (params: FilterParams) => void
}

function VideoFilterModal(props: Props) {

    const colors = useThemeColors()
    const {onFilter, actors = [], initialValues, ...otherProps} = props
    const [form] = Form.useForm()

    async function onOk() {
        const values = await form.validateFields()
        onFilter(values)
    }

    function handleRest() {
        form.resetFields()
        onFilter({})
    }

    const actorOptions = actors.map(actor => (
        {label: `${actor.name}(${actor.count}部)`, value: actor.name}
    ))

    return (
        <Modal
            title={
                <div style={{
                    fontSize: '18px',
                    fontWeight: 600,
                    color: colors.textPrimary,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                }}>
                    <FilterOutlined style={{ color: colors.goldPrimary }} />
                    <span className="tissue-text-gold">影片过滤</span>
                </div>
            }
            {...otherProps}
            forceRender
            footer={
                <Space>
                    <Button
                        onClick={handleRest}
                        style={{
                            background: colors.bgSpotlight,
                            border: `1px solid ${colors.borderPrimary}`,
                            color: colors.textPrimary,
                            fontWeight: 500,
                            transition: 'all var(--transition-fast)',
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.borderColor = colors.borderGold;
                            e.currentTarget.style.color = colors.goldLight;
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.borderColor = colors.borderPrimary;
                            e.currentTarget.style.color = colors.textPrimary;
                        }}
                    >
                        重 制
                    </Button>
                    <Button
                        type="primary"
                        onClick={onOk}
                        className="tissue-btn-gold"
                        style={{
                            background: colors.goldGradient,
                            border: 'none',
                            color: colors.bgBase,
                            fontWeight: 600,
                            boxShadow: colors.shadowSm,
                            transition: 'all var(--transition-base)',
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.background = colors.goldGradientHover;
                            e.currentTarget.style.boxShadow = `0 0 20px ${colors.rgba('gold', 0.3)}, 0 4px 16px ${colors.rgba('black', 0.4)}`;
                            e.currentTarget.style.transform = 'translateY(-1px)';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.background = colors.goldGradient;
                            e.currentTarget.style.boxShadow = colors.shadowSm;
                            e.currentTarget.style.transform = 'translateY(0)';
                        }}
                    >
                        确 定
                    </Button>
                </Space>
            }
            styles={{
                content: {
                    background: colors.bgContainer,
                    border: `1px solid ${colors.borderPrimary}`,
                    boxShadow: colors.shadowLg,
                },
                header: {
                    background: 'transparent',
                    borderBottom: `1px solid ${colors.borderPrimary}`,
                    paddingBottom: '16px',
                },
                body: {
                    paddingTop: '24px',
                },
            }}
        >
            <Form
                form={form}
                layout="vertical"
                initialValues={initialValues}
                style={{
                    padding: '8px 0',
                }}
            >
                <Form.Item
                    name="title"
                    label={
                        <span style={{
                            color: colors.textPrimary,
                            fontWeight: 500,
                            fontSize: '14px',
                        }}>
                            标题
                        </span>
                    }
                >
                    <Input
                        allowClear
                        placeholder="输入标题关键词..."
                        style={{
                            background: colors.bgElevated,
                            border: `1px solid ${colors.borderPrimary}`,
                            color: colors.textPrimary,
                            borderRadius: 'var(--radius-md)',
                            transition: 'all var(--transition-fast)',
                        }}
                        onFocus={(e) => {
                            e.currentTarget.style.borderColor = colors.borderGold;
                            e.currentTarget.style.boxShadow = `0 0 0 2px ${colors.rgba('gold', 0.1)}`;
                        }}
                        onBlur={(e) => {
                            e.currentTarget.style.borderColor = colors.borderPrimary;
                            e.currentTarget.style.boxShadow = 'none';
                        }}
                    />
                </Form.Item>
                <Form.Item
                    name="actors"
                    label={
                        <span style={{
                            color: colors.textPrimary,
                            fontWeight: 500,
                            fontSize: '14px',
                        }}>
                            演员
                        </span>
                    }
                >
                    <Checkbox.Group
                        options={actorOptions.map(opt => ({
                            ...opt,
                            style: {
                                display: 'inline-flex',
                                alignItems: 'center',
                                padding: '8px 12px',
                                margin: '4px',
                                background: colors.bgElevated,
                                border: `1px solid ${colors.borderPrimary}`,
                                borderRadius: 'var(--radius-sm)',
                                color: colors.textPrimary,
                                transition: 'all var(--transition-fast)',
                                cursor: 'pointer',
                                userSelect: 'none',
                            },
                        }))}
                        style={{
                            display: 'flex',
                            flexWrap: 'wrap',
                            gap: '0',
                            maxHeight: '320px',
                            overflowY: 'auto',
                            padding: '8px',
                            background: colors.bgBase,
                            borderRadius: 'var(--radius-md)',
                            border: `1px solid ${colors.borderSecondary}`,
                        }}
                    />
                </Form.Item>
            </Form>
        </Modal>
    )
}

export default VideoFilterModal
