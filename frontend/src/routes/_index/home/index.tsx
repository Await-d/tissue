import Filter, { FilterField } from "./-components/filter.tsx";
import React, { useMemo, useCallback } from "react";
import { Col, message, Row, Button, Tooltip, Checkbox, Dropdown } from "antd";
import { ReloadOutlined, InboxOutlined, CheckSquareOutlined, BorderOutlined, FolderOpenOutlined, MoreOutlined, FilterOutlined, DownOutlined, UpOutlined } from "@ant-design/icons";
import { useResponsive } from "ahooks";
import JavDBItem from "./-components/item.tsx";
import Selector from "../../../components/Selector";
import Slider from "../../../components/Slider";
import * as api from "../../../apis/home.ts";
import * as scanApi from "../../../apis/fileScan.ts";
import { Await, createFileRoute, redirect, useNavigate, useRouter } from "@tanstack/react-router";
import { useBatchSelect, type BatchSelectVideo } from "@/hooks/useBatchSelect";
import { BatchActionBar, BatchDownloadModal } from "@/components/BatchDownload";
import { useThemeColors } from '../../../hooks/useThemeColors';
import { useDownloadStatus } from '../../../hooks/useDownloadStatus';
import HomeSkeleton from "./-components/HomeSkeleton.tsx";
import ScanResultModal from "./-components/ScanResultModal.tsx";

export const Route = createFileRoute('/_index/home/')({
    component: JavDB,
    beforeLoad: ({ search }) => {
        if (Object.keys(search).length === 0)
            throw redirect({ search: { video_type: 'censored', cycle: 'daily', rank: 0, sort_by: 'rank', sort_order: 'desc' } as any })
    },
    loaderDeps: ({ search }) => ({ ...search, rank: 0 }),
    loader: async ({ deps }) => ({
        data: api.getRankings({ ...deps, source: 'JavDB' }).catch((err) => {
            console.error('获取排行榜数据失败:', err);
            return [];
        })
    }),
    staleTime: 5 * 60 * 1000
})

