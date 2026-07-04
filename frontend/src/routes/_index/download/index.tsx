import { Card, Collapse, Empty, Input, List, App, Modal, Space, Tag, theme, Tooltip, Progress, Row, Col, Button, Badge, Pagination } from "antd";
import * as api from "../../../apis/download";
import { useDebounce, useRequest } from "ahooks";
import { FileDoneOutlined, FolderViewOutlined, UserOutlined, FilterOutlined, ReloadOutlined, DeleteOutlined, PauseOutlined, PlayCircleOutlined, SearchOutlined, ClearOutlined } from "@ant-design/icons";
import React, { useMemo, useState, useCallback } from "react";
import IconButton from "../../../components/IconButton";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import VideoDetail from "../../../components/VideoDetail";
import { useThemeColors } from "../../../hooks/useThemeColors";
import { cleanupTorrent, previewCleanup, cleanupAllTorrents } from "@/apis/downloadFilter";
import type { CleanupPreviewData, CleanupResultData } from "@/types/cleanup";
import DownloadStats from "./-components/DownloadStats";
import DownloadFilters, { type AdvancedFilters } from "./-components/DownloadFilters";
import CleanupModal from "./-components/CleanupModal";
import BatchCleanupModal from "./-components/BatchCleanupModal";

const { useToken } = theme

export const Route = createFileRoute('/_index/download/')({
    component: Download,
})

const DEFAULT_ADVANCED_FILTERS: AdvancedFilters = {
    status: 'all',
    sizeRange: [0, 10000],
    dateRange: null,
    sortBy: 'date',
    sortOrder: 'desc',
}

