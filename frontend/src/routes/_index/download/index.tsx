import {
    Card,
    Collapse,
    Empty,
    Input,
    List,
    message,
    Modal,
    Space,
    Tag,
    theme,
    Tooltip,
    Row,
    Col,
    Statistic,
    Select,
    DatePicker,
    Button,
    Progress,
    Checkbox,
    Divider
} from "antd";
import * as api from "../../../apis/download";
import {useDebounce, useRequest} from "ahooks";
import {
    FileDoneOutlined,
    FolderViewOutlined,
    DownloadOutlined,
    CheckCircleOutlined,
    CloseCircleOutlined,
    SyncOutlined,
    DeleteOutlined,
    PauseCircleOutlined,
    PlayCircleOutlined,
    CloudDownloadOutlined,
    FileOutlined,
    HddOutlined
} from "@ant-design/icons";
import React, {useMemo, useState} from "react";
import IconButton from "../../../components/IconButton";
import {createFileRoute, Link} from "@tanstack/react-router";
import VideoDetail from "../../../components/VideoDetail";
import dayjs, {Dayjs} from "dayjs";
import isBetween from "dayjs/plugin/isBetween";

dayjs.extend(isBetween);

const {useToken} = theme;
const {RangePicker} = DatePicker;

export const Route = createFileRoute('/_index/download/')({
    component: Download,
});

// Download status enum
enum DownloadStatus {
    ALL = 'all',
    DOWNLOADING = 'downloading',
    COMPLETED = 'completed',
    FAILED = 'failed'
}

// Mock function to determine status (replace with actual API data)
const getDownloadStatus = (torrent: any): DownloadStatus => {
    // This should come from API, for now we assume all are completed
    if (torrent.progress !== undefined) {
        if (torrent.progress === 100) return DownloadStatus.COMPLETED;
        if (torrent.progress < 0) return DownloadStatus.FAILED;
        return DownloadStatus.DOWNLOADING;
    }
    return DownloadStatus.COMPLETED;
};

// Format bytes to human readable
const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

