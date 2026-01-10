import {useRequest} from "ahooks";
import * as api from "../../../apis/video";
import {Card, Col, Empty, FloatButton, Row, Skeleton, Space, Tag} from "antd";
import VideoCover from "../../../components/VideoCover";
import React, {useMemo, useState} from "react";
import {createPortal} from "react-dom";
import {FilterOutlined, RedoOutlined} from "@ant-design/icons";
import VideoFilterModal, {FilterParams} from "./-components/filter.tsx";
import {createFileRoute, Link} from "@tanstack/react-router";
import VideoDetail from "../../../components/VideoDetail";
import {useThemeColors} from "../../../hooks/useThemeColors";

export const Route = createFileRoute('/_index/video/')({
    component: Video,
})

function Video() {

    const colors = useThemeColors()
    const {data = [], loading, run, refresh} = useRequest(api.getVideos)
    const [selected, setSelected] = useState<string | undefined>()
    const [filterOpen, setFilterOpen] = useState(false)
    const [filterParams, setFilterParams] = useState<FilterParams>({})

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

    const videos = useMemo(() => {
        return data.filter((item: any) => {
            if (filterParams.title) {
                if (!item.title.toUpperCase().includes(filterParams.title.toUpperCase())) {
                    return false
                }
            }
            if (filterParams.actors?.length) {
                return item.actors.map((i: any) => i.name).filter((i: string) => filterParams.actors?.includes(i)).length > 0
            }
            return true
        })
    }, [filterParams, data])

    const hasFilter = !!filterParams.title || !!filterParams.actors?.length

    if (loading) {
        return (
            <Row gutter={[16, 16]}>
                {[...Array(8)].map((_, index) => (
                    <Col key={index} span={24} md={12} lg={6} className="tissue-animate-in" style={{ animationDelay: `${index * 50}ms` }}>
                        <Card
                            style={{
                                background: colors.bgContainer,
                                border: `1px solid ${colors.borderPrimary}`,
                                borderRadius: 'var(--radius-lg)',
                            }}
                        >
                            <div className="tissue-skeleton" style={{ width: '100%', height: '240px', marginBottom: '16px', borderRadius: 'var(--radius-md)' }} />
                            <div className="tissue-skeleton" style={{ width: '100%', height: '20px', marginBottom: '12px' }} />
                            <div className="tissue-skeleton" style={{ width: '60%', height: '16px', marginBottom: '8px' }} />
                            <div style={{ display: 'flex', gap: '6px', marginTop: '12px' }}>
                                <div className="tissue-skeleton" style={{ width: '50px', height: '24px', borderRadius: 'var(--radius-sm)' }} />
                                <div className="tissue-skeleton" style={{ width: '50px', height: '24px', borderRadius: 'var(--radius-sm)' }} />
                                <div className="tissue-skeleton" style={{ width: '60px', height: '24px', borderRadius: 'var(--radius-sm)' }} />
                            </div>
                        </Card>
                    </Col>
                ))}
            </Row>
        )
    }

    return (
        <Row gutter={[16, 16]}>
            {videos.length > 0 ? (
                videos.map((video: any, index: number) => (
                    <Col key={video.path} span={24} md={12} lg={6} className="tissue-animate-in" style={{ animationDelay: `${index * 50}ms` }}>
                        <Card
                            hoverable
                            size="small"
                            cover={
                                <div className="tissue-cover" style={{ height: '240px' }}>
                                    <VideoCover src={video.cover}/>
                                </div>
                            }
                            onClick={() => setSelected(video.path)}
                            style={{
                                background: colors.bgContainer,
                                border: `1px solid ${colors.borderPrimary}`,
                                borderRadius: 'var(--radius-lg)',
                                overflow: 'hidden',
                                transition: 'all var(--transition-base)',
                                cursor: 'pointer',
                                position: 'relative',
                            }}
                            className="tissue-glow-border"
                            onMouseEnter={(e) => {
                                e.currentTarget.style.transform = 'translateY(-6px)';
                                e.currentTarget.style.boxShadow = `0 0 24px ${colors.rgba('gold', 0.2)}, 0 8px 32px ${colors.rgba('black', 0.5)}`;
                                e.currentTarget.style.borderColor = colors.borderGold;
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.transform = 'translateY(0)';
                                e.currentTarget.style.boxShadow = '';
                                e.currentTarget.style.borderColor = colors.borderPrimary;
                            }}
                        >
                            <div style={{
                                position: 'absolute',
                                inset: 0,
                                background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.02) 0%, transparent 50%)',
                                pointerEvents: 'none',
                                zIndex: 1,
                            }} />
                            <Card.Meta
                                title={
                                    <div style={{
                                        overflow: 'hidden',
                                        textOverflow: 'ellipsis',
                                        display: '-webkit-box',
                                        WebkitLineClamp: 2,
                                        WebkitBoxOrient: 'vertical',
                                        lineHeight: '1.5',
                                        minHeight: '3em',
                                        fontSize: '14px',
                                        fontWeight: 600,
                                        color: colors.textPrimary,
                                        transition: 'color var(--transition-fast)',
                                    }}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.color = colors.goldLight;
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.color = colors.textPrimary;
                                    }}
                                    >
                                        {video.title}
                                    </div>
                                }
                                description={(
                                    <div style={{
                                        display: 'flex',
                                        flexWrap: 'wrap',
                                        gap: '6px',
                                        marginTop: '10px'
                                    }}>
                                        {video.is_zh && (
                                            <Tag
                                                style={{
                                                    background: colors.rgba('white', 0.08),
                                                    color: '#4ea8ff',
                                                    border: `1px solid ${colors.rgba('white', 0.3)}`,
                                                    borderRadius: 'var(--radius-sm)',
                                                    fontWeight: 500,
                                                    fontSize: '12px',
                                                    padding: '2px 10px',
                                                    margin: 0,
                                                }}
                                            >
                                                中文
                                            </Tag>
                                        )}
                                        {video.is_uncensored && (
                                            <Tag
                                                style={{
                                                    background: colors.rgba('white', 0.08),
                                                    color: '#73d13d',
                                                    border: `1px solid ${colors.rgba('white', 0.3)}`,
                                                    borderRadius: 'var(--radius-sm)',
                                                    fontWeight: 500,
                                                    fontSize: '12px',
                                                    padding: '2px 10px',
                                                    margin: 0,
                                                }}
                                            >
                                                无码
                                            </Tag>
                                        )}
                                        {video.actors.slice(0, 3).map((actor: any) => (
                                            <Tag
                                                key={actor.name}
                                                style={{
                                                    background: colors.goldGlow,
                                                    color: colors.goldPrimary,
                                                    border: `1px solid ${colors.borderGold}`,
                                                    borderRadius: 'var(--radius-sm)',
                                                    fontWeight: 500,
                                                    fontSize: '12px',
                                                    padding: '2px 10px',
                                                    margin: 0,
                                                    transition: 'all var(--transition-fast)',
                                                }}
                                                onMouseEnter={(e) => {
                                                    e.currentTarget.style.background = colors.rgba('gold', 0.25);
                                                    e.currentTarget.style.transform = 'translateY(-1px)';
                                                }}
                                                onMouseLeave={(e) => {
                                                    e.currentTarget.style.background = colors.goldGlow;
                                                    e.currentTarget.style.transform = 'translateY(0)';
                                                }}
                                            >
                                                {actor.name}
                                            </Tag>
                                        ))}
                                        {video.actors.length > 3 && (
                                            <Tag
                                                style={{
                                                    background: colors.bgSpotlight,
                                                    color: colors.textTertiary,
                                                    border: `1px solid ${colors.borderPrimary}`,
                                                    borderRadius: 'var(--radius-sm)',
                                                    fontWeight: 500,
                                                    fontSize: '12px',
                                                    padding: '2px 10px',
                                                    margin: 0,
                                                }}
                                            >
                                                +{video.actors.length - 3}
                                            </Tag>
                                        )}
                                    </div>
                                )}
                            />
                        </Card>
                    </Col>
                ))
            ) : (
                <Col span={24}>
                    <Card
                        title={
                            <span style={{
                                color: colors.textPrimary,
                                fontSize: '16px',
                                fontWeight: 600,
                            }}>
                                视频
                            </span>
                        }
                        style={{
                            background: colors.bgContainer,
                            border: `1px solid ${colors.borderPrimary}`,
                            borderRadius: 'var(--radius-lg)',
                        }}
                    >
                        <Empty
                            image={Empty.PRESENTED_IMAGE_SIMPLE}
                            description={
                                <div style={{ padding: '24px 0' }}>
                                    <div style={{
                                        fontSize: '16px',
                                        marginBottom: '12px',
                                        color: colors.textPrimary,
                                        fontWeight: 500,
                                    }}>
                                        {hasFilter ? '没有找到符合条件的视频' : '暂无视频'}
                                    </div>
                                    <div style={{
                                        fontSize: '14px',
                                        color: colors.textSecondary,
                                        lineHeight: '1.6',
                                    }}>
                                        {hasFilter
                                            ? '请尝试调整筛选条件'
                                            : (
                                                <span>
                                                    请先{' '}
                                                    <Link
                                                        to={'/setting'}
                                                        hash={'video'}
                                                        style={{
                                                            fontWeight: 500,
                                                            color: colors.goldPrimary,
                                                            textDecoration: 'none',
                                                            transition: 'color var(--transition-fast)',
                                                        }}
                                                        onMouseEnter={(e) => {
                                                            e.currentTarget.style.color = colors.goldLight;
                                                        }}
                                                        onMouseLeave={(e) => {
                                                            e.currentTarget.style.color = colors.goldPrimary;
                                                        }}
                                                    >
                                                        配置视频路径
                                                    </Link>
                                                    {' '}以添加视频
                                                </span>
                                            )
                                        }
                                    </div>
                                </div>
                            }
                        />
                    </Card>
                </Col>
            )}
            <VideoDetail title={'编辑'}
                         mode={'video'}
                         width={1100}
                         path={selected}
                         open={!!selected}
                         onCancel={() => setSelected(undefined)}
                         onOk={() => {
                             setSelected(undefined)
                             refresh()
                         }}
            />
            <VideoFilterModal open={filterOpen}
                              actors={actors}
                              initialValues={filterParams}
                              onCancel={() => setFilterOpen(false)}
                              onFilter={params => {
                                  setFilterParams(params)
                                  setFilterOpen(false)
                              }}/>
            <>
                {createPortal((
                        <>
                            <FloatButton
                                icon={<RedoOutlined/>}
                                onClick={() => run(true)}
                                style={{
                                    background: colors.bgSpotlight,
                                    border: `1px solid ${colors.borderPrimary}`,
                                }}
                            />
                            <FloatButton
                                icon={<FilterOutlined/>}
                                type={hasFilter ? 'primary' : 'default'}
                                onClick={() => setFilterOpen(true)}
                                style={{
                                    ...(hasFilter ? {
                                        background: colors.goldGradient,
                                        boxShadow: colors.shadowGold,
                                    } : {
                                        background: colors.bgSpotlight,
                                        border: `1px solid ${colors.borderPrimary}`,
                                    })
                                }}
                            />
                        </>
                    ), document.getElementsByClassName('index-float-button-group')[0]
                )}
            </>
        </Row>
    )
}
