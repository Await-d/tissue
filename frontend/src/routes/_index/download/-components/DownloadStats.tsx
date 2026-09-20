import { memo, useMemo } from "react";
import { Card, Col, Row, Statistic } from "antd";
import { useThemeColors } from "../../../../hooks/useThemeColors";

interface DownloadStatsFile {
    progress: number;
}

interface DownloadStatsTask {
    files: DownloadStatsFile[];
}

interface DownloadStatsProps {
    data: DownloadStatsTask[];
}

function DownloadStats({ data }: DownloadStatsProps) {
    const colors = useThemeColors();

    const stats = useMemo(() => {
        let downloading = 0;
        let completed = 0;
        let failed = 0;
        data.forEach((item) => {
            item.files.forEach((file) => {
                if (file.progress > 0 && file.progress < 1) downloading += 1;
                if (file.progress >= 1) completed += 1;
                if (file.progress === 0) failed += 1;
            });
        });
        return { total: data.length, downloading, completed, failed };
    }, [data]);

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
                        value={stats.total}
                        valueStyle={{ color: colors.textPrimary, fontSize: '24px', fontWeight: 600 }}
                    />
                </Card>
            </Col>
            <Col span={6}>
                <Card size="small" style={cardStyle} styles={{ body: bodyStyle }}>
                    <Statistic
                        title={<span style={{ color: colors.textSecondary, fontSize: '14px' }}>进行中</span>}
                        value={stats.downloading}
                        valueStyle={{ color: colors.info, fontSize: '24px', fontWeight: 600 }}
                    />
                </Card>
            </Col>
            <Col span={6}>
                <Card size="small" style={cardStyle} styles={{ body: bodyStyle }}>
                    <Statistic
                        title={<span style={{ color: colors.textSecondary, fontSize: '14px' }}>已完成</span>}
                        value={stats.completed}
                        valueStyle={{ color: colors.success, fontSize: '24px', fontWeight: 600 }}
                    />
                </Card>
            </Col>
            <Col span={6}>
                <Card size="small" style={cardStyle} styles={{ body: bodyStyle }}>
                    <Statistic
                        title={<span style={{ color: colors.textSecondary, fontSize: '14px' }}>失败/等待</span>}
                        value={stats.failed}
                        valueStyle={{ color: colors.redLight, fontSize: '24px', fontWeight: 600 }}
                    />
                </Card>
            </Col>
        </Row>
    );
}

export default memo(DownloadStats);