function JavDB() {
    const colors = useThemeColors();
    const { data } = Route.useLoaderData()
    const filter = Route.useSearch<any>()
    const navigate = useNavigate()
    const router = useRouter()
    const responsive = useResponsive()
    const isMobile = !responsive.md
    const actionButtonEdge = isMobile ? 36 : 44
    const [refreshing, setRefreshing] = React.useState(false)
    const [filterExpanded, setFilterExpanded] = React.useState(false)

    const filterLabelMaps = useMemo(() => ({
        video_type: { censored: '有码', uncensored: '无码' } as Record<string, string>,
        cycle: { daily: '日榜', weekly: '周榜', monthly: '月榜' } as Record<string, string>,
        sort_by: { rank: '评分', rank_count: '评论数', publish_date: '日期' } as Record<string, string>,
        sort_order: { desc: '降序', asc: '升序' } as Record<string, string>,
    }), []);

    const filterSummary = useMemo(() => [
        filterLabelMaps.video_type[filter.video_type as string],
        filterLabelMaps.cycle[filter.cycle as string],
        filterLabelMaps.sort_by[filter.sort_by as string],
        filterLabelMaps.sort_order[filter.sort_order as string],
        filter.rank > 0 ? `≥${filter.rank}分` : null,
    ].filter(Boolean).join(' · '), [filterLabelMaps, filter]);

    // 批量选择相关状态
    const batchSelect = useBatchSelect();
    const [batchDownloadModalVisible, setBatchDownloadModalVisible] = React.useState(false);
    const currentVideosRef = React.useRef<BatchSelectVideo[]>([]);

    // 扫描相关状态
    const [scanning, setScanning] = React.useState(false);
    const [scanResultVisible, setScanResultVisible] = React.useState(false);
    const [scanResult, setScanResult] = React.useState<scanApi.ScanResult | null>(null);

    // 下载状态 Hook
    const [videos, setVideos] = React.useState<any[]>([]);
    const { statusMap, error: downloadStatusError } = useDownloadStatus(videos);

    React.useEffect(() => {
        if (data) {
            data.then((loadedData) => {
                setVideos(Array.isArray(loadedData) ? loadedData : []);
            });
        }
    }, [data]);

    React.useEffect(() => {
        if (downloadStatusError) {
            message.warning(`下载状态检测失败: ${downloadStatusError.message}`);
        }
    }, [downloadStatusError]);

    const handleRefresh = useCallback(async () => {
        setRefreshing(true)
        try {
            await router.invalidate()
            message.success('刷新成功')
        } catch {
            message.error('刷新失败')
        } finally {
            setRefreshing(false)
        }
    }, [router])

    const handleScan = useCallback(async () => {
        setScanning(true);
        const hideLoading = message.loading('正在扫描本地视频文件...', 0);
        try {
            const result = await scanApi.triggerScan();
            setScanResult(result);
            if (result.status === 'success') {
                message.success(`扫描完成！发现 ${result.new_found} 个新视频`);
                setScanResultVisible(true);
                if (result.new_found > 0) {
                    await router.invalidate();
                }
            } else {
                message.error(result.error_message || '扫描失败');
            }
        } catch (err: any) {
            console.error('扫描失败:', err);
            message.error(err.message || '扫描失败');
        } finally {
            hideLoading();
            setScanning(false);
        }
    }, [router]);

    const filterFields: FilterField[] = useMemo(() => [
        {
            dataIndex: 'video_type', label: '类型',
            component: (<Selector items={[{ name: '有码', value: 'censored' }, { name: '无码', value: 'uncensored' }]} />),
            span: { lg: 6, md: 12, xs: 12 }
        },
        {
            dataIndex: 'cycle', label: '周期',
            component: (<Selector items={[{ name: '日榜', value: 'daily' }, { name: '周榜', value: 'weekly' }, { name: '月榜', value: 'monthly' }]} />),
            span: { lg: 6, md: 12, xs: 12 }
        },
        {
            dataIndex: 'sort_by', label: '排序',
            component: (<Selector items={[{ name: '评分', value: 'rank' }, { name: '评论数', value: 'rank_count' }, { name: '发布日期', value: 'publish_date' }]} />),
            span: { lg: 6, md: 12, xs: 24 }
        },
        {
            dataIndex: 'sort_order', label: '顺序',
            component: (<Selector items={[{ name: '降序', value: 'desc' }, { name: '升序', value: 'asc' }]} />),
            span: { lg: 6, md: 12, xs: 12 }
        },
        {
            dataIndex: 'rank', label: '评分',
            component: (<Slider step={0.1} min={0} max={5} />),
            span: { lg: 24, md: 24, xs: 24 }
        },
    ], []);

    const sortVideos = useCallback((videos: any[], sortBy: string, sortOrder: string) => {
        return [...videos].sort((a, b) => {
            const getValue = (video: any) => {
                switch (sortBy) {
                    case 'rank_count':
                        return Number(video.rank_count ?? video.comments_count ?? video.comments ?? 0) || 0;
                    case 'publish_date': {
                        const date = video.publish_date ?? video.release_date ?? '1970-01-01';
                        return new Date(date).getTime();
                    }
                    case 'rank':
                    default:
                        return Number(video.rank ?? video.rating ?? 0) || 0;
                }
            };
            const aValue = getValue(a);
            const bValue = getValue(b);
            return sortOrder === 'asc' ? aValue - bValue : bValue - aValue;
        });
    }, []);

    const normalizeVideos = useCallback((videos: any[]) => {
        if (!Array.isArray(videos)) return [];
        return videos.map((video) => {
            const rank = Number(video.rank ?? video.rating ?? 0) || 0;
            const rankCount = Number(video.rank_count ?? video.comments_count ?? video.comments ?? 0) || 0;
            const publishDate = video.publish_date ?? video.release_date ?? '';
            return { ...video, rank, rank_count: rankCount, publish_date: publishDate };
        });
    }, []);

    const mobileActionItems = useMemo(() => [
        { key: 'scan', label: '扫描本地视频文件', icon: <FolderOpenOutlined />, disabled: scanning, onClick: handleScan },
        { key: 'refresh', label: '刷新数据', icon: <ReloadOutlined spin={refreshing} />, disabled: refreshing, onClick: handleRefresh },
        { key: 'batch', label: batchSelect.isBatchMode ? '退出批量选择' : '批量选择', icon: batchSelect.isBatchMode ? <CheckSquareOutlined /> : <BorderOutlined />, onClick: batchSelect.toggleBatchMode },
    ], [scanning, refreshing, batchSelect.isBatchMode, batchSelect.toggleBatchMode, handleScan, handleRefresh]);

    // 操作按钮通用样式
    const actionBtnStyle = useMemo(() => ({
        background: colors.rgba('bgContainer', 0.8),
        border: `1px solid ${colors.borderPrimary}`,
        borderRadius: '12px',
        color: colors.textSecondary,
        height: actionButtonEdge,
        minWidth: actionButtonEdge,
        display: 'flex' as const,
        alignItems: 'center' as const,
        justifyContent: 'center' as const,
        transition: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
    }), [colors, actionButtonEdge]);

    return (
        <div style={{ minHeight: '100vh', padding: '0 0 80px 0' }}>
            {/* 顶部筛选栏 */}
            <div style={{
                position: 'sticky', top: 0, zIndex: 100,
                marginBottom: isMobile ? '12px' : '20px',
                background: colors.rgba('bgContainer', 0.85),
                backdropFilter: 'blur(20px) saturate(180%)',
                borderRadius: isMobile ? '12px' : '16px',
                padding: isMobile ? '10px 12px' : '16px',
                border: `1px solid ${colors.borderPrimary}`,
                boxShadow: `0 4px 24px ${colors.rgba('black', 0.1)}`,
            }}>
                {isMobile ? (
                    <>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <div
                                style={{
                                    flex: 1, display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer',
                                    padding: '6px 10px', borderRadius: '8px',
                                    background: filterExpanded ? colors.rgba('gold', 0.08) : colors.rgba('bgContainer', 0.5),
                                    border: filterExpanded ? `1px solid ${colors.borderGold}` : `1px solid ${colors.borderSecondary}`,
                                    transition: 'all 200ms', minWidth: 0,
                                }}
                                onClick={() => setFilterExpanded(!filterExpanded)}
                            >
                                <FilterOutlined style={{ color: colors.goldPrimary, fontSize: '13px', flexShrink: 0 }} />
                                <span style={{
                                    fontSize: '12px', color: colors.textSecondary, flex: 1,
                                    overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                                }}>
                                    {filterSummary}
                                </span>
                                {filterExpanded ? (
                                    <UpOutlined style={{ fontSize: '10px', color: colors.textTertiary, flexShrink: 0 }} />
                                ) : (
                                    <DownOutlined style={{ fontSize: '10px', color: colors.textTertiary, flexShrink: 0 }} />
                                )}
                            </div>
                            <Dropdown trigger={['click']} placement="bottomRight" menu={{ items: mobileActionItems }}>
                                <Button
                                    type="text"
                                    icon={<MoreOutlined />}
                                    size="middle"
                                    style={{
                                        background: batchSelect.isBatchMode ? colors.rgba('gold', 0.15) : colors.rgba('bgContainer', 0.8),
                                        border: batchSelect.isBatchMode ? `1px solid ${colors.borderGold}` : `1px solid ${colors.borderPrimary}`,
                                        borderRadius: '10px',
                                        color: batchSelect.isBatchMode ? colors.goldPrimary : colors.textSecondary,
                                        height: actionButtonEdge, minWidth: actionButtonEdge,
                                        display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                                    }}
                                />
                            </Dropdown>
                        </div>

                        {filterExpanded && (
                            <div style={{ marginTop: '10px' }}>
                                <Filter
                                    initialValues={filter}
                                    onChange={(values) => navigate({ search: values as any })}
                                    fields={filterFields}
                                    compact={true}
                                />
                            </div>
                        )}
                    </>
                ) : (
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px' }}>
                        <div style={{ flex: 1, minWidth: 0 }}>
                            <Filter
                                initialValues={filter}
                                onChange={(values) => navigate({ search: values as any })}
                                fields={filterFields}
                                compact={false}
                            />
                        </div>
                        <div style={{ display: 'flex', gap: '8px', flexShrink: 0 }}>
                            <Tooltip title="扫描本地视频文件" placement="bottom">
                                <Button
                                    type="text"
                                    icon={<FolderOpenOutlined />}
                                    onClick={handleScan}
                                    loading={scanning}
                                    size="large"
                                    className="tissue-hover-action-btn"
                                    style={actionBtnStyle}
                                />
                            </Tooltip>
                            <Tooltip title="刷新数据" placement="bottom">
                                <Button
                                    type="text"
                                    icon={<ReloadOutlined spin={refreshing} />}
                                    onClick={handleRefresh}
                                    loading={refreshing}
                                    size="large"
                                    className="tissue-hover-action-btn"
                                    style={actionBtnStyle}
                                />
                            </Tooltip>
                            <Tooltip title={batchSelect.isBatchMode ? "退出批量选择" : "批量选择"} placement="bottom">
                                <Button
                                    type="text"
                                    icon={batchSelect.isBatchMode ? <CheckSquareOutlined /> : <BorderOutlined />}
                                    onClick={batchSelect.toggleBatchMode}
                                    size="large"
                                    className="tissue-hover-action-btn"
                                    style={{
                                        ...actionBtnStyle,
                                        background: batchSelect.isBatchMode ? colors.rgba('gold', 0.15) : colors.rgba('bgContainer', 0.8),
                                        border: batchSelect.isBatchMode ? `1px solid ${colors.borderGold}` : `1px solid ${colors.borderPrimary}`,
                                        color: batchSelect.isBatchMode ? colors.goldPrimary : colors.textSecondary,
                                    }}
                                />
                            </Tooltip>
                        </div>
                    </div>
                )}
            </div>
            <Await promise={data} fallback={<HomeSkeleton />}>
                {(data = []) => {
                    const videos = normalizeVideos(data);
                    const minRank = Number(filter.rank ?? 0);
                    const filteredVideos = videos.filter((item: any) => item.rank >= minRank);
                    const sortedVideos = sortVideos(filteredVideos, filter.sort_by || 'rank', filter.sort_order || 'desc');

                    const batchVideos: BatchSelectVideo[] = sortedVideos.map((item: any) => ({
                        num: item.num, title: item.title, cover: item.cover, url: item.url,
                        is_zh: item.is_zh, is_uncensored: item.is_uncensored,
                        rank: item.rank, publish_date: item.publish_date, source: 'JavDB',
                    }));

                    // 更新当前视频列表（用于全选）- 在渲染阶段安全地设置 ref
                    // 使用 queueMicrotask 确保不阻塞渲染
                    queueMicrotask(() => { currentVideosRef.current = batchVideos; });

                    return sortedVideos.length > 0 ? (
                        <Row className={'mt-2 cursor-pointer'} gutter={[16, 16]}>
                            {sortedVideos.map((item: any, index: number) => {
                                const isSelected = batchSelect.isSelected(item.num);
                                const batchVideo: BatchSelectVideo = batchVideos[index];

                                return (
                                    <Col
                                        key={item.url}
                                        span={24}
                                        md={12}
                                        lg={6}
                                        className={`tissue-animate-in tissue-stagger-${(index % 8) + 1}`}
                                        onClick={() => {
                                            if (batchSelect.isBatchMode) {
                                                batchSelect.toggleVideoSelection(batchVideo);
                                            } else {
                                                navigate({
                                                    to: '/home/detail',
                                                    search: { source: 'JavDB', url: item.url, num: item.num }
                                                });
                                            }
                                        }}
                                    >
                                        <div style={{ position: 'relative', height: '100%' }}>
                                            {batchSelect.isBatchMode && (
                                                <div style={{
                                                    position: 'absolute', top: 12, left: 12, zIndex: 20,
                                                    background: colors.rgba('bgContainer', 0.95), backdropFilter: 'blur(10px)',
                                                    borderRadius: '8px', padding: '4px',
                                                    border: `1px solid ${colors.borderPrimary}`,
                                                    boxShadow: `0 2px 8px ${colors.rgba('black', 0.2)}`,
                                                }}>
                                                    <Checkbox
                                                        checked={isSelected}
                                                        onClick={(e) => e.stopPropagation()}
                                                        onChange={() => batchSelect.toggleVideoSelection(batchVideo)}
                                                        style={{ transform: 'scale(1.15)' }}
                                                    />
                                                </div>
                                            )}
                                            <div style={{
                                                borderRadius: '18px', overflow: 'hidden',
                                                border: isSelected ? `3px solid ${colors.goldPrimary}` : '3px solid transparent',
                                                boxShadow: isSelected ? `0 0 0 1px ${colors.rgba('gold', 0.2)}, 0 8px 24px ${colors.rgba('gold', 0.3)}` : 'none',
                                                transition: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
                                                opacity: batchSelect.isBatchMode && !isSelected ? 0.6 : 1,
                                                transform: isSelected ? 'scale(0.98)' : 'scale(1)',
                                            }}>
                                                <JavDBItem
                                                    item={item}
                                                    downloadStatus={statusMap[item.num] || 'none'}
                                                />
                                            </div>
                                        </div>
                                    </Col>
                                );
                            })}
                        </Row>
                    ) : (
                        <div
                            className="tissue-animate-in"
                            style={{
                                display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                                padding: '100px 40px',
                                background: `linear-gradient(135deg, ${colors.rgba('bgContainer', 0.8)} 0%, ${colors.rgba('black', 0.3)} 100%)`,
                                backdropFilter: 'blur(20px)', borderRadius: '20px',
                                border: `1px solid ${colors.borderPrimary}`,
                                boxShadow: `0 8px 32px ${colors.rgba('black', 0.1)}`,
                                marginTop: '60px', position: 'relative', overflow: 'hidden',
                            }}
                        >
                            <div style={{
                                position: 'absolute', top: -50, right: -50, width: 200, height: 200, borderRadius: '50%',
                                background: `radial-gradient(circle, ${colors.rgba('gold', 0.08)} 0%, transparent 70%)`,
                                pointerEvents: 'none',
                            }} />
                            <div style={{
                                position: 'absolute', bottom: -30, left: -30, width: 150, height: 150, borderRadius: '50%',
                                background: `radial-gradient(circle, ${colors.rgba('gold', 0.05)} 0%, transparent 70%)`,
                                pointerEvents: 'none',
                            }} />
                            <div style={{
                                width: 120, height: 120, borderRadius: '50%',
                                background: colors.rgba('gold', 0.08),
                                border: `2px solid ${colors.rgba('gold', 0.2)}`,
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                marginBottom: '32px', animation: 'tissue-glow-pulse 3s ease-in-out infinite',
                            }}>
                                <InboxOutlined style={{ fontSize: '56px', color: colors.goldPrimary }} />
                            </div>
                            <div style={{ fontSize: '22px', fontWeight: 600, color: colors.textPrimary, marginBottom: '12px', letterSpacing: '0.02em' }}>
                                没有找到符合条件的视频
                            </div>
                            <div style={{ fontSize: '15px', color: colors.textSecondary, textAlign: 'center', lineHeight: '1.6', maxWidth: '400px', marginBottom: '24px' }}>
                                {filter.rank > 0 ? '请尝试降低评分要求或调整其他筛选条件' : '请调整筛选条件重试，或者稍后再来看看'}
                            </div>
                            <div style={{
                                width: '60px', height: '3px',
                                background: `linear-gradient(90deg, transparent 0%, ${colors.goldPrimary} 50%, transparent 100%)`,
                                borderRadius: '2px',
                            }} />
                        </div>
                    )
                }}
            </Await>

            {/* 批量操作工具栏 */}
            <BatchActionBar
                visible={batchSelect.isBatchMode}
                selectedCount={batchSelect.selectedCount}
                totalCount={currentVideosRef.current.length}
                onSelectAll={() => batchSelect.selectAll(currentVideosRef.current)}
                onUnselectAll={batchSelect.unselectAll}
                onBatchDownload={() => setBatchDownloadModalVisible(true)}
                onExit={batchSelect.exitBatchMode}
            />

            {/* 批量下载弹窗 */}
            <BatchDownloadModal
                open={batchDownloadModalVisible}
                videos={batchSelect.getSelectedList()}
                sourceType="javdb"
                onCancel={() => setBatchDownloadModalVisible(false)}
                onComplete={(successCount) => {
                    setBatchDownloadModalVisible(false);
                    if (successCount > 0) {
                        batchSelect.exitBatchMode();
                    }
                }}
            />

            {/* 扫描结果弹窗 */}
            <ScanResultModal
                open={scanResultVisible}
                result={scanResult}
                onCancel={() => setScanResultVisible(false)}
            />
        </div>
    )
}

export default JavDB