function Download() {
    const {token} = useToken();
    const {data = [], loading, refresh} = useRequest(api.getDownloads);
    const [selected, setSelected] = useState<string | undefined>();
    const [keyword, setKeyword] = useState<string>();
    const keywordDebounce = useDebounce(keyword, {wait: 1000});

    // Filter states
    const [statusFilter, setStatusFilter] = useState<DownloadStatus>(DownloadStatus.ALL);
    const [dateRange, setDateRange] = useState<[Dayjs | null, Dayjs | null] | null>(null);

    // Batch operation states
    const [selectedHashes, setSelectedHashes] = useState<string[]>([]);
    const [batchMode, setBatchMode] = useState(false);

    // Calculate statistics
    const statistics = useMemo(() => {
        const total = data.length;
        let downloading = 0;
        let completed = 0;
        let failed = 0;
        let totalSize = 0;
        let todayCount = 0;
        const today = dayjs().startOf('day');

        data.forEach((torrent: any) => {
            const status = getDownloadStatus(torrent);
            if (status === DownloadStatus.DOWNLOADING) downloading++;
            else if (status === DownloadStatus.COMPLETED) completed++;
            else if (status === DownloadStatus.FAILED) failed++;

            // Calculate total size
            if (torrent.files) {
                torrent.files.forEach((file: any) => {
                    // Parse size string like "1.5 GB" to bytes
                    const sizeStr = file.size || '0 B';
                    const match = sizeStr.match(/^([\d.]+)\s*([A-Z]+)$/);
                    if (match) {
                        const value = parseFloat(match[1]);
                        const unit = match[2];
                        const multipliers: {[key: string]: number} = {
                            'B': 1,
                            'KB': 1024,
                            'MB': 1024 * 1024,
                            'GB': 1024 * 1024 * 1024,
                            'TB': 1024 * 1024 * 1024 * 1024
                        };
                        totalSize += value * (multipliers[unit] || 0);
                    }
                });
            }

            // Count today's downloads (mock - should come from API)
            if (torrent.added_on && dayjs(torrent.added_on).isAfter(today)) {
                todayCount++;
            }
        });

        return {
            total,
            downloading,
            completed,
            failed,
            totalSize,
            todayCount
        };
    }, [data]);

    // Filter data
    const filteredData = useMemo(() => {
        return data.filter((item: any) => {
            // Keyword filter
            const matchKeyword = !keywordDebounce ||
                item.name.indexOf(keywordDebounce) !== -1 ||
                item.files.some((sub: any) => (
                    sub.name.indexOf(keywordDebounce) !== -1 ||
                    sub.path.indexOf(keywordDebounce) !== -1
                ));

            if (!matchKeyword) return false;

            // Status filter
            if (statusFilter !== DownloadStatus.ALL) {
                const status = getDownloadStatus(item);
                if (status !== statusFilter) return false;
            }

            // Date range filter
            if (dateRange && dateRange[0] && dateRange[1] && item.added_on) {
                const itemDate = dayjs(item.added_on);
                if (!itemDate.isBetween(dateRange[0], dateRange[1], 'day', '[]')) {
                    return false;
                }
            }

            return true;
        });
    }, [data, keywordDebounce, statusFilter, dateRange]);

    const {run: onComplete} = useRequest(api.completeDownload, {
        manual: true,
        onSuccess: () => {
            message.success("标记成功");
            refresh();
        }
    });

    // Batch operations
    const handleBatchComplete = () => {
        Modal.confirm({
            title: '批量标记完成',
            content: `确认标记 ${selectedHashes.length} 个下载为完成？`,
            onOk: async () => {
                for (const hash of selectedHashes) {
                    await onComplete(hash);
                }
                setSelectedHashes([]);
                setBatchMode(false);
            }
        });
    };

    const handleBatchDelete = () => {
        Modal.confirm({
            title: '批量删除',
            content: `确认删除 ${selectedHashes.length} 个下载？（不会删除已下载的文件）`,
            okType: 'danger',
            onOk: async () => {
                for (const hash of selectedHashes) {
                    await api.deleteTorrent(hash, false);
                }
                message.success(`已删除 ${selectedHashes.length} 个下载`);
                setSelectedHashes([]);
                setBatchMode(false);
                refresh();
            }
        });
    };

    const handleSelectAll = (checked: boolean) => {
        if (checked) {
            setSelectedHashes(filteredData.map((item: any) => item.hash));
        } else {
            setSelectedHashes([]);
        }
    };

    const handleSelectItem = (hash: string, checked: boolean) => {
        if (checked) {
            setSelectedHashes([...selectedHashes, hash]);
        } else {
            setSelectedHashes(selectedHashes.filter(h => h !== hash));
        }
    };

    // Get status tag
    const getStatusTag = (torrent: any) => {
        const status = getDownloadStatus(torrent);
        const configs: Record<string, {color: string; icon: React.ReactNode; text: string}> = {
            [DownloadStatus.DOWNLOADING]: {
                color: 'processing',
                icon: <SyncOutlined spin />,
                text: '下载中'
            },
            [DownloadStatus.COMPLETED]: {
                color: 'success',
                icon: <CheckCircleOutlined />,
                text: '已完成'
            },
            [DownloadStatus.FAILED]: {
                color: 'error',
                icon: <CloseCircleOutlined />,
                text: '失败'
            }
        };
        const config = configs[status] || configs[DownloadStatus.COMPLETED];
        return (
            <Tag color={config.color} icon={config.icon}>
                {config.text}
            </Tag>
        );
    };

    // Get progress bar
    const getProgressBar = (torrent: any) => {
        const progress = torrent.progress !== undefined ? torrent.progress : 100;
        const status = getDownloadStatus(torrent);

        if (status === DownloadStatus.FAILED) {
            return <Progress percent={progress} status="exception" size="small" />;
        }
        if (status === DownloadStatus.DOWNLOADING) {
            return (
                <Space direction="vertical" style={{width: '100%'}} size="small">
                    <Progress percent={progress} status="active" size="small" />
                    {torrent.download_speed && (
                        <span style={{fontSize: '12px', color: token.colorTextSecondary}}>
                            速度: {torrent.download_speed}
                        </span>
                    )}
                </Space>
            );
        }
        return <Progress percent={100} size="small" />;
    };

    const items = filteredData.map((torrent: any) => ({
        key: torrent.hash,
        label: (
            <Space>
                {batchMode && (
                    <Checkbox
                        checked={selectedHashes.includes(torrent.hash)}
                        onChange={(e) => handleSelectItem(torrent.hash, e.target.checked)}
                        onClick={(e) => e.stopPropagation()}
                    />
                )}
                <span>{torrent.name}</span>
                {getStatusTag(torrent)}
            </Space>
        ),
        children: (
            <Space direction="vertical" style={{width: '100%'}} size="middle">
                {getProgressBar(torrent)}
                <List
                    itemLayout="horizontal"
                    dataSource={torrent.files}
                    renderItem={(item: any, index) => (
                        <List.Item
                            actions={[
                                <Tooltip title="整理">
                                    <IconButton
                                        onClick={() => {
                                            setSelected(item.path);
                                        }}
                                    >
                                        <FolderViewOutlined style={{fontSize: token.sizeLG}} />
                                    </IconButton>
                                </Tooltip>
                            ]}
                        >
                            <List.Item.Meta
                                avatar={<FileOutlined style={{fontSize: 24, color: token.colorPrimary}} />}
                                title={
                                    <span>
                                        {item.name}
                                        <Tag style={{marginLeft: 5}} color="success">
                                            {item.size}
                                        </Tag>
                                    </span>
                                }
                                description={item.path}
                            />
                        </List.Item>
                    )}
                />
            </Space>
        ),
        extra: (
            <Space>
                <Tooltip title='标记为"整理成功"'>
                    <IconButton
                        onClick={() => {
                            Modal.confirm({
                                title: '是否确认标记为完成',
                                onOk: () => onComplete(torrent.hash)
                            });
                        }}
                    >
                        <FileDoneOutlined style={{fontSize: token.sizeLG}} />
                    </IconButton>
                </Tooltip>
            </Space>
        )
    }));

    return (
        <Space direction="vertical" style={{width: '100%'}} size="large">
            {/* Statistics Panel */}
            <Card>
                <Row gutter={[16, 16]}>
                    <Col xs={24} sm={12} md={6}>
                        <Statistic
                            title="总下载数"
                            value={statistics.total}
                            prefix={<DownloadOutlined />}
                            valueStyle={{color: token.colorPrimary}}
                        />
                    </Col>
                    <Col xs={24} sm={12} md={6}>
                        <Statistic
                            title="下载中"
                            value={statistics.downloading}
                            prefix={<SyncOutlined spin />}
                            valueStyle={{color: token.colorInfo}}
                        />
                    </Col>
                    <Col xs={24} sm={12} md={6}>
                        <Statistic
                            title="已完成"
                            value={statistics.completed}
                            prefix={<CheckCircleOutlined />}
                            valueStyle={{color: token.colorSuccess}}
                        />
                    </Col>
                    <Col xs={24} sm={12} md={6}>
                        <Statistic
                            title="失败"
                            value={statistics.failed}
                            prefix={<CloseCircleOutlined />}
                            valueStyle={{color: token.colorError}}
                        />
                    </Col>
                    <Col xs={24} sm={12} md={6}>
                        <Statistic
                            title="今日下载"
                            value={statistics.todayCount}
                            prefix={<CloudDownloadOutlined />}
                        />
                    </Col>
                    <Col xs={24} sm={12} md={6}>
                        <Statistic
                            title="总大小"
                            value={formatBytes(statistics.totalSize)}
                            prefix={<HddOutlined />}
                        />
                    </Col>
                </Row>
            </Card>

            {/* Filters and Actions */}
            <Card>
                <Space direction="vertical" style={{width: '100%'}} size="middle">
                    <Row gutter={[16, 16]} align="middle">
                        <Col xs={24} sm={12} md={8}>
                            <Input.Search
                                value={keyword}
                                onChange={(e) => setKeyword(e.target.value)}
                                placeholder="搜索下载名称或文件路径"
                                allowClear
                            />
                        </Col>
                        <Col xs={24} sm={12} md={6}>
                            <Select
                                style={{width: '100%'}}
                                value={statusFilter}
                                onChange={setStatusFilter}
                                placeholder="状态筛选"
                            >
                                <Select.Option value={DownloadStatus.ALL}>全部状态</Select.Option>
                                <Select.Option value={DownloadStatus.DOWNLOADING}>下载中</Select.Option>
                                <Select.Option value={DownloadStatus.COMPLETED}>已完成</Select.Option>
                                <Select.Option value={DownloadStatus.FAILED}>失败</Select.Option>
                            </Select>
                        </Col>
                        <Col xs={24} sm={12} md={8}>
                            <RangePicker
                                style={{width: '100%'}}
                                value={dateRange}
                                onChange={setDateRange}
                                placeholder={['开始日期', '结束日期']}
                            />
                        </Col>
                        <Col xs={24} sm={12} md={2}>
                            <Button
                                type={batchMode ? 'primary' : 'default'}
                                onClick={() => {
                                    setBatchMode(!batchMode);
                                    setSelectedHashes([]);
                                }}
                                block
                            >
                                {batchMode ? '取消' : '批量'}
                            </Button>
                        </Col>
                    </Row>

                    {batchMode && selectedHashes.length > 0 && (
                        <>
                            <Divider style={{margin: '8px 0'}} />
                            <Row gutter={[16, 16]} align="middle">
                                <Col>
                                    <Checkbox
                                        checked={selectedHashes.length === filteredData.length}
                                        indeterminate={selectedHashes.length > 0 && selectedHashes.length < filteredData.length}
                                        onChange={(e) => handleSelectAll(e.target.checked)}
                                    >
                                        全选 ({selectedHashes.length}/{filteredData.length})
                                    </Checkbox>
                                </Col>
                                <Col flex="auto" />
                                <Col>
                                    <Space>
                                        <Button
                                            type="primary"
                                            icon={<CheckCircleOutlined />}
                                            onClick={handleBatchComplete}
                                        >
                                            批量完成
                                        </Button>
                                        <Button
                                            danger
                                            icon={<DeleteOutlined />}
                                            onClick={handleBatchDelete}
                                        >
                                            批量删除
                                        </Button>
                                    </Space>
                                </Col>
                            </Row>
                        </>
                    )}
                </Space>
            </Card>

            {/* Download List */}
            <Card title="下载列表" loading={loading}>
                {filteredData.length > 0 ? (
                    <Collapse items={items} ghost={true} />
                ) : (
                    <Empty
                        description={
                            data.length === 0 ? (
                                <span>
                                    无完成下载，<Link to="/setting/download">配置下载</Link>
                                </span>
                            ) : (
                                '没有符合条件的下载'
                            )
                        }
                    />
                )}
            </Card>

            {/* Video Detail Modal */}
            <VideoDetail
                title="下载整理"
                mode="download"
                width={1100}
                path={selected}
                open={!!selected}
                onCancel={() => setSelected(undefined)}
                onOk={() => {
                    setSelected(undefined);
                    refresh();
                }}
            />
        </Space>
    );
}
