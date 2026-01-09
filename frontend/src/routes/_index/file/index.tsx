import {
    Button,
    Card,
    Empty,
    Input,
    Space,
    Table,
    Tag,
    theme,
    Tooltip,
    Select,
    Statistic,
    Row,
    Col,
    Dropdown,
    message,
    Modal
} from "antd";
import {useDebounce, useRequest} from "ahooks";
import * as api from "../../../apis/file.ts";
import React, {useMemo, useState, useCallback} from "react";
import {
    FolderViewOutlined,
    DeleteOutlined,
    FileOutlined,
    VideoCameraOutlined,
    FileTextOutlined,
    CheckCircleOutlined,
    ClockCircleOutlined,
    FilterOutlined,
    MoreOutlined,
    FolderOpenOutlined,
    FileImageOutlined
} from "@ant-design/icons";
import IconButton from "../../../components/IconButton";
import {createFileRoute, Link} from "@tanstack/react-router";
import VideoDetail from "../../../components/VideoDetail";
import BatchModal from "./-components/batchModal.tsx";
import type {TableColumnsType, TableProps} from 'antd';

const {useToken} = theme;

export const Route = createFileRoute('/_index/file/')({
    component: File
});

// File type definitions
interface FileItem {
    name: string;
    path: string;
    size: string;
    fullPath: string;
    type?: 'video' | 'subtitle' | 'other';
    modifiedTime?: string;
    isOrganized?: boolean;
    sizeBytes?: number;
}

type SortField = 'name' | 'size' | 'type' | 'modifiedTime';
type SortOrder = 'ascend' | 'descend' | null;

// File type detection
function getFileType(filename: string): 'video' | 'subtitle' | 'other' {
    const ext = filename.split('.').pop()?.toLowerCase() || '';
    const videoExts = ['mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm', 'rmvb', 'rm', 'ts'];
    const subtitleExts = ['srt', 'ass', 'ssa', 'sub', 'vtt'];

    if (videoExts.includes(ext)) return 'video';
    if (subtitleExts.includes(ext)) return 'subtitle';
    return 'other';
}

// File type icon
function getFileIcon(type: string) {
    switch (type) {
        case 'video':
            return <VideoCameraOutlined style={{fontSize: 18, color: '#1890ff'}}/>;
        case 'subtitle':
            return <FileTextOutlined style={{fontSize: 18, color: '#52c41a'}}/>;
        default:
            return <FileOutlined style={{fontSize: 18, color: '#8c8c8c'}}/>;
    }
}

// Parse size string to bytes for sorting
function parseSizeToBytes(sizeStr: string): number {
    if (!sizeStr) return 0;
    const units: {[key: string]: number} = {
        'B': 1,
        'KB': 1000,
        'MB': 1000000,
        'GB': 1000000000,
        'TB': 1000000000000
    };
    const match = sizeStr.match(/^([\d.]+)\s*([A-Z]+)$/);
    if (!match) return 0;
    const value = parseFloat(match[1]);
    const unit = match[2];
    return value * (units[unit] || 1);
}

