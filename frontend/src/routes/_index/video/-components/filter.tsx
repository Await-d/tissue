import {Button, Checkbox, Form, Input, Modal, ModalProps, Space} from "antd";
import {FilterOutlined} from "@ant-design/icons";

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
                    color: 'var(--color-text-primary)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                }}>
                    <FilterOutlined style={{ color: 'var(--color-gold-primary)' }} />
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
                            background: 'var(--color-bg-spotlight)',
                            border: '1px solid var(--color-border-primary)',
                            color: 'var(--color-text-primary)',
                            fontWeight: 500,
                            transition: 'all var(--transition-fast)',
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.borderColor = 'var(--color-border-gold)';
                            e.currentTarget.style.color = 'var(--color-gold-light)';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.borderColor = 'var(--color-border-primary)';
                            e.currentTarget.style.color = 'var(--color-text-primary)';
                        }}
                    >
                        重 制
                    </Button>
                    <Button
                        type="primary"
                        onClick={onOk}
                        className="tissue-btn-gold"
                        style={{
                            background: 'linear-gradient(135deg, var(--color-gold-primary) 0%, var(--color-gold-dark) 100%)',
                            border: 'none',
                            color: 'var(--color-bg-base)',
                            fontWeight: 600,
                            boxShadow: 'var(--shadow-sm)',
                            transition: 'all var(--transition-base)',
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.background = 'linear-gradient(135deg, var(--color-gold-light) 0%, var(--color-gold-primary) 100%)';
                            e.currentTarget.style.boxShadow = '0 0 20px rgba(212, 168, 82, 0.3), 0 4px 16px rgba(0, 0, 0, 0.4)';
                            e.currentTarget.style.transform = 'translateY(-1px)';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.background = 'linear-gradient(135deg, var(--color-gold-primary) 0%, var(--color-gold-dark) 100%)';
                            e.currentTarget.style.boxShadow = 'var(--shadow-sm)';
                            e.currentTarget.style.transform = 'translateY(0)';
                        }}
                    >
                        确 定
                    </Button>
                </Space>
            }
            styles={{
                content: {
                    background: 'var(--color-bg-container)',
                    border: '1px solid var(--color-border-primary)',
                    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5)',
                },
                header: {
                    background: 'transparent',
                    borderBottom: '1px solid var(--color-border-primary)',
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
                            color: 'var(--color-text-primary)',
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
                            background: 'var(--color-bg-elevated)',
                            border: '1px solid var(--color-border-primary)',
                            color: 'var(--color-text-primary)',
                            borderRadius: 'var(--radius-md)',
                            transition: 'all var(--transition-fast)',
                        }}
                        onFocus={(e) => {
                            e.currentTarget.style.borderColor = 'var(--color-border-gold)';
                            e.currentTarget.style.boxShadow = '0 0 0 2px rgba(212, 168, 82, 0.1)';
                        }}
                        onBlur={(e) => {
                            e.currentTarget.style.borderColor = 'var(--color-border-primary)';
                            e.currentTarget.style.boxShadow = 'none';
                        }}
                    />
                </Form.Item>
                <Form.Item
                    name="actors"
                    label={
                        <span style={{
                            color: 'var(--color-text-primary)',
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
                                background: 'var(--color-bg-elevated)',
                                border: '1px solid var(--color-border-primary)',
                                borderRadius: 'var(--radius-sm)',
                                color: 'var(--color-text-primary)',
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
                            background: 'var(--color-bg-base)',
                            borderRadius: 'var(--radius-md)',
                            border: '1px solid var(--color-border-secondary)',
                        }}
                    />
                </Form.Item>
            </Form>
        </Modal>
    )
}

export default VideoFilterModal
