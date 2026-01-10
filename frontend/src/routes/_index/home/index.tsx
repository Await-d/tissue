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
import { useThemeColors } from '../../../hooks/useThemeColors';

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
    const colors = useThemeColors();
    const { data } = Route.useLoaderData()
    const filter = Route.useSearch<any>()
    const navigate = useNavigate()
    const router = useRouter()
    const [refreshing, setRefreshing] = React.useState(false)

    // 批量选择相关状态
    const batchSelect = useBatchSelect();
    const [batchDownloadModalVisible, setBatchDownloadModalVisible] = React.useState(false);
    const currentVideosRef = React.useRef<BatchSelectVideo[]>([]);

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
        <div style={{ 
            minHeight: '100vh',
            padding: '0 0 80px 0',
        }}>
            {/* 顶部筛选栏 - 玻璃态效果 */}
            <div style={{ 
                position: 'sticky',
                top: 0,
                zIndex: 100,
                marginBottom: '20px',
                background: colors.rgba('bgContainer', 0.85),
                backdropFilter: 'blur(20px) saturate(180%)',
                borderRadius: '16px',
                padding: '16px',
                border: `1px solid ${colors.borderPrimary}`,
                boxShadow: `0 4px 24px ${colors.rgba('black', 0.1)}`,
            }}>
                <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'flex-start',
                    gap: '12px',
                }}>
                    {/* 筛选器 */}
                    <div style={{ flex: 1 }}>
                        <Filter 
                            initialValues={filter} 
                            onChange={(values, field) => {
                                return navigate({ search: values as any })
                            }} 
                            fields={filterFields} 
                        />
                    </div>

                    {/* 操作按钮组 */}
                    <div style={{ 
                        display: 'flex', 
                        gap: '8px',
                        flexShrink: 0,
                    }}>
                        {/* 刷新按钮 */}
                        <Tooltip title="刷新数据" placement="bottom">
                            <Button
                                type="text"
                                icon={<ReloadOutlined spin={refreshing} />}
                                onClick={handleRefresh}
                                loading={refreshing}
                                size="large"
                                style={{
                                    background: colors.rgba('bgContainer', 0.8),
                                    border: `1px solid ${colors.borderPrimary}`,
                                    borderRadius: '12px',
                                    color: colors.textSecondary,
                                    height: 44,
                                    minWidth: 44,
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    transition: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
                                }}
                                onMouseEnter={(e) => {
                                    e.currentTarget.style.background = colors.rgba('gold', 0.12);
                                    e.currentTarget.style.borderColor = colors.borderGold;
                                    e.currentTarget.style.color = colors.goldPrimary;
                                    e.currentTarget.style.transform = 'scale(1.05)';
                                }}
                                onMouseLeave={(e) => {
                                    e.currentTarget.style.background = colors.rgba('bgContainer', 0.8);
                                    e.currentTarget.style.borderColor = colors.borderPrimary;
                                    e.currentTarget.style.color = colors.textSecondary;
                                    e.currentTarget.style.transform = 'scale(1)';
                                }}
                            />
                        </Tooltip>

                        {/* 批量选择按钮 */}
                        <Tooltip 
                            title={batchSelect.isBatchMode ? "退出批量选择" : "批量选择"} 
                            placement="bottom"
                        >
                            <Button
                                type="text"
                                icon={batchSelect.isBatchMode ? 
                                    <CheckSquareOutlined /> : 
                                    <BorderOutlined />
                                }
                                onClick={batchSelect.toggleBatchMode}
                                size="large"
                                style={{
                                    background: batchSelect.isBatchMode ? 
                                        colors.rgba('gold', 0.15) : 
                                        colors.rgba('bgContainer', 0.8),
                                    border: batchSelect.isBatchMode ? 
                                        `1px solid ${colors.borderGold}` : 
                                        `1px solid ${colors.borderPrimary}`,
                                    borderRadius: '12px',
                                    color: batchSelect.isBatchMode ? 
                                        colors.goldPrimary : 
                                        colors.textSecondary,
                                    height: 44,
                                    minWidth: 44,
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    transition: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
                                }}
                                onMouseEnter={(e) => {
                                    e.currentTarget.style.background = colors.rgba('gold', 0.15);
                                    e.currentTarget.style.borderColor = colors.borderGold;
                                    e.currentTarget.style.color = colors.goldPrimary;
                                    e.currentTarget.style.transform = 'scale(1.05)';
                                }}
                                onMouseLeave={(e) => {
                                    if (!batchSelect.isBatchMode) {
                                        e.currentTarget.style.background = colors.rgba('bgContainer', 0.8);
                                        e.currentTarget.style.borderColor = colors.borderPrimary;
                                        e.currentTarget.style.color = colors.textSecondary;
                                    }
                                    e.currentTarget.style.transform = 'scale(1)';
                                }}
                            />
                        </Tooltip>
                    </div>
                </div>
            </div>
            <Await promise={data} fallback={(
                <Row className={'mt-2'} gutter={[16, 16]}>
                    {[...Array(8)].map((_, index) => (
                        <Col 
                            key={index} 
                            span={24} 
                            md={12} 
                            lg={6} 
                            className={`tissue-animate-in tissue-stagger-${(index % 8) + 1}`}
                        >
                            <div style={{
                                background: colors.bgContainer,
                                borderRadius: '16px',
                                overflow: 'hidden',
                                border: `1px solid ${colors.borderSecondary}`,
                                boxShadow: `0 4px 12px ${colors.rgba('black', 0.15)}`,
                            }}>
                                {/* 封面骨架 - 更丰富的动画 */}
                                <div style={{
                                    aspectRatio: '16/10',
                                    position: 'relative',
                                    overflow: 'hidden',
                                    background: colors.bgSpotlight,
                                }}>
                                    <div style={{
                                        position: 'absolute',
                                        inset: 0,
                                        background: `linear-gradient(
                                            90deg, 
                                            transparent 0%, 
                                            ${colors.rgba('gold', 0.08)} 50%, 
                                            transparent 100%
                                        )`,
                                        backgroundSize: '200% 100%',
                                        animation: 'tissue-shimmer 2s ease-in-out infinite',
                                    }} />
                                    {/* 模拟评分角标 */}
                                    <div style={{
                                        position: 'absolute',
                                        top: 14,
                                        left: 14,
                                        width: 60,
                                        height: 28,
                                        background: colors.rgba('gold', 0.15),
                                        borderRadius: 10,
                                    }} />
                                </div>

                                {/* 内容骨架 */}
                                <div style={{ padding: '16px 18px' }}>
                                    {/* 番号标签骨架 */}
                                    <div style={{
                                        width: '40%',
                                        height: 20,
                                        background: colors.rgba('gold', 0.12),
                                        borderRadius: 6,
                                        marginBottom: 10,
                                        position: 'relative',
                                        overflow: 'hidden',
                                    }}>
                                        <div style={{
                                            position: 'absolute',
                                            inset: 0,
                                            background: `linear-gradient(
                                                90deg, 
                                                transparent 0%, 
                                                ${colors.rgba('white', 0.08)} 50%, 
                                                transparent 100%
                                            )`,
                                            backgroundSize: '200% 100%',
                                            animation: 'tissue-shimmer 2s ease-in-out infinite 0.2s',
                                        }} />
                                    </div>

                                    {/* 标题骨架 */}
                                    <div style={{
                                        width: '100%',
                                        height: 16,
                                        background: colors.bgSpotlight,
                                        borderRadius: 6,
                                        marginBottom: 8,
                                        position: 'relative',
                                        overflow: 'hidden',
                                    }}>
                                        <div style={{
                                            position: 'absolute',
                                            inset: 0,
                                            background: `linear-gradient(
                                                90deg, 
                                                transparent 0%, 
                                                ${colors.rgba('white', 0.05)} 50%, 
                                                transparent 100%
                                            )`,
                                            backgroundSize: '200% 100%',
                                            animation: 'tissue-shimmer 2s ease-in-out infinite 0.4s',
                                        }} />
                                    </div>
                                    <div style={{
                                        width: '75%',
                                        height: 16,
                                        background: colors.bgSpotlight,
                                        borderRadius: 6,
                                        marginBottom: 14,
                                        position: 'relative',
                                        overflow: 'hidden',
                                    }}>
                                        <div style={{
                                            position: 'absolute',
                                            inset: 0,
                                            background: `linear-gradient(
                                                90deg, 
                                                transparent 0%, 
                                                ${colors.rgba('white', 0.05)} 50%, 
                                                transparent 100%
                                            )`,
                                            backgroundSize: '200% 100%',
                                            animation: 'tissue-shimmer 2s ease-in-out infinite 0.6s',
                                        }} />
                                    </div>

                                    {/* 底部信息骨架 */}
                                    <div style={{
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        paddingTop: 12,
                                        borderTop: `1px solid ${colors.borderSecondary}`,
                                    }}>
                                        <div style={{
                                            width: '50%',
                                            height: 14,
                                            background: colors.bgSpotlight,
                                            borderRadius: 6,
                                            position: 'relative',
                                            overflow: 'hidden',
                                        }}>
                                            <div style={{
                                                position: 'absolute',
                                                inset: 0,
                                                background: `linear-gradient(
                                                    90deg, 
                                                    transparent 0%, 
                                                    ${colors.rgba('white', 0.05)} 50%, 
                                                    transparent 100%
                                                )`,
                                                backgroundSize: '200% 100%',
                                                animation: 'tissue-shimmer 2s ease-in-out infinite 0.8s',
                                            }} />
                                        </div>
                                        <div style={{
                                            width: '25%',
                                            height: 14,
                                            background: colors.bgSpotlight,
                                            borderRadius: 6,
                                            position: 'relative',
                                            overflow: 'hidden',
                                        }}>
                                            <div style={{
                                                position: 'absolute',
                                                inset: 0,
                                                background: `linear-gradient(
                                                    90deg, 
                                                    transparent 0%, 
                                                    ${colors.rgba('white', 0.05)} 50%, 
                                                    transparent 100%
                                                )`,
                                                backgroundSize: '200% 100%',
                                                animation: 'tissue-shimmer 2s ease-in-out infinite 1s',
                                            }} />
                                        </div>
                                    </div>
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
                    currentVideosRef.current = batchVideos;

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
                                        <div style={{ 
                                            position: 'relative',
                                            height: '100%',
                                        }}>
                                            {/* 批量选择复选框 */}
                                            {batchSelect.isBatchMode && (
                                                <div style={{
                                                    position: 'absolute',
                                                    top: 12,
                                                    left: 12,
                                                    zIndex: 20,
                                                    background: colors.rgba('bgContainer', 0.95),
                                                    backdropFilter: 'blur(10px)',
                                                    borderRadius: '8px',
                                                    padding: '4px',
                                                    border: `1px solid ${colors.borderPrimary}`,
                                                    boxShadow: `0 2px 8px ${colors.rgba('black', 0.2)}`,
                                                }}>
                                                    <Checkbox
                                                        checked={isSelected}
                                                        onClick={(e) => e.stopPropagation()}
                                                        onChange={() => batchSelect.toggleVideoSelection(batchVideo)}
                                                        style={{
                                                            transform: 'scale(1.15)',
                                                        }}
                                                    />
                                                </div>
                                            )}
                                            
                                            {/* 选中状态的外边框 */}
                                            <div style={{
                                                borderRadius: '18px',
                                                overflow: 'hidden',
                                                border: isSelected ? 
                                                    `3px solid ${colors.goldPrimary}` : 
                                                    '3px solid transparent',
                                                boxShadow: isSelected ? 
                                                    `0 0 0 1px ${colors.rgba('gold', 0.2)}, 0 8px 24px ${colors.rgba('gold', 0.3)}` : 
                                                    'none',
                                                transition: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
                                                opacity: batchSelect.isBatchMode && !isSelected ? 0.6 : 1,
                                                transform: isSelected ? 'scale(0.98)' : 'scale(1)',
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
                                padding: '100px 40px',
                                background: `linear-gradient(135deg, ${colors.rgba('bgContainer', 0.8)} 0%, ${colors.rgba('black', 0.3)} 100%)`,
                                backdropFilter: 'blur(20px)',
                                borderRadius: '20px',
                                border: `1px solid ${colors.borderPrimary}`,
                                boxShadow: `0 8px 32px ${colors.rgba('black', 0.1)}`,
                                marginTop: '60px',
                                position: 'relative',
                                overflow: 'hidden',
                            }}
                        >
                            {/* 装饰性背景元素 */}
                            <div style={{
                                position: 'absolute',
                                top: -50,
                                right: -50,
                                width: 200,
                                height: 200,
                                borderRadius: '50%',
                                background: `radial-gradient(circle, ${colors.rgba('gold', 0.08)} 0%, transparent 70%)`,
                                pointerEvents: 'none',
                            }} />
                            <div style={{
                                position: 'absolute',
                                bottom: -30,
                                left: -30,
                                width: 150,
                                height: 150,
                                borderRadius: '50%',
                                background: `radial-gradient(circle, ${colors.rgba('gold', 0.05)} 0%, transparent 70%)`,
                                pointerEvents: 'none',
                            }} />

                            {/* 图标容器 - 带动画效果 */}
                            <div style={{
                                width: 120,
                                height: 120,
                                borderRadius: '50%',
                                background: colors.rgba('gold', 0.08),
                                border: `2px solid ${colors.rgba('gold', 0.2)}`,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                marginBottom: '32px',
                                animation: 'tissue-glow-pulse 3s ease-in-out infinite',
                            }}>
                                <InboxOutlined style={{
                                    fontSize: '56px',
                                    color: colors.goldPrimary,
                                }} />
                            </div>

                            {/* 标题 */}
                            <div style={{
                                fontSize: '22px',
                                fontWeight: 600,
                                color: colors.textPrimary,
                                marginBottom: '12px',
                                letterSpacing: '0.02em',
                            }}>
                                没有找到符合条件的视频
                            </div>

                            {/* 描述文字 */}
                            <div style={{
                                fontSize: '15px',
                                color: colors.textSecondary,
                                textAlign: 'center',
                                lineHeight: '1.6',
                                maxWidth: '400px',
                                marginBottom: '24px',
                            }}>
                                {filter.rank > 0 
                                    ? '请尝试降低评分要求或调整其他筛选条件' 
                                    : '请调整筛选条件重试，或者稍后再来看看'}
                            </div>

                            {/* 装饰性分割线 */}
                            <div style={{
                                width: '60px',
                                height: '3px',
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
