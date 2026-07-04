import { Card, Col, Row, Statistic } from "antd";
import { useThemeColors } from "../../../../hooks/useThemeColors";

interface DownloadStatsProps {
    data: any[];
}

export default function DownloadStats({ data }: DownloadStatsProps) {
    const colors = useThemeColors();

    const cardStyle = {
        background: colors.bgContainer,
        borderColor: colors.borderPrimary,
        borderRadius: '8px',
    };

    const bodyStyle = { padding: '16px' };

    return (
        <Row gutter={16} style={{ marginBottom: 20 }}>
            <Col span={6}>
                <Card size="small" style={cardStyle} styles={{ body: bodyStyle }}>
                    <Statistic
                        title={<span style={{ color: colors.textSecondary, fontSize: '14px' }}>总任务数</span>}
                        value={data.length}
                        valueStyle={{ color: colors.textPrimary, fontSize: '24px', fontWeight: 600 }}
                    />
                </Card>
            </Col>
            <Col span={6}>
                <Card size="small" style={cardStyle} styles={{ body: bodyStyle }}>
                    <Statistic
                        title={<span style={{ color: colors.textSecondary, fontSize: '14px' }}>进行中</span>}
                        value={data.reduce((count: number, item: any) =>
                            count + item.files.filter((f: any) => f.progress > 0 && f.progress < 1).length, 0
                        )}
                        valueStyle={{ color: colors.info, fontSize: '24px', fontWeight: 600 }}
                    />
                </Card>
            </Col>
            <Col span={6}>
                <Card size="small" style={cardStyle} styles={{ body: bodyStyle }}>
                    <Statistic
                        title={<span style={{ color: colors.textSecondary, fontSize: '14px' }}>已完成</span>}
                        value={data.reduce((count: number, item: any) =>
                            count + item.files.filter((f: any) => f.progress >= 1).length, 0
                        )}
                        valueStyle={{ color: colors.success, fontSize: '24px', fontWeight: 600 }}
                    />
                </Card>
            </Col>
            <Col span={6}>
                <Card size="small" style={cardStyle} styles={{ body: bodyStyle }}>
                    <Statistic
                        title={<span style={{ color: colors.textSecondary, fontSize: '14px' }}>失败/等待</span>}
                        value={data.reduce((count: number, item: any) =>
                            count + item.files.filter((f: any) => f.progress === 0).length, 0
                        )}
                        valueStyle={{ color: colors.redLight, fontSize: '24px', fontWeight: 600 }}
                    />
                </Card>
            </Col>
        </Row>
    );
}
