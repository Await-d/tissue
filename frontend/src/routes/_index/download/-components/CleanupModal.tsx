import { Col, Empty, List, Modal, Row, Space, Tag } from "antd";
import { useThemeColors } from "../../../../hooks/useThemeColors";
import type { CleanupPreviewData } from "@/types/cleanup";

interface CleanupModalProps {
    open: boolean;
    preview: CleanupPreviewData | null;
    loading: boolean;
    onConfirm: () => void;
    onCancel: () => void;
}

export default function CleanupModal({ open, preview, loading, onConfirm, onCancel }: CleanupModalProps) {
    const colors = useThemeColors();

    return (
        <Modal
            title="清理文件预览"
            open={open}
            onOk={onConfirm}
            onCancel={onCancel}
            okText="确认清理"
            cancelText="取消"
            okButtonProps={{ danger: true, loading }}
            width={800}
            styles={{ body: { background: colors.bgBase, maxHeight: '500px', overflowY: 'auto' } }}
        >
            {preview && (
                <div style={{ color: colors.textPrimary }}>
                    <div style={{
                        marginBottom: 16,
                        padding: '12px 16px',
                        background: colors.bgContainer,
                        borderRadius: '8px',
                        border: `1px solid ${colors.borderPrimary}`,
                    }}>
                        <Row gutter={16}>
                            <Col span={12}>
                                <span style={{ color: colors.textSecondary }}>将要删除的文件数：</span>
                                <span style={{ color: colors.error, fontWeight: 600, marginLeft: 8 }}>
                                    {preview.files_to_delete?.length || 0}
                                </span>
                            </Col>
                            <Col span={12}>
                                <span style={{ color: colors.textSecondary }}>预计释放空间：</span>
                                <span style={{ color: colors.success, fontWeight: 600, marginLeft: 8 }}>
                                    {preview.deleted_size_mb ? `${preview.deleted_size_mb} MB` : '0 MB'}
                                </span>
                            </Col>
                        </Row>
                    </div>

                    {preview.files_to_delete && preview.files_to_delete.length > 0 ? (
                        <List
                            dataSource={preview.files_to_delete}
                            renderItem={(file: any) => (
                                <List.Item style={{
                                    background: colors.bgElevated,
                                    borderRadius: '8px',
                                    padding: '12px 16px',
                                    marginBottom: '8px',
                                    border: `1px solid ${colors.borderPrimary}`,
                                }}>
                                    <List.Item.Meta
                                        title={<span style={{ color: colors.textPrimary }}>{file.name}</span>}
                                        description={
                                            <div>
                                                <div style={{ color: colors.textTertiary, fontSize: '13px' }}>{file.path}</div>
                                                <Space style={{ marginTop: 4 }}>
                                                    <Tag style={{ background: colors.rgba('red', 0.2), borderColor: colors.error, color: colors.error }}>
                                                        {file.size}
                                                    </Tag>
                                                    {file.reason && (
                                                        <Tag style={{ background: colors.rgba('warning', 0.2), borderColor: colors.warning, color: colors.warning }}>
                                                            {file.reason}
                                                        </Tag>
                                                    )}
                                                </Space>
                                            </div>
                                        }
                                    />
                                </List.Item>
                            )}
                        />
                    ) : (
                        <Empty description="没有需要清理的文件" style={{ color: colors.textSecondary }} />
                    )}
                </div>
            )}
        </Modal>
    );
}
