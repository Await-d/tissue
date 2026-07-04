import { Badge, Col, Empty, List, Modal, Row, Space, Statistic, Tag } from "antd";
import { useThemeColors } from "../../../../hooks/useThemeColors";
import type { CleanupResultData } from "@/types/cleanup";

interface BatchCleanupModalProps {
    open: boolean;
    result: CleanupResultData | null;
    affectedResults: any[];
    loading: boolean;
    onConfirm: () => void;
    onCancel: () => void;
}

export default function BatchCleanupModal({
    open, result, affectedResults, loading, onConfirm, onCancel
}: BatchCleanupModalProps) {
    const colors = useThemeColors();

    return (
        <Modal
            title="不符合过滤规则的文件预览"
            open={open}
            onOk={onConfirm}
            onCancel={onCancel}
            okText="确认清理"
            cancelText="取消"
            okButtonProps={{ danger: true, loading }}
            width={900}
            styles={{ body: { background: colors.bgBase, maxHeight: '600px', overflowY: 'auto' } }}
        >
            {result && (
                <div style={{ color: colors.textPrimary }}>
                    {/* 总览统计 */}
                    <div style={{
                        marginBottom: 16,
                        padding: '16px',
                        background: colors.bgContainer,
                        borderRadius: '8px',
                        border: `1px solid ${colors.borderPrimary}`,
                    }}>
                        <Row gutter={16}>
                            <Col span={8}>
                                <Statistic
                                    title={<span style={{ color: colors.textSecondary }}>将要清理的种子数</span>}
                                    value={affectedResults.length}
                                    valueStyle={{ color: colors.goldPrimary, fontWeight: 600 }}
                                />
                            </Col>
                            <Col span={8}>
                                <Statistic
                                    title={<span style={{ color: colors.textSecondary }}>总共要删除的文件数</span>}
                                    value={result.total_deleted_files || 0}
                                    valueStyle={{ color: colors.error, fontWeight: 600 }}
                                />
                            </Col>
                            <Col span={8}>
                                <Statistic
                                    title={<span style={{ color: colors.textSecondary }}>预计释放空间</span>}
                                    value={(result.total_deleted_size_mb || 0) / 1024}
                                    precision={2}
                                    suffix="GB"
                                    valueStyle={{ color: colors.success, fontWeight: 600 }}
                                />
                            </Col>
                        </Row>
                    </div>

                    {/* 每个种子的详细清理信息 */}
                    {affectedResults.length > 0 ? (
                        <div>
                            <div style={{ marginBottom: 12, color: colors.textSecondary, fontSize: '14px', fontWeight: 500 }}>
                                详细清理列表：
                            </div>
                            <List
                                dataSource={affectedResults}
                                renderItem={(item: any, index: number) => (
                                    <List.Item style={{
                                        background: colors.bgElevated,
                                        borderRadius: '8px',
                                        padding: '12px 16px',
                                        marginBottom: '8px',
                                        border: `1px solid ${colors.borderPrimary}`,
                                    }}>
                                        <div style={{ width: '100%' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
                                                <Badge count={index + 1} style={{ background: colors.goldPrimary, marginRight: 8 }} />
                                                <span style={{ color: colors.textPrimary, fontWeight: 500, fontSize: '14px' }}>
                                                    {item.name || '未知种子'}
                                                </span>
                                                <Tag style={{ marginLeft: 'auto', background: colors.rgba('red', 0.2), borderColor: colors.error, color: colors.error }}>
                                                    {item.deleted_files || 0} 个文件
                                                </Tag>
                                            </div>
                                            <div style={{ paddingLeft: 32, color: colors.textTertiary, fontSize: '13px' }}>
                                                {item.message || '无详情'}
                                            </div>
                                        </div>
                                    </List.Item>
                                )}
                            />
                        </div>
                    ) : (
                        <Empty description="没有需要批量清理的文件" style={{ color: colors.textSecondary }} />
                    )}
                </div>
            )}
        </Modal>
    );
}