function File() {
    const {token} = useToken();
    const {data = [], loading, refresh} = useRequest(api.getFiles);
    const [selectedVideo, setSelectedVideo] = useState<string | undefined>();
    const [keyword, setKeyword] = useState<string>('');
    const keywordDebounce = useDebounce(keyword, {wait: 300});

    const [batchModalOpen, setBatchModalOpen] = useState(false);
    const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);

    // Filters
    const [typeFilter, setTypeFilter] = useState<string>('all');
    const [statusFilter, setStatusFilter] = useState<string>('all');
    const [sizeFilter, setSizeFilter] = useState<string>('all');

    // Sorting
    const [sortField, setSortField] = useState<SortField>('name');
    const [sortOrder, setSortOrder] = useState<SortOrder>('ascend');

    // Process data with type detection and enhanced info
    const processedData: FileItem[] = useMemo(() => {
        return data.map((item: any) => {
            const fullPath = `${item.path}/${item.name}`;
            const type = getFileType(item.name);
            const sizeBytes = parseSizeToBytes(item.size);

            return {
                ...item,
                fullPath,
                type,
                sizeBytes,
                isOrganized: false, // TODO: Get from API if available
                modifiedTime: item.modifiedTime || new Date().toISOString()
            };
        });
    }, [data]);

    // Apply filters
    const filteredData = useMemo(() => {
        return processedData.filter((item: FileItem) => {
            // Keyword search
            if (keywordDebounce &&
                !item.name.toLowerCase().includes(keywordDebounce.toLowerCase()) &&
                !item.path.toLowerCase().includes(keywordDebounce.toLowerCase())) {
                return false;
            }

            // Type filter
            if (typeFilter !== 'all' && item.type !== typeFilter) {
                return false;
            }

            // Status filter
            if (statusFilter === 'organized' && !item.isOrganized) {
                return false;
            }
            if (statusFilter === 'unorganized' && item.isOrganized) {
                return false;
            }

            // Size filter
            if (sizeFilter !== 'all') {
                const bytes = item.sizeBytes || 0;
                if (sizeFilter === 'small' && bytes >= 100000000) return false;
                if (sizeFilter === 'medium' && (bytes < 100000000 || bytes >= 1000000000)) return false;
                if (sizeFilter === 'large' && bytes < 1000000000) return false;
            }

            return true;
        });
    }, [processedData, keywordDebounce, typeFilter, statusFilter, sizeFilter]);

    // Apply sorting
    const sortedData = useMemo(() => {
        if (!sortOrder) return filteredData;

        return [...filteredData].sort((a, b) => {
            let compareResult = 0;

            switch (sortField) {
                case 'name':
                    compareResult = a.name.localeCompare(b.name);
                    break;
                case 'size':
                    compareResult = (a.sizeBytes || 0) - (b.sizeBytes || 0);
                    break;
                case 'type':
                    compareResult = (a.type || '').localeCompare(b.type || '');
                    break;
                case 'modifiedTime':
                    compareResult = new Date(a.modifiedTime || 0).getTime() - new Date(b.modifiedTime || 0).getTime();
                    break;
            }

            return sortOrder === 'ascend' ? compareResult : -compareResult;
        });
    }, [filteredData, sortField, sortOrder]);

    // Statistics
    const statistics = useMemo(() => {
        const total = processedData.length;
        const organized = processedData.filter(item => item.isOrganized).length;
        const unorganized = total - organized;
        const totalSize = processedData.reduce((sum, item) => sum + (item.sizeBytes || 0), 0);

        return {
            total,
            organized,
            unorganized,
            totalSize: formatBytes(totalSize)
        };
    }, [processedData]);

    // Format bytes
    const formatBytes = (bytes: number): string => {
        if (bytes === 0) return '0 B';
        const k = 1000;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i];
    };

    // Row selection
    const rowSelection = {
        selectedRowKeys,
        onChange: (newSelectedRowKeys: React.Key[]) => {
            setSelectedRowKeys(newSelectedRowKeys);
        },
        selections: [
            Table.SELECTION_ALL,
            Table.SELECTION_INVERT,
            Table.SELECTION_NONE,
        ],
    };

    // Table change handler
    const handleTableChange: TableProps<FileItem>['onChange'] = (pagination, filters, sorter: any) => {
        if (sorter.field) {
            setSortField(sorter.field as SortField);
            setSortOrder(sorter.order);
        }
    };

    // Batch organize
    const handleBatchOrganize = useCallback(() => {
        if (selectedRowKeys.length === 0) {
            message.warning('请先选择文件');
            return;
        }
        setBatchModalOpen(true);
    }, [selectedRowKeys]);

    // Batch delete
    const handleBatchDelete = useCallback(() => {
        if (selectedRowKeys.length === 0) {
            message.warning('请先选择文件');
            return;
        }

        Modal.confirm({
            title: '确认删除',
            content: `确定要删除选中的 ${selectedRowKeys.length} 个文件吗？`,
            okText: '确认',
            cancelText: '取消',
            okType: 'danger',
            onOk: () => {
                message.success('删除功能待实现');
                setSelectedRowKeys([]);
            }
        });
    }, [selectedRowKeys]);

    // Context menu actions
    const getRowContextMenu = (record: FileItem) => ({
        items: [
            {
                key: 'organize',
                label: '整理',
                icon: <FolderViewOutlined/>,
                onClick: () => setSelectedVideo(record.fullPath)
            },
            {
                key: 'open',
                label: '打开所在文件夹',
                icon: <FolderOpenOutlined/>,
                onClick: () => message.info('打开文件夹功能待实现')
            },
            {
                type: 'divider' as const
            },
            {
                key: 'delete',
                label: '删除',
                icon: <DeleteOutlined/>,
                danger: true,
                onClick: () => {
                    Modal.confirm({
                        title: '确认删除',
                        content: `确定要删除文件 "${record.name}" 吗？`,
                        okText: '确认',
                        cancelText: '取消',
                        okType: 'danger',
                        onOk: () => message.success('删除功能待实现')
                    });
                }
            }
        ]
    });

    // Table columns
    const columns: TableColumnsType<FileItem> = [
        {
            title: '文件名',
            dataIndex: 'name',
            key: 'name',
            sorter: true,
            sortOrder: sortField === 'name' ? sortOrder : null,
            ellipsis: {showTitle: false},
            render: (name: string, record: FileItem) => (
                <Space size={8}>
                    {getFileIcon(record.type || 'other')}
                    <Tooltip title={name}>
                        <span style={{cursor: 'pointer'}} onDoubleClick={() => setSelectedVideo(record.fullPath)}>
                            {name}
                        </span>
                    </Tooltip>
                    {record.isOrganized && (
                        <CheckCircleOutlined style={{color: '#52c41a'}}/>
                    )}
                </Space>
            ),
        },
        {
            title: '大小',
            dataIndex: 'size',
            key: 'size',
            width: 120,
            sorter: true,
            sortOrder: sortField === 'size' ? sortOrder : null,
            render: (size: string) => <Tag color="blue">{size}</Tag>
        },
        {
            title: '类型',
            dataIndex: 'type',
            key: 'type',
            width: 100,
            sorter: true,
            sortOrder: sortField === 'type' ? sortOrder : null,
            render: (type: string) => {
                const typeMap: {[key: string]: {text: string, color: string}} = {
                    video: {text: '视频', color: 'blue'},
                    subtitle: {text: '字幕', color: 'green'},
                    other: {text: '其他', color: 'default'}
                };
                const typeInfo = typeMap[type] || typeMap.other;
                return <Tag color={typeInfo.color}>{typeInfo.text}</Tag>;
            }
        },
        {
            title: '修改时间',
            dataIndex: 'modifiedTime',
            key: 'modifiedTime',
            width: 180,
            sorter: true,
            sortOrder: sortField === 'modifiedTime' ? sortOrder : null,
            render: (time: string) => time ? new Date(time).toLocaleString('zh-CN') : '-'
        },
        {
            title: '状态',
            dataIndex: 'isOrganized',
            key: 'isOrganized',
            width: 100,
            render: (isOrganized: boolean) => (
                isOrganized ? (
                    <Tag icon={<CheckCircleOutlined/>} color="success">已整理</Tag>
                ) : (
                    <Tag icon={<ClockCircleOutlined/>} color="default">未整理</Tag>
                )
            )
        },
        {
            title: '路径',
            dataIndex: 'path',
            key: 'path',
            ellipsis: {showTitle: false},
            render: (path: string) => (
                <Tooltip title={path}>
                    <span style={{color: token.colorTextSecondary}}>{path}</span>
                </Tooltip>
            )
        },
        {
            title: '操作',
            key: 'action',
            width: 100,
            fixed: 'right',
            render: (_, record: FileItem) => (
                <Space size="small">
                    <Tooltip title="整理">
                        <IconButton onClick={() => setSelectedVideo(record.fullPath)}>
                            <FolderViewOutlined style={{fontSize: token.sizeLG}}/>
                        </IconButton>
                    </Tooltip>
                    <Dropdown menu={getRowContextMenu(record)} trigger={['click']}>
                        <IconButton>
                            <MoreOutlined style={{fontSize: token.sizeLG}}/>
                        </IconButton>
                    </Dropdown>
                </Space>
            ),
        },
    ];

    // Clear filters
    const clearFilters = () => {
        setTypeFilter('all');
        setStatusFilter('all');
        setSizeFilter('all');
        setKeyword('');
    };

    const hasActiveFilters = typeFilter !== 'all' || statusFilter !== 'all' || sizeFilter !== 'all' || keyword !== '';

    return (
        <div>
            {/* Statistics Cards */}
            <Row gutter={16} style={{marginBottom: 16}}>
                <Col xs={24} sm={12} md={6}>
                    <Card>
                        <Statistic
                            title="总文件数"
                            value={statistics.total}
                            prefix={<FileOutlined/>}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={12} md={6}>
                    <Card>
                        <Statistic
                            title="已整理"
                            value={statistics.organized}
                            valueStyle={{color: '#3f8600'}}
                            prefix={<CheckCircleOutlined/>}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={12} md={6}>
                    <Card>
                        <Statistic
                            title="未整理"
                            value={statistics.unorganized}
                            valueStyle={{color: '#cf1322'}}
                            prefix={<ClockCircleOutlined/>}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={12} md={6}>
                    <Card>
                        <Statistic
                            title="总大小"
                            value={statistics.totalSize}
                            prefix={<FileImageOutlined/>}
                        />
                    </Card>
                </Col>
            </Row>

            {/* Main Table Card */}
            <Card
                title={
                    <Space>
                        <span>文件列表</span>
                        {selectedRowKeys.length > 0 && (
                            <Tag color="blue">已选择 {selectedRowKeys.length} 项</Tag>
                        )}
                    </Space>
                }
                loading={loading}
                extra={
                    <Space wrap>
                        {/* Search */}
                        <Input.Search
                            placeholder="搜索文件名或路径"
                            value={keyword}
                            onChange={e => setKeyword(e.target.value)}
                            style={{width: 200}}
                            allowClear
                        />

                        {/* Filters */}
                        <Select
                            value={typeFilter}
                            onChange={setTypeFilter}
                            style={{width: 120}}
                            suffixIcon={<FilterOutlined/>}
                        >
                            <Select.Option value="all">全部类型</Select.Option>
                            <Select.Option value="video">视频</Select.Option>
                            <Select.Option value="subtitle">字幕</Select.Option>
                            <Select.Option value="other">其他</Select.Option>
                        </Select>

                        <Select
                            value={statusFilter}
                            onChange={setStatusFilter}
                            style={{width: 120}}
                        >
                            <Select.Option value="all">全部状态</Select.Option>
                            <Select.Option value="organized">已整理</Select.Option>
                            <Select.Option value="unorganized">未整理</Select.Option>
                        </Select>

                        <Select
                            value={sizeFilter}
                            onChange={setSizeFilter}
                            style={{width: 120}}
                        >
                            <Select.Option value="all">全部大小</Select.Option>
                            <Select.Option value="small">&lt; 100MB</Select.Option>
                            <Select.Option value="medium">100MB - 1GB</Select.Option>
                            <Select.Option value="large">&gt; 1GB</Select.Option>
                        </Select>

                        {hasActiveFilters && (
                            <Button onClick={clearFilters}>清除筛选</Button>
                        )}

                        {/* Batch Actions */}
                        {selectedRowKeys.length > 0 && (
                            <>
                                <Button type="primary" onClick={handleBatchOrganize}>
                                    批量整理
                                </Button>
                                <Button danger onClick={handleBatchDelete}>
                                    批量删除
                                </Button>
                            </>
                        )}
                    </Space>
                }
            >
                {sortedData.length > 0 ? (
                    <Table<FileItem>
                        rowKey="fullPath"
                        columns={columns}
                        dataSource={sortedData}
                        rowSelection={rowSelection}
                        onChange={handleTableChange}
                        pagination={{
                            showSizeChanger: true,
                            showQuickJumper: true,
                            showTotal: (total) => `共 ${total} 条`,
                            defaultPageSize: 20,
                            pageSizeOptions: ['10', '20', '50', '100']
                        }}
                        scroll={{x: 1200}}
                        size="middle"
                        rowClassName={(record, index) =>
                            index % 2 === 0 ? 'table-row-light' : 'table-row-dark'
                        }
                        onRow={(record) => ({
                            onDoubleClick: () => setSelectedVideo(record.fullPath),
                            onContextMenu: (e) => {
                                e.preventDefault();
                            }
                        })}
                    />
                ) : (
                    <Empty
                        description={
                            hasActiveFilters ? (
                                <span>
                                    无匹配文件，<Button type="link" onClick={clearFilters}>清除筛选</Button>
                                </span>
                            ) : (
                                <span>
                                    无文件，<Link to={'/setting/file'}>配置文件</Link>
                                </span>
                            )
                        }
                    />
                )}
            </Card>

            {/* Video Detail Modal */}
            <VideoDetail
                title="文件整理"
                mode="file"
                width={1100}
                path={selectedVideo}
                open={!!selectedVideo}
                onCancel={() => setSelectedVideo(undefined)}
                onOk={() => {
                    setSelectedVideo(undefined);
                    refresh();
                }}
            />

            {/* Batch Modal */}
            <BatchModal
                open={batchModalOpen}
                onCancel={() => {
                    setBatchModalOpen(false);
                    setSelectedRowKeys([]);
                    refresh();
                }}
                files={selectedRowKeys as string[]}
            />

            {/* Custom Styles */}
            <style>{`
                .table-row-light {
                    background-color: #ffffff;
                }
                .table-row-dark {
                    background-color: #fafafa;
                }
                .ant-table-row:hover {
                    background-color: #e6f7ff !important;
                }
                .ant-table-row-selected {
                    background-color: #bae7ff !important;
                }
                .ant-table-row-selected:hover {
                    background-color: #91d5ff !important;
                }
            `}</style>
        </div>
    );
}
