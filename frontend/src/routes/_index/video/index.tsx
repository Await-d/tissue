import {useRequest} from "ahooks";
import * as api from "../../../apis/video";
import {
    Card,
    Col,
    Empty,
    FloatButton,
    Row,
    Skeleton,
    Space,
    Tag,
    Tooltip,
    Statistic,
    Button,
    Dropdown,
    Badge,
    Checkbox,
    Modal,
    message
} from "antd";
import VideoCover from "../../../components/VideoCover";
import React, {useMemo, useState} from "react";
import {createPortal} from "react-dom";
import {
    FilterOutlined,
    RedoOutlined,
    SearchOutlined,
    EditOutlined,
    DeleteOutlined,
    StarOutlined,
    SortAscendingOutlined,
    ClockCircleOutlined,
    TrophyOutlined,
    VideoCameraOutlined,
    MessageOutlined,
    SafetyOutlined,
    HighlightOutlined,
    CheckSquareOutlined,
    DownloadOutlined
} from "@ant-design/icons";
import VideoFilterModal, {FilterParams} from "./-components/filter.tsx";
import {createFileRoute, Link, useRouter} from "@tanstack/react-router";
import VideoDetail from "../../../components/VideoDetail";
import BatchOperations from "../../../components/BatchOperations";
import TagEditModal from "../../../components/BatchOperations/TagEditModal";
import { useBatchSelection } from "../../../hooks/useBatchSelection";
import FavoriteButton from "../../../components/FavoriteButton";
import { batchAddFavorites } from "../../../apis/favorite";

export const Route = createFileRoute('/_index/video/')({
    component: Video,
})

type SortType = 'time' | 'rating';

