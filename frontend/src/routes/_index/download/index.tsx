import { Card, Collapse, Empty, Input, List, message, Modal, Space, Tag, theme, Tooltip, Progress, Switch, Row, Col, Select, DatePicker, Divider, Button, Badge, Statistic } from "antd";
import * as api from "../../../apis/download";
import { useDebounce, useRequest } from "ahooks";
import { FileDoneOutlined, FolderViewOutlined, UserOutlined, FilterOutlined, ReloadOutlined, DeleteOutlined, PauseOutlined, PlayCircleOutlined, FileOutlined, SettingOutlined, CheckCircleOutlined, CloseCircleOutlined } from "@ant-design/icons";
import React, { useMemo, useState } from "react";
import IconButton from "../../../components/IconButton";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import VideoDetail from "../../../components/VideoDetail";

const { useToken } = theme

export const Route = createFileRoute('/_index/download/')({
    component: Download,
})

function Download() {

    const { token } = useToken()
    const navigate = useNavigate()
    const [selected, setSelected] = useState<string | undefined>()
    const [keyword, setKeyword] = useState<string>()
    const keywordDebounce = useDebounce(keyword, { wait: 1000 })
    const [includeSuccess, setIncludeSuccess] = useState(true)
    const [includeFailed, setIncludeFailed] = useState(true)
    const [showAdvancedFilters, setShowAdvancedFilters] = useState(false)
    const [advancedFilters, setAdvancedFilters] = useState({
        status: 'all', // all, downloading, completed, failed
        sizeRange: [0, 10000],
        dateRange: null as any,
        sortBy: 'date',
        sortOrder: 'desc'
    })
    const [downloadStats, setDownloadStats] = useState({
        total: 0,
        downloading: 0,
        completed: 0,
        failed: 0,
        totalSize: '0 GB'
    })
    const [fileManageVisible, setFileManageVisible] = useState(false)
    const [currentTorrentHash, setCurrentTorrentHash] = useState<string>('')
    const [torrentFiles, setTorrentFiles] = useState<any[]>([])
    const [selectedFileIndices, setSelectedFileIndices] = useState<number[]>([])
    const [fileManageLoading, setFileManageLoading] = useState(false)
    
    const { data = [], loading, refresh } = useRequest(
        () => api.getDownloads({
            include_success: includeSuccess,
            include_failed: includeFailed
        }),
        {
            refreshDeps: [includeSuccess, includeFailed]
        }
    )

    const realData = useMemo(() => {
        let filteredData = data.filter((item: any) => {
            // 首先根据关键词筛选
            const matchKeyword = !keywordDebounce ||
                item.name.indexOf(keywordDebounce) != -1 ||
                item.files.some((sub: any) => (
                    sub.name.indexOf(keywordDebounce) != -1 ||
                    sub.path.indexOf(keywordDebounce) != -1
                ));

            if (!matchKeyword) return false;

            // 然后根据完成状态筛选
            const hasCompleted = item.files.some((file: any) => file.progress >= 1);
            const hasFailed = item.files.some((file: any) => file.progress === 0);

            // 如果不显示已完成，则过滤掉全部完成的任务
            if (!includeSuccess && hasCompleted && !item.files.some((file: any) => file.progress < 1)) {
                return false;
            }

            // 如果不显示失败，则过滤掉有失败文件的任务
            if (!includeFailed && hasFailed) {
                return false;
            }

            return true;
        });

        // 高级过滤
        if (showAdvancedFilters) {
            filteredData = filteredData.filter((item: any) => {
                // 状态过滤
                if (advancedFilters.status !== 'all') {
                    const hasCompleted = item.files.some((file: any) => file.progress >= 1);
                    const hasDownloading = item.files.some((file: any) => file.progress > 0 && file.progress < 1);
                    
                    if (advancedFilters.status === 'completed' && !hasCompleted) return false;
                    if (advancedFilters.status === 'downloading' && !hasDownloading) return false;
                }

                return true;
            });
        }

        return filteredData;
    }, [data, keywordDebounce, showAdvancedFilters, advancedFilters, includeSuccess, includeFailed])

    const { run: onComplete } = useRequest(api.completeDownload, {
        manual: true,
        onSuccess: () => {
            message.success("标记成功")
            refresh()
        }
    })

    // 跳转到视频详情页面
    const handleVideoClick = (num: string) => {
        if (num) {
            // 从URL中获取当前的search参数
            const urlParams = new URLSearchParams(window.location.search);
            const source = urlParams.get('source') || 'javdb'; // 默认使用javdb作为源
            const url = urlParams.get('url') || ''; // URL可能为空

            navigate({
                to: `/video/${num}`,
                search: {
                    source: source,
                    url: url
                }
            });
        } else {
            message.info("无法识别番号，无法跳转到详情页面");
        }
    };

    // 跳转到演员页面
    const handleActorClick = (actorName: string) => {
        navigate({
            to: '/actor',
            search: { actorName }
        });
    };

    // 打开文件管理 Modal
    const handleManageFiles = async (torrentHash: string) => {
        setCurrentTorrentHash(torrentHash)
        setFileManageVisible(true)
        setFileManageLoading(true)
        try {
            const files = await api.getTorrentFiles(torrentHash)
            setTorrentFiles(files)
        } catch (error) {
            message.error('获取文件列表失败')
        } finally {
            setFileManageLoading(false)
        }
    }

    // 设置文件优先级
    const handleSetPriority = async (priority: number) => {
        if (selectedFileIndices.length === 0) {
            message.warning('请先选择文件')
            return
        }
        
        try {
            await api.setFilesPriority({
                torrent_hash: currentTorrentHash,
                file_indices: selectedFileIndices,
                priority
            })
            message.success('优先级设置成功')
            // 刷新文件列表
            const files = await api.getTorrentFiles(currentTorrentHash)
            setTorrentFiles(files)
            setSelectedFileIndices([])
        } catch (error) {
            message.error('设置优先级失败')
        }
    }

    // 应用过滤规则
    const handleApplyFilter = async (torrentHash: string) => {
        try {
            const result = await api.applyFilterToTorrent(torrentHash)
            if (result.code === 200) {
                message.success(result.message || '过滤规则应用成功')
                refresh()
            } else {
                message.error(result.message || '应用过滤规则失败')
            }
        } catch (error) {
            message.error('应用过滤规则失败')
        }
    }

    // 暂停种子
    const handlePauseTorrent = async (torrentHash: string) => {
        try {
            await api.pauseTorrent(torrentHash)
            message.success('已暂停下载')
            refresh()
        } catch (error) {
            message.error('暂停失败')
        }
    }

    // 恢复种子
    const handleResumeTorrent = async (torrentHash: string) => {
        try {
            await api.resumeTorrent(torrentHash)
            message.success('已恢复下载')
            refresh()
        } catch (error) {
            message.error('恢复失败')
        }
    }

    // 删除种子
    const handleDeleteTorrent = async (torrentHash: string, deleteFiles: boolean) => {
        try {
            await api.deleteTorrent(torrentHash, deleteFiles)
            message.success('删除成功')
            refresh()
        } catch (error) {
            message.error('删除失败')
        }
    }

    const items = realData.map((torrent: any) => (
        {
            key: torrent.hash,
            label: (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                    <span>{torrent.name}</span>
                    <Space>
                        {(() => {
                            const totalFiles = torrent.files.length;
                            const completedFiles = torrent.files.filter((f: any) => f.progress >= 1).length;
                            const downloadingFiles = torrent.files.filter((f: any) => f.progress > 0 && f.progress < 1).length;
                            const avgProgress = torrent.files.reduce((sum: number, f: any) => sum + f.progress, 0) / totalFiles;
                            
                            return (
                                <>
                                    <Tag color={completedFiles === totalFiles ? 'success' : downloadingFiles > 0 ? 'processing' : 'default'}>
                                        {completedFiles}/{totalFiles} 文件
                                    </Tag>
                                    <Progress 
                                        percent={Math.round(avgProgress * 100)} 
                                        size="small" 
                                        style={{ width: 80 }}
                                        strokeColor={completedFiles === totalFiles ? '#52c41a' : '#1890ff'}
                                    />
                                </>
                            );
                        })()}
                    </Space>
                </div>
            ),
            children: (
                <List itemLayout="horizontal"
                    dataSource={torrent.files}
                    renderItem={(item: any, index) => (
                        <List.Item actions={[
                            <Tooltip title={'整理'}>
                                <IconButton onClick={() => {
                                    setSelected(item.path)
                                }}>
                                    <FolderViewOutlined style={{ fontSize: token.sizeLG }} />
                                </IconButton>
                            </Tooltip>
                        ]}>
                            <List.Item.Meta
                                title={(
                                    <span>
                                        {item.num ? (
                                            <a onClick={() => handleVideoClick(item.num)}>
                                                {item.name}
                                            </a>
                                        ) : (
                                            item.name
                                        )}
                                        <Tag style={{ marginLeft: 5 }} color='success'>{item.size}</Tag>
                                        {item.progress < 1 && (
                                            <Progress
                                                percent={Math.round(item.progress * 100)}
                                                size="small"
                                                style={{ width: 100, marginLeft: 10, display: 'inline-block' }}
                                            />
                                        )}
                                    </span>
                                )}
                                description={(
                                    <div>
                                        <div>{item.path}</div>
                                        {item.actors && item.actors.length > 0 && (
                                            <div style={{ marginTop: 5 }}>
                                                <UserOutlined style={{ marginRight: 5 }} />
                                                {item.actors.map((actor: string, idx: number) => (
                                                    <React.Fragment key={actor}>
                                                        <a onClick={() => handleActorClick(actor)}>{actor}</a>
                                                        {idx < item.actors.length - 1 && <span>, </span>}
                                                    </React.Fragment>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                )}
                            />
                        </List.Item>
                    )}
                />
            ),
            extra: (
                <Space>
                    <Tooltip title={'管理文件'}>
                        <IconButton onClick={() => handleManageFiles(torrent.hash)}>
                            <FileOutlined style={{ fontSize: token.sizeLG, color: '#722ed1' }} />
                        </IconButton>
                    </Tooltip>
                    <Tooltip title={'应用过滤规则'}>
                        <IconButton onClick={() => handleApplyFilter(torrent.hash)}>
                            <FilterOutlined style={{ fontSize: token.sizeLG, color: '#13c2c2' }} />
                        </IconButton>
                    </Tooltip>
                    <Tooltip title={'恢复下载'}>
                        <IconButton onClick={() => handleResumeTorrent(torrent.hash)}>
                            <PlayCircleOutlined style={{ fontSize: token.sizeLG, color: '#1890ff' }} />
                        </IconButton>
                    </Tooltip>
                    <Tooltip title={'暂停下载'}>
                        <IconButton onClick={() => handlePauseTorrent(torrent.hash)}>
                            <PauseOutlined style={{ fontSize: token.sizeLG, color: '#faad14' }} />
                        </IconButton>
                    </Tooltip>
                    <Tooltip title={'标记为"整理成功"'}>
                        <IconButton onClick={() => {
                            Modal.confirm({
                                title: '是否确认标记为完成',
                                onOk: () => onComplete(torrent.hash)
                            })
                        }}>
                            <FileDoneOutlined style={{ fontSize: token.sizeLG, color: '#52c41a' }} />
                        </IconButton>
                    </Tooltip>
                    <Tooltip title={'删除任务'}>
                        <IconButton onClick={() => {
                            Modal.confirm({
                                title: '确认删除下载任务？',
                                content: (
                                    <div>
                                        <p>请选择删除方式：</p>
                                        <p>• 只删除任务：仅从下载器移除，保留已下载文件</p>
                                        <p>• 删除任务和文件：同时删除任务和已下载的文件</p>
                                    </div>
                                ),
                                okText: '只删除任务',
                                cancelText: '取消',
                                onOk: () => handleDeleteTorrent(torrent.hash, false),
                                footer: (_, { OkBtn, CancelBtn }) => (
                                    <>
                                        <CancelBtn />
                                        <OkBtn />
                                        <Button 
                                            danger 
                                            type="primary"
                                            onClick={() => {
                                                Modal.destroyAll()
                                                handleDeleteTorrent(torrent.hash, true)
                                            }}
                                        >
                                            删除任务和文件
                                        </Button>
                                    </>
                                ),
                            })
                        }}>
                            <DeleteOutlined style={{ fontSize: token.sizeLG, color: '#ff4d4f' }} />
                        </IconButton>
                    </Tooltip>
                </Space>
            )
        }
    ))

    return (
        <Card 
            title={
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span>下载列表</span>
                    <Space>
                        <Button
                            icon={<FilterOutlined />}
                            size="small"
                            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                        >
                            高级筛选 {showAdvancedFilters ? '▼' : '▶'}
                        </Button>
                        <Button
                            icon={<ReloadOutlined />}
                            size="small"
                            onClick={refresh}
                            loading={loading}
                        >
                            刷新
                        </Button>
                    </Space>
                </div>
            }
            loading={loading}
            extra={<Input.Search value={keyword} onChange={e => setKeyword(e.target.value)} placeholder={'搜索'} />}>
            
            {/* 统计信息 */}
            <Row gutter={16} style={{ marginBottom: 16 }}>
                <Col span={6}>
                    <Statistic title="总任务数" value={data.length} />
                </Col>
                <Col span={6}>
                    <Statistic 
                        title="进行中" 
                        value={data.reduce((count: number, item: any) => 
                            count + item.files.filter((f: any) => f.progress > 0 && f.progress < 1).length, 0
                        )} 
                        valueStyle={{ color: '#1890ff' }}
                    />
                </Col>
                <Col span={6}>
                    <Statistic 
                        title="已完成" 
                        value={data.reduce((count: number, item: any) => 
                            count + item.files.filter((f: any) => f.progress >= 1).length, 0
                        )} 
                        valueStyle={{ color: '#52c41a' }}
                    />
                </Col>
                <Col span={6}>
                    <Statistic 
                        title="失败/等待" 
                        value={data.reduce((count: number, item: any) => 
                            count + item.files.filter((f: any) => f.progress === 0).length, 0
                        )} 
                        valueStyle={{ color: '#ff4d4f' }}
                    />
                </Col>
            </Row>

            <Divider />

            {/* 基础过滤选项 */}
            <div style={{ marginBottom: 16 }}>
                <Row gutter={16}>
                    <Col>
                        <Space>
                            <span>显示已完成:</span>
                            <Switch 
                                checked={includeSuccess} 
                                onChange={setIncludeSuccess}
                                size="small"
                            />
                        </Space>
                    </Col>
                    <Col>
                        <Space>
                            <span>显示失败:</span>
                            <Switch 
                                checked={includeFailed} 
                                onChange={setIncludeFailed}
                                size="small"
                            />
                        </Space>
                    </Col>
                </Row>
            </div>

            {/* 高级过滤选项 */}
            {showAdvancedFilters && (
                <Card size="small" style={{ marginBottom: 16 }}>
                    <Row gutter={[16, 8]}>
                        <Col span={8}>
                            <div style={{ marginBottom: 8 }}>状态筛选</div>
                            <Select
                                value={advancedFilters.status}
                                onChange={(value) => setAdvancedFilters({
                                    ...advancedFilters,
                                    status: value
                                })}
                                style={{ width: '100%' }}
                            >
                                <Select.Option value="all">全部状态</Select.Option>
                                <Select.Option value="downloading">下载中</Select.Option>
                                <Select.Option value="completed">已完成</Select.Option>
                                <Select.Option value="failed">失败/等待</Select.Option>
                            </Select>
                        </Col>
                        <Col span={8}>
                            <div style={{ marginBottom: 8 }}>排序方式</div>
                            <Select
                                value={`${advancedFilters.sortBy}-${advancedFilters.sortOrder}`}
                                onChange={(value) => {
                                    const [sortBy, sortOrder] = value.split('-');
                                    setAdvancedFilters({
                                        ...advancedFilters,
                                        sortBy,
                                        sortOrder
                                    });
                                }}
                                style={{ width: '100%' }}
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
                            <div style={{ marginBottom: 8 }}>快速操作</div>
                            <Space>
                                <Button 
                                    size="small" 
                                    onClick={() => {
                                        setAdvancedFilters({
                                            status: 'all',
                                            sizeRange: [0, 10000],
                                            dateRange: null,
                                            sortBy: 'date',
                                            sortOrder: 'desc'
                                        });
                                        setKeyword('');
                                    }}
                                >
                                    重置筛选
                                </Button>
                            </Space>
                        </Col>
                    </Row>
                </Card>
            )}
            
            {realData.length > 0 ? (
                <>
                    {realData.length !== data.length && (
                        <div style={{ marginBottom: 16, padding: '8px 12px', background: '#f0f2f5', borderRadius: 4 }}>
                            <Space>
                                <Badge count={realData.length} style={{ backgroundColor: '#1890ff' }} />
                                <span>筛选结果：{realData.length} / {data.length} 个任务</span>
                            </Space>
                        </div>
                    )}
                    <Collapse items={items} ghost={true} />
                </>
            ) : data.length > 0 ? (
                <Empty description="没有符合筛选条件的下载任务" />
            ) : (
                <Empty description={(<span>无下载任务，<Link to={'/setting/download'}>配置下载</Link></span>)} />
            )}
            <VideoDetail title={'下载整理'}
                mode={'download'}
                width={1100}
                path={selected}
                open={!!selected}
                onCancel={() => setSelected(undefined)}
                onOk={() => {
                    setSelected(undefined)
                    refresh()
                }}
            />
        </Card>
    )
}

// 文件管理 Modal
const FileManageModal = () => {
    const priorityNames = {
        0: '不下载',
        1: '正常',
        6: '高',
        7: '最高'
    }

    const priorityColors: any = {
        0: 'default',
        1: 'blue',
        6: 'orange',
        7: 'red'
    }

    return (
        <Modal
            title="种子文件管理"
            open={fileManageVisible}
            onCancel={() => {
                setFileManageVisible(false)
                setSelectedFileIndices([])
            }}
            width={1000}
            footer={[
                <Button key="close" onClick={() => {
                    setFileManageVisible(false)
                    setSelectedFileIndices([])
                }}>
                    关闭
                </Button>
            ]}
        >
            <div style={{ marginBottom: 16 }}>
                <Space>
                    <span>批量设置优先级：</span>
                    <Button 
                        size="small" 
                        disabled={selectedFileIndices.length === 0}
                        onClick={() => handleSetPriority(7)}
                    >
                        最高
                    </Button>
                    <Button 
                        size="small" 
                        disabled={selectedFileIndices.length === 0}
                        onClick={() => handleSetPriority(6)}
                    >
                        高
                    </Button>
                    <Button 
                        size="small" 
                        disabled={selectedFileIndices.length === 0}
                        onClick={() => handleSetPriority(1)}
                    >
                        正常
                    </Button>
                    <Button 
                        size="small" 
                        danger
                        disabled={selectedFileIndices.length === 0}
                        onClick={() => handleSetPriority(0)}
                    >
                        不下载
                    </Button>
                    <Divider type="vertical" />
                    <span style={{ color: '#999' }}>
                        已选择 {selectedFileIndices.length} 个文件
                    </span>
                </Space>
            </div>

            <List
                loading={fileManageLoading}
                dataSource={torrentFiles}
                renderItem={(file: any) => (
                    <List.Item
                        actions={[
                            <Select
                                value={file.priority}
                                size="small"
                                style={{ width: 100 }}
                                onChange={(value) => {
                                    handleSetPriority(value)
                                    setSelectedFileIndices([file.index])
                                }}
                            >
                                <Select.Option value={7}>最高</Select.Option>
                                <Select.Option value={6}>高</Select.Option>
                                <Select.Option value={1}>正常</Select.Option>
                                <Select.Option value={0}>不下载</Select.Option>
                            </Select>
                        ]}
                    >
                        <List.Item.Meta
                            avatar={
                                <input
                                    type="checkbox"
                                    checked={selectedFileIndices.includes(file.index)}
                                    onChange={(e) => {
                                        if (e.target.checked) {
                                            setSelectedFileIndices([...selectedFileIndices, file.index])
                                        } else {
                                            setSelectedFileIndices(selectedFileIndices.filter(i => i !== file.index))
                                        }
                                    }}
                                    style={{ width: 16, height: 16, cursor: 'pointer' }}
                                />
                            }
                            title={
                                <div>
                                    <span>{file.name}</span>
                                    <Tag 
                                        style={{ marginLeft: 8 }} 
                                        color={priorityColors[file.priority] || 'default'}
                                    >
                                        {priorityNames[file.priority as keyof typeof priorityNames] || '未知'}
                                    </Tag>
                                    <Tag color="success">{file.size_formatted}</Tag>
                                    {file.progress < 1 && (
                                        <Progress
                                            percent={Math.round(file.progress * 100)}
                                            size="small"
                                            style={{ width: 150, marginLeft: 10, display: 'inline-block' }}
                                        />
                                    )}
                                </div>
                            }
                            description={file.path}
                        />
                    </List.Item>
                )}
            />
        </Modal>
    )
}

return (
    <>
        <Card 
            title={
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span>下载列表</span>
                    <Space>
                        <Button
                            icon={<FilterOutlined />}
                            size="small"
                            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                        >
                            高级筛选 {showAdvancedFilters ? '▼' : '▶'}
                        </Button>
                        <Button
                            icon={<ReloadOutlined />}
                            size="small"
                            onClick={refresh}
                            loading={loading}
                        >
                            刷新
                        </Button>
                    </Space>
                </div>
            }
            loading={loading}
            extra={<Input.Search value={keyword} onChange={e => setKeyword(e.target.value)} placeholder={'搜索'} />}>
            
            {/* 统计信息 */}
            <Row gutter={16} style={{ marginBottom: 16 }}>
                <Col span={6}>
                    <Statistic title="总任务数" value={data.length} />
                </Col>
                <Col span={6}>
                    <Statistic 
                        title="进行中" 
                        value={data.reduce((count: number, item: any) => 
                            count + item.files.filter((f: any) => f.progress > 0 && f.progress < 1).length, 0
                        )} 
                        valueStyle={{ color: '#1890ff' }}
                    />
                </Col>
                <Col span={6}>
                    <Statistic 
                        title="已完成" 
                        value={data.reduce((count: number, item: any) => 
                            count + item.files.filter((f: any) => f.progress >= 1).length, 0
                        )} 
                        valueStyle={{ color: '#52c41a' }}
                    />
                </Col>
                <Col span={6}>
                    <Statistic 
                        title="失败/等待" 
                        value={data.reduce((count: number, item: any) => 
                            count + item.files.filter((f: any) => f.progress === 0).length, 0
                        )} 
                        valueStyle={{ color: '#ff4d4f' }}
                    />
                </Col>
            </Row>

            <Divider />

            {/* 基础过滤选项 */}
            <div style={{ marginBottom: 16 }}>
                <Row gutter={16}>
                    <Col>
                        <Space>
                            <span>显示已完成:</span>
                            <Switch 
                                checked={includeSuccess} 
                                onChange={setIncludeSuccess}
                                size="small"
                            />
                        </Space>
                    </Col>
                    <Col>
                        <Space>
                            <span>显示失败:</span>
                            <Switch 
                                checked={includeFailed} 
                                onChange={setIncludeFailed}
                                size="small"
                            />
                        </Space>
                    </Col>
                </Row>
            </div>

            {/* 高级过滤选项 */}
            {showAdvancedFilters && (
                <Card size="small" style={{ marginBottom: 16 }}>
                    <Row gutter={[16, 8]}>
                        <Col span={8}>
                            <div style={{ marginBottom: 8 }}>状态筛选</div>
                            <Select
                                value={advancedFilters.status}
                                onChange={(value) => setAdvancedFilters({
                                    ...advancedFilters,
                                    status: value
                                })}
                                style={{ width: '100%' }}
                            >
                                <Select.Option value="all">全部状态</Select.Option>
                                <Select.Option value="downloading">下载中</Select.Option>
                                <Select.Option value="completed">已完成</Select.Option>
                                <Select.Option value="failed">失败/等待</Select.Option>
                            </Select>
                        </Col>
                        <Col span={8}>
                            <div style={{ marginBottom: 8 }}>排序方式</div>
                            <Select
                                value={`${advancedFilters.sortBy}-${advancedFilters.sortOrder}`}
                                onChange={(value) => {
                                    const [sortBy, sortOrder] = value.split('-');
                                    setAdvancedFilters({
                                        ...advancedFilters,
                                        sortBy,
                                        sortOrder
                                    });
                                }}
                                style={{ width: '100%' }}
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
                            <div style={{ marginBottom: 8 }}>快速操作</div>
                            <Space>
                                <Button 
                                    size="small" 
                                    onClick={() => {
                                        setAdvancedFilters({
                                            status: 'all',
                                            sizeRange: [0, 10000],
                                            dateRange: null,
                                            sortBy: 'date',
                                            sortOrder: 'desc'
                                        });
                                        setKeyword('');
                                    }}
                                >
                                    重置筛选
                                </Button>
                            </Space>
                        </Col>
                    </Row>
                </Card>
            )}
            
            {realData.length > 0 ? (
                <>
                    {realData.length !== data.length && (
                        <div style={{ marginBottom: 16, padding: '8px 12px', background: '#f0f2f5', borderRadius: 4 }}>
                            <Space>
                                <Badge count={realData.length} style={{ backgroundColor: '#1890ff' }} />
                                <span>筛选结果：{realData.length} / {data.length} 个任务</span>
                            </Space>
                        </div>
                    )}
                    <Collapse items={items} ghost={true} />
                </>
            ) : data.length > 0 ? (
                <Empty description="没有符合筛选条件的下载任务" />
            ) : (
                <Empty description={(<span>无下载任务，<Link to={'/setting/download'}>配置下载</Link></span>)} />
            )}
            <VideoDetail title={'下载整理'}
                mode={'download'}
                width={1100}
                path={selected}
                open={!!selected}
                onCancel={() => setSelected(undefined)}
                onOk={() => {
                    setSelected(undefined)
                    refresh()
                }}
            />
        </Card>
        <FileManageModal />
    </>
)

