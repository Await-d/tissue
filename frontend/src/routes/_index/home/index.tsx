/*
 * @Author: Await
 * @Date: 2025-05-24 17:05:38
 * @LastEditors: Await
 * @LastEditTime: 2025-05-29 17:23:46
 * @Description: 请填写简介
 */
import Filter, { FilterField } from "./-components/filter.tsx";
import React from "react";
import { Col, message, Row, Button, Tooltip, Checkbox, App } from "antd";
import { ReloadOutlined, InboxOutlined, CheckSquareOutlined, BorderOutlined } from "@ant-design/icons";
import JavDBItem from "./-components/item.tsx";
import Selector from "../../../components/Selector";
import Slider from "../../../components/Slider";
import * as api from "../../../apis/home.ts";
import { Await, createFileRoute, redirect, useNavigate, useRouter } from "@tanstack/react-router";
import { useBatchSelect, type BatchSelectVideo } from "@/hooks/useBatchSelect";
import { BatchActionBar, BatchDownloadModal } from "@/components/BatchDownload";

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
    staleTime: 5 * 60 * 1000  // 5分钟后数据过期，允许重新获取
})

function JavDB() {
    const { data } = Route.useLoaderData()
    const filter = Route.useSearch<any>()
    const navigate = useNavigate()
    const router = useRouter()
    const [refreshing, setRefreshing] = React.useState(false)

    // 批量选择相关状态
    const batchSelect = useBatchSelect();
    const [batchDownloadModalVisible, setBatchDownloadModalVisible] = React.useState(false);
    const [currentVideos, setCurrentVideos] = React.useState<BatchSelectVideo[]>([]);

    // 手动刷新数据
    const handleRefresh = async () => {
        setRefreshing(true)
        try {
            await router.invalidate()
            message.success('刷新成功')
        } catch (err) {
            message.error('刷新失败')
        } finally {
            setRefreshing(false)
        }
    }

    const filterFields: FilterField[] = [
        {
            dataIndex: 'video_type',
            label: '类型',
            component: (<Selector items={[
                { name: '有码', value: 'censored' },
                { name: '无码', value: 'uncensored' }]}
            />),
            span: { lg: 6, md: 12, xs: 24 }
        },
        {
            dataIndex: 'cycle',
            label: '周期',
            component: (<Selector items={[
                { name: '日榜', value: 'daily' },
                { name: '周榜', value: 'weekly' },
                { name: '月榜', value: 'monthly' }]}
            />),
            span: { lg: 6, md: 12, xs: 24 }
        },
        {
            dataIndex: 'sort_by',
            label: '排序',
            component: (<Selector items={[
                { name: '评分', value: 'rank' },
                { name: '评论数', value: 'rank_count' },
                { name: '发布日期', value: 'publish_date' }]}
            />),
            span: { lg: 6, md: 12, xs: 24 }
        },
        {
            dataIndex: 'sort_order',
            label: '顺序',
            component: (<Selector items={[
                { name: '降序', value: 'desc' },
                { name: '升序', value: 'asc' }]}
            />),
            span: { lg: 6, md: 12, xs: 24 }
        },
        {
            dataIndex: 'rank',
            label: '评分',
            component: (<Slider step={0.1} min={0} max={5} />),
            span: { lg: 24, md: 24, xs: 24 }
        },
    ]

    // 排序函数
    const sortVideos = (videos: any[], sortBy: string, sortOrder: string) => {
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
    };

    // 兼容缓存数据与实时爬取字段，统一映射到 rank/rank_count/publish_date
    const normalizeVideos = (videos: any[]) => {
        if (!Array.isArray(videos)) return [];
        return videos.map((video) => {
            const rank = Number(video.rank ?? video.rating ?? 0) || 0;
            const rankCount = Number(video.rank_count ?? video.comments_count ?? video.comments ?? 0) || 0;
            const publishDate = video.publish_date ?? video.release_date ?? '';
            return { ...video, rank, rank_count: rankCount, publish_date: publishDate };
        });
    };

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                <div style={{ flex: 1 }}>
                    <Filter initialValues={filter} onChange={(values, field) => {
                        return navigate({ search: values as any })
                    }} fields={filterFields} />
                </div>
                <Tooltip title="刷新数据">
                    <Button
                        type="text"
                        icon={<ReloadOutlined spin={refreshing} style={{ color: '#d4a852' }} />}
                        onClick={handleRefresh}
                        loading={refreshing}
                        style={{
                            marginLeft: '8px',
                            marginTop: '4px',
                            background: 'rgba(26, 26, 29, 0.6)',
                            border: '1px solid rgba(255, 255, 255, 0.08)',
                            borderRadius: '10px',
                            transition: 'all 250ms cubic-bezier(0.4, 0, 0.2, 1)',
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.background = 'rgba(212, 168, 82, 0.15)';
                            e.currentTarget.style.borderColor = 'rgba(212, 168, 82, 0.3)';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.background = 'rgba(26, 26, 29, 0.6)';
                            e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.08)';
                        }}
                    />
                </Tooltip>
                <Tooltip title={batchSelect.isBatchMode ? "退出批量选择" : "批量选择"}>
                    <Button
                        type="text"
                        icon={batchSelect.isBatchMode ? <CheckSquareOutlined style={{ color: '#d4a852' }} /> : <BorderOutlined style={{ color: '#d4a852' }} />}
                        onClick={batchSelect.toggleBatchMode}
                        style={{
                            marginLeft: '8px',
                            marginTop: '4px',
                            background: batchSelect.isBatchMode ? 'rgba(212, 168, 82, 0.15)' : 'rgba(26, 26, 29, 0.6)',
                            border: batchSelect.isBatchMode ? '1px solid rgba(212, 168, 82, 0.3)' : '1px solid rgba(255, 255, 255, 0.08)',
                            borderRadius: '10px',
                            transition: 'all 250ms cubic-bezier(0.4, 0, 0.2, 1)',
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.background = 'rgba(212, 168, 82, 0.15)';
                            e.currentTarget.style.borderColor = 'rgba(212, 168, 82, 0.3)';
                        }}
                        onMouseLeave={(e) => {
                            if (!batchSelect.isBatchMode) {
                                e.currentTarget.style.background = 'rgba(26, 26, 29, 0.6)';
                                e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.08)';
                            }
                        }}
                    />
                </Tooltip>
            </div>
            <Await promise={data} fallback={(
                <Row className={'mt-2'} gutter={[12, 12]}>
                    {[...Array(8)].map((_, index) => (
                        <Col key={index} span={24} md={12} lg={6} className={`tissue-animate-in tissue-stagger-${(index % 8) + 1}`}>
                            <div style={{
                                background: '#1a1a1d',
                                borderRadius: '14px',
                                overflow: 'hidden',
                                border: '1px solid rgba(255, 255, 255, 0.06)',
                                boxShadow: '0 4px 16px rgba(0, 0, 0, 0.4)',
                            }}>
                                <div style={{
                                    aspectRatio: '16/10',
                                    background: 'linear-gradient(90deg, #222226 25%, #2a2a2e 50%, #222226 75%)',
                                    backgroundSize: '200% 100%',
                                    animation: 'tissue-shimmer 1.5s infinite',
                                }} />
                                <div style={{ padding: '14px 16px' }}>
                                    <div style={{
                                        width: '60%',
                                        height: '12px',
                                        background: 'linear-gradient(90deg, #222226 25%, #2a2a2e 50%, #222226 75%)',
                                        backgroundSize: '200% 100%',
                                        animation: 'tissue-shimmer 1.5s infinite',
                                        borderRadius: '6px',
                                        marginBottom: '8px',
                                    }} />
                                    <div style={{
                                        width: '90%',
                                        height: '14px',
                                        background: 'linear-gradient(90deg, #222226 25%, #2a2a2e 50%, #222226 75%)',
                                        backgroundSize: '200% 100%',
                                        animation: 'tissue-shimmer 1.5s infinite',
                                        borderRadius: '6px',
                                        marginBottom: '6px',
                                    }} />
                                    <div style={{
                                        width: '75%',
                                        height: '14px',
                                        background: 'linear-gradient(90deg, #222226 25%, #2a2a2e 50%, #222226 75%)',
                                        backgroundSize: '200% 100%',
                                        animation: 'tissue-shimmer 1.5s infinite',
                                        borderRadius: '6px',
                                    }} />
                                </div>
                            </div>
                        </Col>
                    ))}
                </Row>
            )}>
                {(data = []) => {
                    // 兼容缓存数据字段差异后再过滤排序
                    const videos = normalizeVideos(data);
                    const minRank = Number(filter.rank ?? 0);
                    const filteredVideos = videos.filter((item: any) => item.rank >= minRank);
                    const sortedVideos = sortVideos(filteredVideos, filter.sort_by || 'rank', filter.sort_order || 'desc');

                    // 转换为批量选择格式
                    const batchVideos: BatchSelectVideo[] = sortedVideos.map((item: any) => ({
                        num: item.num,
                        title: item.title,
                        cover: item.cover,
                        url: item.url,
                        is_zh: item.is_zh,
                        is_uncensored: item.is_uncensored,
                        rank: item.rank,
                        publish_date: item.publish_date,
                        source: 'JavDB',
                    }));

                    // 更新当前视频列表（用于全选）
                    React.useEffect(() => {
                        setCurrentVideos(batchVideos);
                    }, [sortedVideos.length]);

                    return sortedVideos.length > 0 ? (
                        <Row className={'mt-2 cursor-pointer'} gutter={[12, 12]}>
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
                                        <div style={{ position: 'relative' }}>
                                            {batchSelect.isBatchMode && (
                                                <div style={{
                                                    position: 'absolute',
                                                    top: 10,
                                                    left: 10,
                                                    zIndex: 10,
                                                }}>
                                                    <Checkbox
                                                        checked={isSelected}
                                                        onClick={(e) => e.stopPropagation()}
                                                        onChange={() => batchSelect.toggleVideoSelection(batchVideo)}
                                                        style={{
                                                            transform: 'scale(1.2)',
                                                        }}
                                                    />
                                                </div>
                                            )}
                                            <div style={{
                                                borderRadius: '14px',
                                                overflow: 'hidden',
                                                border: isSelected ? '2px solid #d4a852' : '2px solid transparent',
                                                transition: 'all 0.2s ease',
                                                opacity: batchSelect.isBatchMode && !isSelected ? 0.7 : 1,
                                            }}>
                                                <JavDBItem item={item} />
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
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                justifyContent: 'center',
                                padding: '80px 20px',
                                background: 'rgba(26, 26, 29, 0.6)',
                                borderRadius: '14px',
                                border: '1px solid rgba(255, 255, 255, 0.06)',
                                marginTop: '40px',
                            }}
                        >
                            <InboxOutlined style={{
                                fontSize: '64px',
                                color: 'rgba(212, 168, 82, 0.3)',
                                marginBottom: '20px',
                            }} />
                            <div style={{
                                fontSize: '18px',
                                fontWeight: 500,
                                color: '#a0a0a8',
                                marginBottom: '8px',
                                letterSpacing: '0.02em',
                            }}>
                                没有找到符合条件的视频
                            </div>
                            <div style={{
                                fontSize: '14px',
                                color: '#6a6a72',
                                textAlign: 'center',
                                lineHeight: '1.6',
                            }}>
                                {filter.rank > 0 ? '请尝试降低评分要求或调整其他筛选条件' : '请调整筛选条件重试'}
                            </div>
                        </div>
                    )
                }}
            </Await>

            {/* 批量操作工具栏 */}
            <BatchActionBar
                visible={batchSelect.isBatchMode}
                selectedCount={batchSelect.selectedCount}
                totalCount={currentVideos.length}
                onSelectAll={() => batchSelect.selectAll(currentVideos)}
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
                onComplete={(successCount, failCount) => {
                    setBatchDownloadModalVisible(false);
                    if (successCount > 0) {
                        batchSelect.exitBatchMode();
                    }
                }}
            />
        </div>
    )
}

export default JavDB
