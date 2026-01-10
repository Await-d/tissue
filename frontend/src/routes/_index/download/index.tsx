import { Card, Collapse, Empty, Input, List, App, Modal, Space, Tag, theme, Tooltip, Progress, Switch, Row, Col, Select, DatePicker, Divider, Button, Badge, Statistic } from "antd";
import * as api from "../../../apis/download";
import { useDebounce, useRequest } from "ahooks";
import { FileDoneOutlined, FolderViewOutlined, UserOutlined, FilterOutlined, ReloadOutlined, DeleteOutlined, PauseOutlined, PlayCircleOutlined, SearchOutlined } from "@ant-design/icons";
import React, { useMemo, useState } from "react";
import IconButton from "../../../components/IconButton";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import VideoDetail from "../../../components/VideoDetail";
import { useThemeColors } from "../../../hooks/useThemeColors";

const { useToken } = theme

export const Route = createFileRoute('/_index/download/')({
    component: Download,
})

function Download() {
    const { message, modal } = App.useApp()
    const { token } = useToken()
    const colors = useThemeColors()
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

    const items = realData.map((torrent: any) => (
        {
            key: torrent.hash,
            label: (
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    width: '100%',
                }}>
                    <span style={{
                        color: colors.textPrimary,
                        fontWeight: 500,
                        fontSize: '14px',
                    }}>
                        {torrent.name}
                    </span>
                    <Space>
                        {(() => {
                            const totalFiles = torrent.files.length;
                            const completedFiles = torrent.files.filter((f: any) => f.progress >= 1).length;
                            const downloadingFiles = torrent.files.filter((f: any) => f.progress > 0 && f.progress < 1).length;
                            const avgProgress = torrent.files.reduce((sum: number, f: any) => sum + f.progress, 0) / totalFiles;
                            
                            return (
                                <>
                                    <Tag
                                        style={{
                                            background: completedFiles === totalFiles
                                                ? 'rgba(82, 196, 26, 0.2)'
                                                : downloadingFiles > 0
                                                ? colors.rgba('gold', 0.2)
                                                : colors.borderPrimary,
                                            borderColor: completedFiles === totalFiles
                                                ? '#52c41a'
                                                : downloadingFiles > 0
                                                ? colors.goldPrimary
                                                : colors.borderPrimary,
                                            color: completedFiles === totalFiles
                                                ? '#52c41a'
                                                : downloadingFiles > 0
                                                ? colors.goldLight
                                                : colors.textSecondary,
                                            fontWeight: 500,
                                        }}
                                    >
                                        {completedFiles}/{totalFiles} 文件
                                    </Tag>
                                    <Progress 
                                        percent={Math.round(avgProgress * 100)} 
                                        size="small" 
                                        style={{ width: 80 }}
                                        strokeColor={completedFiles === totalFiles ? '#52c41a' : {
                                            '0%': colors.goldPrimary,
                                            '100%': colors.goldLight,
                                        }}
                                        trailColor="rgba(255, 255, 255, 0.08)"
                                    />
                                </>
                            );
                        })()}
                    </Space>
                </div>
            ),
            children: (
                <List
                    itemLayout="horizontal"
                    dataSource={torrent.files}
                    style={{
                        background: colors.bgBase,
                        borderRadius: '8px',
                        padding: '12px',
                    }}
                    renderItem={(item: any, index) => (
                        <List.Item
                            style={{
                                background: colors.bgElevated,
                                borderRadius: '8px',
                                padding: '12px 16px',
                                marginBottom: '8px',
                                border: '1px solid rgba(255, 255, 255, 0.08)',
                                transition: 'all 0.3s ease',
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.borderColor = colors.goldPrimary;
                                e.currentTarget.style.background = colors.bgContainer;
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.borderColor = colors.borderPrimary;
                                e.currentTarget.style.background = colors.bgElevated;
                            }}
                            actions={[
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
                                            <a
                                                onClick={() => handleVideoClick(item.num)}
                                                style={{
                                                    color: colors.goldPrimary,
                                                    fontWeight: 500,
                                                    transition: 'color 0.3s ease',
                                                }}
                                                onMouseEnter={(e) => {
                                                    e.currentTarget.style.color = colors.goldLight;
                                                }}
                                                onMouseLeave={(e) => {
                                                    e.currentTarget.style.color = colors.goldPrimary;
                                                }}
                                            >
                                                {item.name}
                                            </a>
                                        ) : (
                                            <span style={{ color: colors.textPrimary, fontWeight: 500 }}>
                                                {item.name}
                                            </span>
                                        )}
                                        <Tag
                                            style={{
                                                marginLeft: 5,
                                                background: 'rgba(82, 196, 26, 0.2)',
                                                borderColor: '#52c41a',
                                                color: '#52c41a',
                                                fontWeight: 500,
                                            }}
                                        >
                                            {item.size}
                                        </Tag>
                                        {item.progress < 1 && (
                                            <Progress
                                                percent={Math.round(item.progress * 100)}
                                                size="small"
                                                style={{ width: 100, marginLeft: 10, display: 'inline-block' }}
                                                strokeColor={{
                                                    '0%': colors.goldPrimary,
                                                    '100%': colors.goldLight,
                                                }}
                                                trailColor="rgba(255, 255, 255, 0.08)"
                                            />
                                        )}
                                    </span>
                                )}
                                description={(
                                    <div>
                                        <div style={{ color: colors.textTertiary, fontSize: '13px', marginTop: '4px' }}>
                                            {item.path}
                                        </div>
                                        {item.actors && item.actors.length > 0 && (
                                            <div style={{ marginTop: 8 }}>
                                                <UserOutlined style={{ marginRight: 6, color: colors.textSecondary }} />
                                                {item.actors.map((actor: string, idx: number) => (
                                                    <React.Fragment key={actor}>
                                                        <a
                                                            onClick={() => handleActorClick(actor)}
                                                            style={{
                                                                color: colors.goldPrimary,
                                                                fontWeight: 500,
                                                                fontSize: '13px',
                                                                transition: 'color 0.3s ease',
                                                            }}
                                                            onMouseEnter={(e) => {
                                                                e.currentTarget.style.color = colors.goldLight;
                                                            }}
                                                            onMouseLeave={(e) => {
                                                                e.currentTarget.style.color = colors.goldPrimary;
                                                            }}
                                                        >
                                                            {actor}
                                                        </a>
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
                    <Tooltip title={'重新开始下载'}>
                        <IconButton onClick={() => {
                            message.info('重新开始下载功能开发中...');
                        }}>
                            <PlayCircleOutlined style={{ fontSize: token.sizeLG, color: '#1890ff' }} />
                        </IconButton>
                    </Tooltip>
                    <Tooltip title={'暂停下载'}>
                        <IconButton onClick={() => {
                            message.info('暂停下载功能开发中...');
                        }}>
                            <PauseOutlined style={{ fontSize: token.sizeLG, color: '#faad14' }} />
                        </IconButton>
                    </Tooltip>
                    <Tooltip title={'标记为"整理成功"'}>
                        <IconButton onClick={() => {
                            modal.confirm({
                                title: '是否确认标记为完成',
                                onOk: () => onComplete(torrent.hash)
                            })
                        }}>
                            <FileDoneOutlined style={{ fontSize: token.sizeLG, color: '#52c41a' }} />
                        </IconButton>
                    </Tooltip>
                    <Tooltip title={'删除任务'}>
                        <IconButton onClick={() => {
                            modal.confirm({
                                title: '确认删除下载任务？',
                                content: '此操作将删除下载任务，但不会删除已下载的文件',
                                okText: '确认删除',
                                okType: 'danger',
                                onOk: () => {
                                    message.info('删除功能开发中...');
                                }
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
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                }}>
                    <span style={{
                        color: colors.textPrimary,
                        fontSize: '18px',
                        fontWeight: 600,
                    }}>
                        下载列表
                    </span>
                    <Space>
                        <Button
                            icon={<FilterOutlined />}
                            size="small"
                            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                            style={{
                                background: colors.bgContainer,
                                borderColor: colors.borderPrimary,
                                color: colors.textSecondary,
                                transition: 'all 0.3s ease',
                            }}
                        >
                            高级筛选 {showAdvancedFilters ? '▼' : '▶'}
                        </Button>
                        <Button
                            icon={<ReloadOutlined />}
                            size="small"
                            onClick={refresh}
                            loading={loading}
                            style={{
                                background: 'linear-gradient(135deg, #d4a852 0%, #e8c780 100%)',
                                borderColor: colors.goldPrimary,
                                color: colors.bgBase,
                                fontWeight: 600,
                                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                            }}
                        >
                            刷新
                        </Button>
                    </Space>
                </div>
            }
            loading={loading}
            extra={
                <Space.Compact>
                    <Input
                        value={keyword}
                        onChange={e => setKeyword(e.target.value)}
                        placeholder={'搜索'}
                        style={{
                            background: colors.bgContainer,
                            borderColor: colors.borderPrimary,
                            color: colors.textPrimary,
                        }}
                    />
                    <Button
                        icon={<SearchOutlined />}
                        style={{
                            background: colors.bgContainer,
                            borderColor: colors.borderPrimary,
                            color: colors.textSecondary,
                        }}
                    />
                </Space.Compact>
            }
            style={{
                background: colors.bgElevated,
                borderColor: colors.borderPrimary,
            }}
            styles={{
                header: {
                    background: colors.bgBase,
                    borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
                },
                body: {
                    background: colors.bgElevated,
                }
            }}>
            
            {/* 统计信息 */}
            <Row gutter={16} style={{ marginBottom: 20 }}>
                <Col span={6}>
                    <Card
                        size="small"
                        style={{
                            background: colors.bgContainer,
                            borderColor: colors.borderPrimary,
                            borderRadius: '8px',
                        }}
                        styles={{
                            body: { padding: '16px' }
                        }}
                    >
                        <Statistic
                            title={<span style={{ color: colors.textSecondary, fontSize: '14px' }}>总任务数</span>}
                            value={data.length}
                            valueStyle={{ color: colors.textPrimary, fontSize: '24px', fontWeight: 600 }}
                        />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card
                        size="small"
                        style={{
                            background: colors.bgContainer,
                            borderColor: colors.borderPrimary,
                            borderRadius: '8px',
                        }}
                        styles={{
                            body: { padding: '16px' }
                        }}
                    >
                        <Statistic 
                            title={<span style={{ color: colors.textSecondary, fontSize: '14px' }}>进行中</span>}
                            value={data.reduce((count: number, item: any) => 
                                count + item.files.filter((f: any) => f.progress > 0 && f.progress < 1).length, 0
                            )} 
                            valueStyle={{ color: '#4facfe', fontSize: '24px', fontWeight: 600 }}
                        />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card
                        size="small"
                        style={{
                            background: colors.bgContainer,
                            borderColor: colors.borderPrimary,
                            borderRadius: '8px',
                        }}
                        styles={{
                            body: { padding: '16px' }
                        }}
                    >
                        <Statistic 
                            title={<span style={{ color: colors.textSecondary, fontSize: '14px' }}>已完成</span>}
                            value={data.reduce((count: number, item: any) => 
                                count + item.files.filter((f: any) => f.progress >= 1).length, 0
                            )} 
                            valueStyle={{ color: '#52c41a', fontSize: '24px', fontWeight: 600 }}
                        />
                    </Card>
                </Col>
                <Col span={6}>
                    <Card
                        size="small"
                        style={{
                            background: colors.bgContainer,
                            borderColor: colors.borderPrimary,
                            borderRadius: '8px',
                        }}
                        styles={{
                            body: { padding: '16px' }
                        }}
                    >
                        <Statistic 
                            title={<span style={{ color: colors.textSecondary, fontSize: '14px' }}>失败/等待</span>}
                            value={data.reduce((count: number, item: any) => 
                                count + item.files.filter((f: any) => f.progress === 0).length, 0
                            )} 
                            valueStyle={{ color: '#ff7875', fontSize: '24px', fontWeight: 600 }}
                        />
                    </Card>
                </Col>
            </Row>

            <Divider />

            {/* 基础过滤选项 */}
            <div style={{
                marginBottom: 16,
                padding: '12px 16px',
                background: colors.bgContainer,
                border: '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: '8px',
            }}>
                <Row gutter={16}>
                    <Col>
                        <Space>
                            <span style={{ color: colors.textSecondary, fontSize: '14px' }}>显示已完成:</span>
                            <Switch 
                                checked={includeSuccess} 
                                onChange={setIncludeSuccess}
                                size="small"
                                style={{
                                    background: includeSuccess ? colors.goldPrimary : 'rgba(255, 255, 255, 0.2)',
                                }}
                            />
                        </Space>
                    </Col>
                    <Col>
                        <Space>
                            <span style={{ color: colors.textSecondary, fontSize: '14px' }}>显示失败:</span>
                            <Switch 
                                checked={includeFailed} 
                                onChange={setIncludeFailed}
                                size="small"
                                style={{
                                    background: includeFailed ? colors.goldPrimary : 'rgba(255, 255, 255, 0.2)',
                                }}
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
                    styles={{
                        body: {
                            padding: '16px',
                            background: colors.bgContainer,
                        }
                    }}
                >
                    <Row gutter={[16, 8]}>
                        <Col span={8}>
                            <div style={{
                                marginBottom: 8,
                                color: colors.textSecondary,
                                fontSize: '14px',
                                fontWeight: 500,
                            }}>
                                状态筛选
                            </div>
                            <Select
                                value={advancedFilters.status}
                                onChange={(value) => setAdvancedFilters({
                                    ...advancedFilters,
                                    status: value
                                })}
                                style={{ width: '100%' }}
                                dropdownStyle={{
                                    background: colors.bgContainer,
                                    borderColor: colors.borderPrimary,
                                }}
                            >
                                <Select.Option value="all">全部状态</Select.Option>
                                <Select.Option value="downloading">下载中</Select.Option>
                                <Select.Option value="completed">已完成</Select.Option>
                                <Select.Option value="failed">失败/等待</Select.Option>
                            </Select>
                        </Col>
                        <Col span={8}>
                            <div style={{
                                marginBottom: 8,
                                color: colors.textSecondary,
                                fontSize: '14px',
                                fontWeight: 500,
                            }}>
                                排序方式
                            </div>
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
                                dropdownStyle={{
                                    background: colors.bgContainer,
                                    borderColor: colors.borderPrimary,
                                }}
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
                            <div style={{
                                marginBottom: 8,
                                color: colors.textSecondary,
                                fontSize: '14px',
                                fontWeight: 500,
                            }}>
                                快速操作
                            </div>
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
                                    style={{
                                        background: colors.bgContainer,
                                        borderColor: colors.borderPrimary,
                                        color: colors.textSecondary,
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
                        <div style={{
                            marginBottom: 16,
                            padding: '12px 16px',
                            background: colors.bgContainer,
                            border: '1px solid rgba(255, 255, 255, 0.08)',
                            borderRadius: 8,
                        }}>
                            <Space>
                                <Badge
                                    count={realData.length}
                                    style={{
                                        background: 'linear-gradient(135deg, #d4a852 0%, #e8c780 100%)',
                                        color: colors.bgBase,
                                        fontWeight: 600,
                                        boxShadow: '0 2px 8px rgba(212, 168, 82, 0.3)',
                                    }}
                                />
                                <span style={{
                                    color: colors.textSecondary,
                                    fontSize: '14px',
                                }}>
                                    筛选结果：{realData.length} / {data.length} 个任务
                                </span>
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

