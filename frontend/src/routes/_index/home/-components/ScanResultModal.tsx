import { Button, Col, Modal, Row, Statistic } from "antd";
import { CheckCircleOutlined, ClockCircleOutlined, FileTextOutlined, PlusCircleOutlined } from "@ant-design/icons";
import { useThemeColors } from "../../../../hooks/useThemeColors";
import type { ScanResult } from "../../../../apis/fileScan";

interface ScanResultModalProps {
    open: boolean;
    result: ScanResult | null;
    onCancel: () => void;
}

export default function ScanResultModal({ open, result, onCancel }: ScanResultModalProps) {
    const colors = useThemeColors();

    return (
        <Modal
            open={open}
            onCancel={onCancel}
            footer={[
                <Button
                    key="close"
                    type="primary"
                    onClick={onCancel}
                    style={{
                        background: `linear-gradient(135deg, ${colors.goldPrimary} 0%, ${colors.rgba('gold', 0.8)} 100%)`,
                        border: 'none', borderRadius: '8px', height: '40px', fontWeight: 500,
                    }}
                >
                    确定
                </Button>
            ]}
            width={600}
            centered
            style={{ borderRadius: '16px' }}
            styles={{
                content: { background: colors.bgContainer, borderRadius: '16px', border: `1px solid ${colors.borderPrimary}` },
                header: {
                    background: `linear-gradient(135deg, ${colors.rgba('gold', 0.08)} 0%, ${colors.rgba('gold', 0.02)} 100%)`,
                    borderBottom: `1px solid ${colors.borderSecondary}`,
                    borderRadius: '16px 16px 0 0', padding: '20px 24px',
                },
                body: { padding: '32px 24px' },
            }}
            title={
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '18px', fontWeight: 600, color: colors.textPrimary }}>
                    <div style={{
                        width: 40, height: 40, borderRadius: '10px',
                        background: colors.rgba('gold', 0.12),
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}>
                        <CheckCircleOutlined style={{ fontSize: 20, color: colors.goldPrimary }} />
                    </div>
                    扫描结果
                </div>
            }
        >
            {result && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                    <Row gutter={[16, 16]}>
                        <Col span={12}>
                            <div style={{
                                background: colors.rgba('bgContainer', 0.5), borderRadius: '12px', padding: '20px',
                                border: `1px solid ${colors.borderSecondary}`,
                            }}>
                                <Statistic
                                    title={<div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: colors.textSecondary, fontSize: '14px' }}><ClockCircleOutlined />扫描时间</div>}
                                    value={new Date(result.scan_time).toLocaleString('zh-CN')}
                                    valueStyle={{ fontSize: '14px', color: colors.textPrimary, fontWeight: 500 }}
                                />
                            </div>
                        </Col>
                        <Col span={12}>
                            <div style={{
                                background: colors.rgba('bgContainer', 0.5), borderRadius: '12px', padding: '20px',
                                border: `1px solid ${colors.borderSecondary}`,
                            }}>
                                <Statistic
                                    title={<div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: colors.textSecondary, fontSize: '14px' }}><ClockCircleOutlined />扫描耗时</div>}
                                    value={result.scan_duration.toFixed(2)}
                                    suffix="秒"
                                    valueStyle={{ fontSize: '20px', color: colors.textPrimary, fontWeight: 600 }}
                                />
                            </div>
                        </Col>
                        <Col span={12}>
                            <div style={{
                                background: colors.rgba('bgContainer', 0.5), borderRadius: '12px', padding: '20px',
                                border: `1px solid ${colors.borderSecondary}`,
                            }}>
                                <Statistic
                                    title={<div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: colors.textSecondary, fontSize: '14px' }}><FileTextOutlined />扫描文件总数</div>}
                                    value={result.total_files}
                                    valueStyle={{ fontSize: '20px', color: colors.textPrimary, fontWeight: 600 }}
                                />
                            </div>
                        </Col>
                        <Col span={12}>
                            <div style={{
                                background: `linear-gradient(135deg, ${colors.rgba('gold', 0.08)} 0%, ${colors.rgba('gold', 0.02)} 100%)`,
                                borderRadius: '12px', padding: '20px',
                                border: `1px solid ${colors.borderGold}`,
                                boxShadow: `0 2px 8px ${colors.rgba('gold', 0.1)}`,
                            }}>
                                <Statistic
                                    title={<div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: colors.textSecondary, fontSize: '14px' }}><PlusCircleOutlined />新发现视频</div>}
                                    value={result.new_found}
                                    valueStyle={{ fontSize: '28px', color: colors.goldPrimary, fontWeight: 700 }}
                                />
                            </div>
                        </Col>
                        <Col span={24}>
                            <div style={{
                                background: colors.rgba('bgContainer', 0.5), borderRadius: '12px', padding: '20px',
                                border: `1px solid ${colors.borderSecondary}`,
                            }}>
                                <Statistic
                                    title={<div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: colors.textSecondary, fontSize: '14px' }}><CheckCircleOutlined />已存在视频</div>}
                                    value={result.already_exists}
                                    valueStyle={{ fontSize: '20px', color: colors.textPrimary, fontWeight: 600 }}
                                />
                            </div>
                        </Col>
                    </Row>

                    {result.new_found > 0 && (
                        <div style={{
                            background: colors.rgba('gold', 0.05),
                            border: `1px solid ${colors.borderGold}`,
                            borderRadius: '10px', padding: '16px 20px',
                            display: 'flex', alignItems: 'center', gap: '12px',
                        }}>
                            <CheckCircleOutlined style={{ fontSize: 18, color: colors.goldPrimary }} />
                            <div style={{ flex: 1, fontSize: '14px', color: colors.textPrimary }}>
                                新视频已自动添加到视频库，页面已刷新
                            </div>
                        </div>
                    )}
                </div>
            )}
        </Modal>
    );
}