function Video() {

    const {data = [], loading, run, refresh} = useRequest(api.getVideos)
    const [selected, setSelected] = useState<string | undefined>()
    const [filterOpen, setFilterOpen] = useState(false)
    const [filterParams, setFilterParams] = useState<FilterParams>({})
    const [quickFilters, setQuickFilters] = useState<{
        zh?: boolean;
        uncensored?: boolean;
        hd?: boolean;
    }>({})
    const [sortBy, setSortBy] = useState<SortType>('time')
    const {navigate} = useRouter()
    
    // Batch selection state
    const [batchMode, setBatchMode] = useState(false)
    const [tagModalOpen, setTagModalOpen] = useState(false)
    const [lastSelectedIndex, setLastSelectedIndex] = useState<number | null>(null)

    const actors = useMemo(() => {
        const actors: any[] = []
        data.forEach((video: any) => {
            video.actors.forEach((actor: any) => {
                const exist = actors.find(i => i.name == actor.name)
                if (exist) {
                    exist.count = exist.count + 1
                } else {
                    actor.count = 1
                    actors.push(actor)
                }
            })
        })
        return actors
    }, [data])

    // Batch selection hook
    const {
        selectedIds,
        selectedItems,
        isSelected,
        toggleSelection,
        toggleAll,
        selectRange,
        clearSelection,
        isAllSelected,
        selectedCount
    } = useBatchSelection<any>({
        items: data,
        getItemId: (video) => video.path
    })

    // Statistics calculation
    const statistics = useMemo(() => {
        return {
            total: data.length,
            zh: data.filter((v: any) => v.is_zh).length,
            uncensored: data.filter((v: any) => v.is_uncensored).length,
            hd: data.filter((v: any) => v.is_hd || v.quality === 'HD' || v.quality === '4K').length,
        }
    }, [data])

    const videos = useMemo(() => {
        let filtered = data.filter((item: any) => {
            // Text filter
            if (filterParams.title) {
                if (!item.title.toUpperCase().includes(filterParams.title.toUpperCase())) {
                    return false
                }
            }
            // Actor filter
            if (filterParams.actors?.length) {
                const hasActor = item.actors.map((i: any) => i.name).filter((i: string) => filterParams.actors?.includes(i)).length > 0
                if (!hasActor) return false
            }
            // Quick filters
            if (quickFilters.zh && !item.is_zh) return false
            if (quickFilters.uncensored && !item.is_uncensored) return false
            if (quickFilters.hd && !(item.is_hd || item.quality === 'HD' || item.quality === '4K')) return false

            return true
        })

        // Sorting
        if (sortBy === 'time') {
            filtered = [...filtered].sort((a: any, b: any) => {
                const timeA = a.created_at || a.date || 0
                const timeB = b.created_at || b.date || 0
                return timeB - timeA
            })
        } else if (sortBy === 'rating') {
            filtered = [...filtered].sort((a: any, b: any) => {
                const ratingA = a.rating || 0
                const ratingB = b.rating || 0
                return ratingB - ratingA
            })
        }

        return filtered
    }, [filterParams, quickFilters, sortBy, data])

    const hasFilter = !!filterParams.title || !!filterParams.actors?.length ||
                      Object.values(quickFilters).some(v => v)

    const toggleQuickFilter = (key: 'zh' | 'uncensored' | 'hd') => {
        setQuickFilters(prev => ({
            ...prev,
            [key]: !prev[key]
        }))
    }

    const handleCardAction = (e: React.MouseEvent, action: string, video: any) => {
        e.stopPropagation()
        switch (action) {
            case 'edit':
                setSelected(video.path)
                break
            case 'delete':
                // TODO: Implement delete functionality
                console.log('Delete video:', video.path)
                break
            case 'favorite':
                // TODO: Implement favorite functionality
                console.log('Favorite video:', video.path)
                break
        }
    }

    // Batch operations handlers
    const handleCardClick = (e: React.MouseEvent, video: any, index: number) => {
        if (!batchMode) {
            setSelected(video.path)
            return
        }

        // Shift key for range selection
        if (e.shiftKey && lastSelectedIndex !== null) {
            const startIndex = Math.min(lastSelectedIndex, index)
            const endIndex = Math.max(lastSelectedIndex, index)
            for (let i = startIndex; i <= endIndex; i++) {
                const videoId = videos[i].path
                if (!isSelected(videoId)) {
                    toggleSelection(videoId)
                }
            }
        } else {
            toggleSelection(video.path)
        }
        setLastSelectedIndex(index)
    }

    const handleBatchDelete = () => {
        message.info('批量删除功能开发中')
    }

    const handleBatchEditTags = () => {
        setTagModalOpen(true)
    }

    const handleTagsUpdate = (tags: string[]) => {
        message.info('批量标签更新功能开发中')
        setTagModalOpen(false)
        clearSelection()
    }

    const handleBatchFavorite = async () => {
        try {
            const videoNums = selectedItems.map(item => item.num)
            await batchAddFavorites(videoNums)
            message.success(`已收藏 ${selectedCount} 个视频`)
            clearSelection()
        } catch (error) {
            message.error('收藏失败')
        }
    }

    const handleBatchDownload = () => {
        message.info('批量下载功能开发中')
        clearSelection()
    }

    const toggleBatchMode = () => {
        setBatchMode(!batchMode)
        if (batchMode) {
            clearSelection()
        }
    }

    if (loading) {
        return (
            <Row gutter={[15, 15]}>
                {/* Statistics Skeleton */}
                <Col span={24}>
                    <Row gutter={[15, 15]}>
                        {[1, 2, 3, 4].map(i => (
                            <Col key={i} span={24} sm={12} lg={6}>
                                <Card>
                                    <Skeleton.Input active style={{width: '100%'}} />
                                </Card>
                            </Col>
                        ))}
                    </Row>
                </Col>
                {/* Video Cards Skeleton */}
                {[1, 2, 3, 4, 5, 6, 7, 8].map(i => (
                    <Col key={i} span={24} md={12} lg={6}>
                        <Card>
                            <Skeleton.Image active style={{width: '100%', height: 200}} />
                            <Skeleton active paragraph={{rows: 2}} style={{marginTop: 16}} />
                        </Card>
                    </Col>
                ))}
            </Row>
        )
    }

    return (
        <Row gutter={[15, 15]}>
            {/* Statistics Panel */}
            <Col span={24}>
                <Row gutter={[15, 15]}>
                    <Col span={24} sm={12} lg={6}>
                        <Card hoverable onClick={() => setQuickFilters({})}>
                            <Statistic
                                title="总视频数"
                                value={statistics.total}
                                prefix={<VideoCameraOutlined />}
                                valueStyle={{color: '#1890ff'}}
                            />
                        </Card>
                    </Col>
                    <Col span={24} sm={12} lg={6}>
                        <Card
                            hoverable
                            onClick={() => toggleQuickFilter('zh')}
                            style={{
                                borderColor: quickFilters.zh ? '#1890ff' : undefined,
                                borderWidth: quickFilters.zh ? 2 : 1
                            }}
                        >
                            <Statistic
                                title="中文字幕"
                                value={statistics.zh}
                                prefix={<MessageOutlined />}
                                valueStyle={{color: '#52c41a'}}
                                suffix={`/ ${statistics.total}`}
                            />
                        </Card>
                    </Col>
                    <Col span={24} sm={12} lg={6}>
                        <Card
                            hoverable
                            onClick={() => toggleQuickFilter('uncensored')}
                            style={{
                                borderColor: quickFilters.uncensored ? '#1890ff' : undefined,
                                borderWidth: quickFilters.uncensored ? 2 : 1
                            }}
                        >
                            <Statistic
                                title="无码视频"
                                value={statistics.uncensored}
                                prefix={<SafetyOutlined />}
                                valueStyle={{color: '#faad14'}}
                                suffix={`/ ${statistics.total}`}
                            />
                        </Card>
                    </Col>
                    <Col span={24} sm={12} lg={6}>
                        <Card
                            hoverable
                            onClick={() => toggleQuickFilter('hd')}
                            style={{
                                borderColor: quickFilters.hd ? '#1890ff' : undefined,
                                borderWidth: quickFilters.hd ? 2 : 1
                            }}
                        >
                            <Statistic
                                title="高清视频"
                                value={statistics.hd}
                                prefix={<HighlightOutlined />}
                                valueStyle={{color: '#f5222d'}}
                                suffix={`/ ${statistics.total}`}
                            />
                        </Card>
                    </Col>
                </Row>
            </Col>

            {/* Filter and Sort Bar */}
            {videos.length > 0 && (
                <Col span={24}>
                    <Card size="small">
                        <Space wrap>
                            <span style={{color: '#666'}}>快速筛选:</span>
                            <Button
                                size="small"
                                type={quickFilters.zh ? 'primary' : 'default'}
                                onClick={() => toggleQuickFilter('zh')}
                            >
                                中文字幕
                            </Button>
                            <Button
                                size="small"
                                type={quickFilters.uncensored ? 'primary' : 'default'}
                                onClick={() => toggleQuickFilter('uncensored')}
                            >
                                无码
                            </Button>
                            <Button
                                size="small"
                                type={quickFilters.hd ? 'primary' : 'default'}
                                onClick={() => toggleQuickFilter('hd')}
                            >
                                高清
                            </Button>
                            <span style={{marginLeft: 16, color: '#666'}}>排序:</span>
                            <Dropdown
                                menu={{
                                    items: [
                                        {
                                            key: 'time',
                                            label: '按时间',
                                            icon: <ClockCircleOutlined />,
                                            onClick: () => setSortBy('time')
                                        },
                                        {
                                            key: 'rating',
                                            label: '按评分',
                                            icon: <TrophyOutlined />,
                                            onClick: () => setSortBy('rating')
                                        }
                                    ],
                                    selectedKeys: [sortBy]
                                }}
                            >
                                <Button size="small" icon={<SortAscendingOutlined />}>
                                    {sortBy === 'time' ? '按时间' : '按评分'}
                                </Button>
                            </Dropdown>
                            {hasFilter && (
                                <Tag color="blue">
                                    已筛选 {videos.length} / {data.length} 个视频
                                </Tag>
                            )}
                        </Space>
                    </Card>
                </Col>
            )}

            {/* Video Cards */}
            {videos.length > 0 ? (
                videos.map((video: any) => (
                    <Col key={video.path} span={24} md={12} lg={6}>
                        <Badge.Ribbon
                            text={video.quality || 'SD'}
                            color={video.is_hd || video.quality === 'HD' || video.quality === '4K' ? 'red' : 'gray'}
                        >
                            <Card
                                hoverable
                                size="small"
                                cover={(<VideoCover src={video.cover}/>)}
                                onClick={() => setSelected(video.path)}
                                className="video-card"
                                style={{
                                    transition: 'all 0.3s ease',
                                }}
                                styles={{
                                    body: {
                                        padding: '12px'
                                    }
                                }}
                            >
                                <Card.Meta
                                    title={
                                        <div style={{
                                            overflow: 'hidden',
                                            textOverflow: 'ellipsis',
                                            whiteSpace: 'nowrap'
                                        }}>
                                            {video.title}
                                        </div>
                                    }
                                    description={(
                                        <div>
                                            {/* Tags */}
                                            <div className="flex" style={{marginBottom: 8}}>
                                                <div
                                                    className="flex-1 items-center overflow-x-scroll"
                                                    style={{scrollbarWidth: 'none'}}
                                                >
                                                    <Space size={[0, 'small']} className="flex-1" wrap>
                                                        {video.is_zh && (
                                                            <Tag color="blue" bordered={false}>中文</Tag>
                                                        )}
                                                        {video.is_uncensored && (
                                                            <Tag color="green" bordered={false}>无码</Tag>
                                                        )}
                                                        {(video.is_hd || video.quality === 'HD' || video.quality === '4K') && (
                                                            <Tag color="red" bordered={false}>高清</Tag>
                                                        )}
                                                        {video.rating && (
                                                            <Tag color="gold" bordered={false}>
                                                                {video.rating}分
                                                            </Tag>
                                                        )}
                                                        {video.actors.slice(0, 2).map((actor: any) => (
                                                            <Tag
                                                                key={actor.name}
                                                                color="purple"
                                                                bordered={false}
                                                                style={{cursor: 'pointer'}}
                                                                onClick={(e) => {
                                                                    e.stopPropagation();
                                                                    navigate({
                                                                        to: '/actor',
                                                                        search: {actorName: actor.name}
                                                                    });
                                                                }}
                                                            >
                                                                {actor.name}
                                                            </Tag>
                                                        ))}
                                                        {video.actors.length > 2 && (
                                                            <Tag bordered={false}>
                                                                +{video.actors.length - 2}
                                                            </Tag>
                                                        )}
                                                    </Space>
                                                </div>
                                            </div>
                                            {/* Action Buttons */}
                                            <div className="flex" style={{gap: 8}}>
                                                <Tooltip title="编辑">
                                                    <Button
                                                        type="text"
                                                        size="small"
                                                        icon={<EditOutlined />}
                                                        onClick={(e) => handleCardAction(e, 'edit', video)}
                                                    />
                                                </Tooltip>
                                                <FavoriteButton
                                                    videoNum={video.num}
                                                    videoTitle={video.title}
                                                    videoCover={video.cover}
                                                    type="text"
                                                    size="small"
                                                />
                                                <Tooltip title="下载">
                                                    <Button
                                                        type="text"
                                                        size="small"
                                                        icon={<DownloadOutlined />}
                                                        onClick={(e) => {
                                                            e.stopPropagation()
                                                            navigate({
                                                                to: '/search',
                                                                search: {num: video.num}
                                                            })
                                                        }}
                                                    />
                                                </Tooltip>
                                                <Tooltip title="搜索">
                                                    <Button
                                                        type="text"
                                                        size="small"
                                                        icon={<SearchOutlined />}
                                                        onClick={(e) => {
                                                            e.stopPropagation()
                                                            navigate({
                                                                to: '/search',
                                                                search: {num: video.num}
                                                            })
                                                        }}
                                                    />
                                                </Tooltip>
                                                <div style={{flex: 1}} />
                                                <Tooltip title="删除">
                                                    <Button
                                                        type="text"
                                                        size="small"
                                                        danger
                                                        icon={<DeleteOutlined />}
                                                        onClick={(e) => handleCardAction(e, 'delete', video)}
                                                    />
                                                </Tooltip>
                                            </div>
                                        </div>
                                    )}
                                />
                            </Card>
                        </Badge.Ribbon>
                    </Col>
                ))
            ) : (
                <Col span={24}>
                    <Card title="视频">
                        <Empty
                            description={
                                hasFilter ? (
                                    <span>
                                        没有符合条件的视频
                                        <Button
                                            type="link"
                                            onClick={() => {
                                                setFilterParams({})
                                                setQuickFilters({})
                                            }}
                                        >
                                            清除筛选
                                        </Button>
                                    </span>
                                ) : (
                                    <span>
                                        无视频，<Link to="/setting" hash="video">配置视频</Link>
                                    </span>
                                )
                            }
                        />
                    </Card>
                </Col>
            )}

            {/* Video Detail Modal */}
            <VideoDetail
                title="编辑"
                mode="video"
                width={1100}
                path={selected}
                open={!!selected}
                onCancel={() => setSelected(undefined)}
                onOk={() => {
                    setSelected(undefined)
                    refresh()
                }}
            />

            {/* Filter Modal */}
            <VideoFilterModal
                open={filterOpen}
                actors={actors}
                initialValues={filterParams}
                onCancel={() => setFilterOpen(false)}
                onFilter={params => {
                    setFilterParams(params)
                    setFilterOpen(false)
                }}
            />

            {/* Float Buttons */}
            <>
                {createPortal((
                    <>
                        <FloatButton icon={<RedoOutlined/>} onClick={() => run(true)}/>
                        <FloatButton
                            icon={<FilterOutlined/>}
                            type={hasFilter ? 'primary' : 'default'}
                            onClick={() => setFilterOpen(true)}
                        />
                    </>
                ), document.getElementsByClassName('index-float-button-group')[0])}
            </>

            {/* Custom Styles */}
            <style>{`
                .video-card:hover {
                    transform: translateY(-4px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                }

                .video-card .ant-card-cover {
                    overflow: hidden;
                }

                .video-card:hover .ant-card-cover img {
                    transform: scale(1.05);
                    transition: transform 0.3s ease;
                }
            `}</style>
        </Row>
    )
}
