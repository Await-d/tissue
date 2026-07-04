import { Button, Card, Col, Row, Select, Space, Switch } from "antd";
import { useThemeColors } from "../../../../hooks/useThemeColors";

export interface AdvancedFilters {
    status: string;
    sizeRange: number[];
    dateRange: any;
    sortBy: string;
    sortOrder: string;
}

interface DownloadFiltersProps {
    includeSuccess: boolean;
    includeFailed: boolean;
    onIncludeSuccessChange: (v: boolean) => void;
    onIncludeFailedChange: (v: boolean) => void;
    showAdvancedFilters: boolean;
    advancedFilters: AdvancedFilters;
    onAdvancedFiltersChange: (v: AdvancedFilters) => void;
    onResetFilters: () => void;
}

export default function DownloadFilters({
    includeSuccess,
    includeFailed,
    onIncludeSuccessChange,
    onIncludeFailedChange,
    showAdvancedFilters,
    advancedFilters,
    onAdvancedFiltersChange,
    onResetFilters,
}: DownloadFiltersProps) {
    const colors = useThemeColors();

    return (
        <>
            {/* 基础过滤选项 */}
            <div style={{
                marginBottom: 16,
                padding: '12px 16px',
                background: colors.bgContainer,
                border: `1px solid ${colors.borderPrimary}`,
                borderRadius: '8px',
            }}>
                <Row gutter={16}>
                    <Col>
                        <Space>
                            <span style={{ color: colors.textSecondary, fontSize: '14px' }}>显示已完成:</span>
                            <Switch
                                checked={includeSuccess}
                                onChange={onIncludeSuccessChange}
                                size="small"
                                style={{ background: includeSuccess ? colors.goldPrimary : colors.borderSecondary }}
                            />
                        </Space>
                    </Col>
                    <Col>
                        <Space>
                            <span style={{ color: colors.textSecondary, fontSize: '14px' }}>显示失败:</span>
                            <Switch
                                checked={includeFailed}
                                onChange={onIncludeFailedChange}
                                size="small"
                                style={{ background: includeFailed ? colors.goldPrimary : colors.borderSecondary }}
                            />
                        </Space>
                    </Col>
                </Row>
            </div>

            {/* 高级过滤选项 */}
            {showAdvancedFilters && (
                <Card
                    size="small"
                    style={{
                        marginBottom: 16,
                        background: colors.bgContainer,
                        borderColor: colors.borderPrimary,
                        borderRadius: '8px',
                    }}
                    styles={{ body: { padding: '16px', background: colors.bgContainer } }}
                >
                    <Row gutter={[16, 8]}>
                        <Col span={8}>
                            <div style={{ marginBottom: 8, color: colors.textSecondary, fontSize: '14px', fontWeight: 500 }}>
                                状态筛选
                            </div>
                            <Select
                                value={advancedFilters.status}
                                onChange={(value) => onAdvancedFiltersChange({ ...advancedFilters, status: value })}
                                style={{ width: '100%' }}
                                dropdownStyle={{ background: colors.bgContainer, borderColor: colors.borderPrimary }}
                            >
                                <Select.Option value="all">全部状态</Select.Option>
                                <Select.Option value="downloading">下载中</Select.Option>
                                <Select.Option value="completed">已完成</Select.Option>
                                <Select.Option value="failed">失败/等待</Select.Option>
                            </Select>
                        </Col>
                        <Col span={8}>
                            <div style={{ marginBottom: 8, color: colors.textSecondary, fontSize: '14px', fontWeight: 500 }}>
                                排序方式
                            </div>
                            <Select
                                value={`${advancedFilters.sortBy}-${advancedFilters.sortOrder}`}
                                onChange={(value) => {
                                    const [sortBy, sortOrder] = value.split('-');
                                    onAdvancedFiltersChange({ ...advancedFilters, sortBy, sortOrder });
                                }}
                                style={{ width: '100%' }}
                                dropdownStyle={{ background: colors.bgContainer, borderColor: colors.borderPrimary }}
                            >
                                <Select.Option value="date-desc">添加时间 (新→旧)</Select.Option>
                                <Select.Option value="date-asc">添加时间 (旧→新)</Select.Option>
                                <Select.Option value="progress-desc">进度 (高→低)</Select.Option>
                                <Select.Option value="progress-asc">进度 (低→高)</Select.Option>
                                <Select.Option value="size-desc">大小 (大→小)</Select.Option>
                                <Select.Option value="size-asc">大小 (小→大)</Select.Option>
                            </Select>
                        </Col>
                        <Col span={8}>
                            <div style={{ marginBottom: 8, color: colors.textSecondary, fontSize: '14px', fontWeight: 500 }}>
                                快速操作
                            </div>
                            <Space>
                                <Button
                                    size="small"
                                    onClick={onResetFilters}
                                    style={{ background: colors.bgContainer, borderColor: colors.borderPrimary, color: colors.textSecondary }}
                                >
                                    重置筛选
                                </Button>
                            </Space>
                        </Col>
                    </Row>
                </Card>
            )}
        </>
    );
}