const PAGE_SIZE = 10;

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
    const [advancedFilters, setAdvancedFilters] = useState<AdvancedFilters>(DEFAULT_ADVANCED_FILTERS)
    const [cleanupModalVisible, setCleanupModalVisible] = useState(false)
    const [cleanupPreview, setCleanupPreview] = useState<CleanupPreviewData | null>(null)
    const [selectedTorrentHash, setSelectedTorrentHash] = useState<string>('')
    const [cleanupLoading, setCleanupLoading] = useState(false)

    // 分页状态
    const [currentPage, setCurrentPage] = useState(1)

    // 批量清理状态
    const [batchCleanupModalVisible, setBatchCleanupModalVisible] = useState(false)
    const [batchCleanupResult, setBatchCleanupResult] = useState<CleanupResultData | null>(null)
    const [batchCleanupLoading, setBatchCleanupLoading] = useState(false)
    const affectedBatchCleanupResults = useMemo(
        () => (batchCleanupResult?.torrent_results || []).filter((item: any) => (item.deleted_files || 0) > 0),
        [batchCleanupResult]
    )

    const { data = [], loading, refresh } = useRequest(
        () => api.getDownloads({
            include_success: includeSuccess,
            include_failed: includeFailed
        }),
        { refreshDeps: [includeSuccess, includeFailed] }
    )

    const realData = useMemo(() => {
        let filteredData = data.filter((item: any) => {
            const matchKeyword = !keywordDebounce ||
                item.name.indexOf(keywordDebounce) !== -1 ||
                item.files.some((sub: any) => (
                    sub.name.indexOf(keywordDebounce) !== -1 ||
                    sub.path.indexOf(keywordDebounce) !== -1
                ));
            return matchKeyword;
        });

        if (showAdvancedFilters) {
            filteredData = filteredData.filter((item: any) => {
                const tags: string[] = Array.isArray(item.tags) ? item.tags : [];
                if (advancedFilters.status !== 'all') {
                    const hasCompleted = item.files.some((file: any) => file.progress >= 1);
                    const hasDownloading = item.files.some((file: any) => file.progress > 0 && file.progress < 1);
                    const hasFailedTag = tags.includes('整理失败');
                    const isWaiting = !hasCompleted && !hasDownloading && !hasFailedTag;
                    if (advancedFilters.status === 'completed' && !hasCompleted) return false;
                    if (advancedFilters.status === 'downloading' && !hasDownloading) return false;
                    if (advancedFilters.status === 'failed' && !(hasFailedTag || isWaiting)) return false;
                }
                return true;
            });
        }

        if (showAdvancedFilters) {
            const toNumber = (sizeText: string): number => {
                const normalized = (sizeText || '').trim().toUpperCase();
                const value = parseFloat(normalized.replace(/[^\d.]/g, ''));
                if (!Number.isFinite(value)) return 0;
                if (normalized.includes('TB')) return value * 1024;
                if (normalized.includes('GB')) return value;
                if (normalized.includes('MB')) return value / 1024;
                if (normalized.includes('KB')) return value / (1024 * 1024);
                return value;
            };

            if (advancedFilters.sortBy === 'date') {
                if (advancedFilters.sortOrder === 'asc') {
                    filteredData = [...filteredData].reverse();
                }
                return filteredData;
            }

            filteredData = [...filteredData].sort((a: any, b: any) => {
                const progressA = a.files.length
                    ? a.files.reduce((sum: number, f: any) => sum + (f.progress || 0), 0) / a.files.length
                    : 0;
                const progressB = b.files.length
                    ? b.files.reduce((sum: number, f: any) => sum + (f.progress || 0), 0) / b.files.length
                    : 0;
                const compareBy = (() => {
                    if (advancedFilters.sortBy === 'progress') return progressA - progressB;
                    if (advancedFilters.sortBy === 'size') return toNumber(a.size || '') - toNumber(b.size || '');
                    return 0;
                })();
                return advancedFilters.sortOrder === 'asc' ? compareBy : -compareBy;
            });
        }

        return filteredData;
    }, [data, keywordDebounce, showAdvancedFilters, advancedFilters])

    // 前端分页
    const pagedData = useMemo(() => {
        const start = (currentPage - 1) * PAGE_SIZE;
        return realData.slice(start, start + PAGE_SIZE);
    }, [realData, currentPage]);

    const { run: onComplete } = useRequest(api.completeDownload, {
        manual: true,
        onSuccess: () => {
            message.success("标记成功")
            refresh()
        }
    })

    // 清理文件处理函数
    const handleCleanupClick = useCallback(async (torrentHash: string) => {
        try {
            setCleanupLoading(true)
            setSelectedTorrentHash(torrentHash)
            const result = await previewCleanup(torrentHash)
            if (result.success) {
                setCleanupPreview(result.data)
                setCleanupModalVisible(true)
            } else {
                message.error(result.message || '获取清理预览失败')
            }
        } catch (error: any) {
            message.error(error?.message || '获取清理预览失败')
        } finally {
            setCleanupLoading(false)
        }
    }, [message])

    const handleCleanupConfirm = useCallback(async () => {
        try {
            setCleanupLoading(true)
            const result = await cleanupTorrent(selectedTorrentHash, false)
            if (result.success) {
                message.success('清理成功')
                setCleanupModalVisible(false)
                setCleanupPreview(null)
                refresh()
            } else {
                message.error(result.message || '清理失败')
            }
        } catch (error: any) {
            message.error(error?.message || '清理失败')
        } finally {
            setCleanupLoading(false)
        }
    }, [selectedTorrentHash, message, refresh])

    const handleCleanupCancel = useCallback(() => {
        setCleanupModalVisible(false)
        setCleanupPreview(null)
        setSelectedTorrentHash('')
    }, [])

    // 批量清理处理函数
    const handleBatchCleanupClick = useCallback(async () => {
        try {
            setBatchCleanupLoading(true)
            const result = await cleanupAllTorrents(undefined, true, includeSuccess, includeFailed)
            if (result.success && result.data) {
                setBatchCleanupResult(result.data)
                setBatchCleanupModalVisible(true)
            } else {
                message.error(result.message || '获取批量清理预览失败')
            }
        } catch (error: any) {
            message.error(error?.message || '获取批量清理预览失败')
        } finally {
            setBatchCleanupLoading(false)
        }
    }, [includeSuccess, includeFailed, message])

    const handleBatchCleanupConfirm = useCallback(async () => {
        try {
            setBatchCleanupLoading(true)
            const result = await cleanupAllTorrents(undefined, false, includeSuccess, includeFailed)
            if (result.success) {
                message.success(`批量清理成功，共清理 ${result.data?.total_deleted_files || 0} 个文件`)
                setBatchCleanupModalVisible(false)
                setBatchCleanupResult(null)
                refresh()
            } else {
                message.error(result.message || '批量清理失败')
            }
        } catch (error: any) {
            message.error(error?.message || '批量清理失败')
        } finally {
            setBatchCleanupLoading(false)
        }
    }, [includeSuccess, includeFailed, message, refresh])

    const handleBatchCleanupCancel = useCallback(() => {
        setBatchCleanupModalVisible(false)
        setBatchCleanupResult(null)
    }, [])

    const handleVideoClick = useCallback((num: string) => {
        if (num) {
            const urlParams = new URLSearchParams(window.location.search);
            const source = urlParams.get('source') || 'javdb';
            const url = urlParams.get('url') || '';
            navigate({ to: `/video/${num}`, search: { source, url } });
        } else {
            message.info("无法识别番号，无法跳转到详情页面");
        }
    }, [navigate, message])

    const handleActorClick = useCallback((actorName: string) => {
        navigate({ to: '/actor', search: { actorName } });
    }, [navigate])

    const handleResetFilters = useCallback(() => {
        setAdvancedFilters(DEFAULT_ADVANCED_FILTERS)
        setKeyword('')
        setCurrentPage(1)
    }, [])

    const items = useMemo(() => pagedData.map((torrent: any) => ({
        key: torrent.hash,
        label: (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                <span style={{ color: colors.textPrimary, fontWeight: 500, fontSize: '14px' }}>
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
                                <Tag style={{
                                    background: completedFiles === totalFiles ? colors.rgba('green', 0.2) : downloadingFiles > 0 ? colors.rgba('gold', 0.2) : colors.borderPrimary,
                                    borderColor: completedFiles === totalFiles ? colors.success : downloadingFiles > 0 ? colors.goldPrimary : colors.borderPrimary,
                                    color: completedFiles === totalFiles ? colors.success : downloadingFiles > 0 ? colors.goldLight : colors.textSecondary,
                                    fontWeight: 500,
                                }}>
                                    {completedFiles}/{totalFiles} 文件
                                </Tag>
                                <Progress
                                    percent={Math.round(avgProgress * 100)}
                                    size="small"
                                    style={{ width: 80 }}
                                    strokeColor={completedFiles === totalFiles ? colors.success : { '0%': colors.goldPrimary, '100%': colors.goldLight }}
                                    trailColor={colors.borderSecondary}
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
                style={{ background: colors.bgBase, borderRadius: '8px', padding: '12px' }}
                renderItem={(item: any) => (
                    <List.Item
                        className="tissue-hover-item"
                        style={{
                            background: colors.bgElevated,
                            borderRadius: '8px',
                            padding: '12px 16px',
                            marginBottom: '8px',
                            border: `1px solid ${colors.borderPrimary}`,
                            transition: 'all 0.3s ease',
                        }}
                        actions={[
                            <Tooltip key="organize" title={'整理'}>
                                <IconButton onClick={() => setSelected(item.path)}>
                                    <FolderViewOutlined style={{ fontSize: token.sizeLG }} />
                                </IconButton>
                            </Tooltip>
                        ]}>
                        <List.Item.Meta
                            title={(
                                <span>
                                    {item.num ? (
                                        <button
                                            type="button"
                                            onClick={() => handleVideoClick(item.num)}
                                            className="tissue-hover-text-gold"
                                            style={{
                                                background: 'transparent', border: 'none', padding: 0, margin: 0,
                                                cursor: 'pointer', color: colors.goldPrimary, fontWeight: 500,
                                            }}
                                        >
                                            {item.name}
                                        </button>
                                    ) : (
                                        <span style={{ color: colors.textPrimary, fontWeight: 500 }}>
                                            {item.name}
                                        </span>
                                    )}
                                    <Tag style={{ marginLeft: 5, background: colors.rgba('green', 0.2), borderColor: colors.success, color: colors.success, fontWeight: 500 }}>
                                        {item.size}
                                    </Tag>
                                    {item.progress < 1 && (
                                        <Progress
                                            percent={Math.round(item.progress * 100)}
                                            size="small"
                                            style={{ width: 100, marginLeft: 10, display: 'inline-block' }}
                                            strokeColor={{ '0%': colors.goldPrimary, '100%': colors.goldLight }}
                                            trailColor={colors.borderSecondary}
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
                                                    <button
                                                        type="button"
                                                        onClick={() => handleActorClick(actor)}
                                                        className="tissue-hover-text-gold"
                                                        style={{
                                                            background: 'transparent', border: 'none', padding: 0, margin: 0,
                                                            cursor: 'pointer', color: colors.goldPrimary, fontWeight: 500,
                                                            fontSize: '13px',
                                                        }}
                                                    >
                                                        {actor}
                                                    </button>
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
                <Tooltip title={'清理文件'}>
                    <IconButton
                        onClick={() => handleCleanupClick(torrent.hash)}
                        loading={cleanupLoading && selectedTorrentHash === torrent.hash}
                    >
                        <ClearOutlined style={{ fontSize: token.sizeLG, color: colors.warning }} />
                    </IconButton>
                </Tooltip>
                <Tooltip title={'重新开始下载'}>
                    <IconButton onClick={() => message.info('重新开始下载功能开发中...')}>
                        <PlayCircleOutlined style={{ fontSize: token.sizeLG, color: colors.info }} />
                    </IconButton>
                </Tooltip>
                <Tooltip title={'暂停下载'}>
                    <IconButton onClick={() => message.info('暂停下载功能开发中...')}>
                        <PauseOutlined style={{ fontSize: token.sizeLG, color: colors.warning }} />
                    </IconButton>
                </Tooltip>
                <Tooltip title={'标记为"整理成功"'}>
                    <IconButton onClick={() => {
                        modal.confirm({
                            title: '是否确认标记为完成',
                            onOk: () => onComplete(torrent.hash)
                        })
                    }}>
                        <FileDoneOutlined style={{ fontSize: token.sizeLG, color: colors.success }} />
                    </IconButton>
                </Tooltip>
                <Tooltip title={'删除任务'}>
                    <IconButton onClick={() => {
                        modal.confirm({
                            title: '确认删除下载任务？',
                            content: '此操作将删除下载任务，但不会删除已下载的文件',
                            okText: '确认删除',
                            okType: 'danger',
                            onOk: () => message.info('删除功能开发中...'),
                        })
                    }}>
                        <DeleteOutlined style={{ fontSize: token.sizeLG, color: colors.error }} />
                    </IconButton>
                </Tooltip>
            </Space>
        )
    })), [pagedData, colors, token, cleanupLoading, selectedTorrentHash, handleVideoClick, handleActorClick, handleCleanupClick, message, modal, onComplete])

    return (
        <Card
            title={
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ color: colors.textPrimary, fontSize: '18px', fontWeight: 600 }}>
                        下载列表
                    </span>
                    <Space>
                        <Tooltip title="检查不符合过滤规则的文件">
                            <Button
                                icon={<SearchOutlined />}
                                size="small"
                                onClick={handleBatchCleanupClick}
                                loading={batchCleanupLoading}
                                style={{ background: colors.bgContainer, borderColor: colors.goldPrimary, color: colors.goldPrimary, transition: 'all 0.3s ease' }}
                            >
                                快速检查
                            </Button>
                        </Tooltip>
                        <Button
                            icon={<ClearOutlined />}
                            size="small"
                            onClick={handleBatchCleanupClick}
                            loading={batchCleanupLoading}
                            style={{ background: colors.bgContainer, borderColor: colors.warning, color: colors.warning, transition: 'all 0.3s ease' }}
                        >
                            批量清理
                        </Button>
                        <Button
                            icon={<FilterOutlined />}
                            size="small"
                            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                            style={{ background: colors.bgContainer, borderColor: colors.borderPrimary, color: colors.textSecondary, transition: 'all 0.3s ease' }}
                        >
                            高级筛选 {showAdvancedFilters ? '▼' : '▶'}
                        </Button>
                        <Button
                            icon={<ReloadOutlined />}
                            size="small"
                            onClick={refresh}
                            loading={loading}
                            style={{
                                background: `linear-gradient(135deg, ${colors.goldPrimary} 0%, ${colors.goldLight} 100%)`,
                                borderColor: colors.goldPrimary, color: colors.bgBase, fontWeight: 600,
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
                        style={{ background: colors.bgContainer, borderColor: colors.borderPrimary, color: colors.textPrimary }}
                    />
                    <Button icon={<SearchOutlined />} style={{ background: colors.bgContainer, borderColor: colors.borderPrimary, color: colors.textSecondary }} />
                </Space.Compact>
            }
            style={{ background: colors.bgElevated, borderColor: colors.borderPrimary }}
            styles={{
                header: { background: colors.bgBase, borderBottom: `1px solid ${colors.borderPrimary}` },
                body: { background: colors.bgElevated },
            }}>

            <DownloadStats data={data} />

            <div style={{ marginBottom: 16 }} />

            <DownloadFilters
                includeSuccess={includeSuccess}
                includeFailed={includeFailed}
                onIncludeSuccessChange={(v) => { setIncludeSuccess(v); setCurrentPage(1); }}
                onIncludeFailedChange={(v) => { setIncludeFailed(v); setCurrentPage(1); }}
                showAdvancedFilters={showAdvancedFilters}
                advancedFilters={advancedFilters}
                onAdvancedFiltersChange={(v) => { setAdvancedFilters(v); setCurrentPage(1); }}
                onResetFilters={handleResetFilters}
            />

            {realData.length > 0 ? (
                <>
                    {realData.length !== data.length && (
                        <div style={{
                            marginBottom: 16, padding: '12px 16px', background: colors.bgContainer,
                            border: `1px solid ${colors.borderPrimary}`, borderRadius: 8,
                        }}>
                            <Space>
                                <Badge count={realData.length} style={{
                                    background: `linear-gradient(135deg, ${colors.goldPrimary} 0%, ${colors.goldLight} 100%)`,
                                    color: colors.bgBase, fontWeight: 600, boxShadow: `0 2px 8px ${colors.rgba('gold', 0.3)}`,
                                }} />
                                <span style={{ color: colors.textSecondary, fontSize: '14px' }}>
                                    筛选结果：{realData.length} / {data.length} 个任务
                                </span>
                            </Space>
                        </div>
                    )}
                    <Collapse items={items} ghost={true} />
                    {realData.length > PAGE_SIZE && (
                        <div style={{ display: 'flex', justifyContent: 'center', marginTop: 24 }}>
                            <Pagination
                                current={currentPage}
                                pageSize={PAGE_SIZE}
                                total={realData.length}
                                onChange={(page) => setCurrentPage(page)}
                                showSizeChanger={false}
                                showTotal={(total) => `共 ${total} 个任务`}
                            />
                        </div>
                    )}
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
                onOk={() => { setSelected(undefined); refresh() }}
            />

            <CleanupModal
                open={cleanupModalVisible}
                preview={cleanupPreview}
                loading={cleanupLoading}
                onConfirm={handleCleanupConfirm}
                onCancel={handleCleanupCancel}
            />

            <BatchCleanupModal
                open={batchCleanupModalVisible}
                result={batchCleanupResult}
                affectedResults={affectedBatchCleanupResults}
                loading={batchCleanupLoading}
                onConfirm={handleBatchCleanupConfirm}
                onCancel={handleBatchCleanupCancel}
            />
        </Card>
    )
}
