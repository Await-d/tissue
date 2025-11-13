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

export const Route = createFileRoute('/_index/video/')({
    component: Video,
})

function Video() {

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
            <Row gutter={[15, 15]}>
                {[...Array(8)].map((_, index) => (
                    <Col key={index} span={24} md={12} lg={6}>
                        <Card>
                            <Skeleton.Image active style={{ width: '100%', height: '200px', marginBottom: '12px' }} />
                            <Skeleton active paragraph={{ rows: 2 }} />
                        </Card>
                    </Col>
                ))}
            </Row>
        )
    }

    return (
        <Row gutter={[15, 15]}>
            {videos.length > 0 ? (
                videos.map((video: any) => (
                    <Col key={video.path} span={24} md={12} lg={6}>
                        <Card hoverable
                              size={"small"}
                              cover={(<VideoCover src={video.cover}/>)}
                              onClick={() => setSelected(video.path)}
                              style={{
                                  transition: 'all 0.3s',
                                  cursor: 'pointer'
                              }}
                              onMouseEnter={(e) => {
                                  e.currentTarget.style.transform = 'translateY(-4px)';
                                  e.currentTarget.style.boxShadow = '0 12px 24px rgba(0,0,0,0.15)';
                              }}
                              onMouseLeave={(e) => {
                                  e.currentTarget.style.transform = 'translateY(0)';
                                  e.currentTarget.style.boxShadow = '';
                              }}
                        >
                            <Card.Meta
                                       title={
                                           <div style={{
                                               overflow: 'hidden',
                                               textOverflow: 'ellipsis',
                                               display: '-webkit-box',
                                               WebkitLineClamp: 2,
                                               WebkitBoxOrient: 'vertical',
                                               lineHeight: '1.4',
                                               minHeight: '2.8em',
                                               fontSize: '14px',
                                               fontWeight: 600
                                           }}>
                                               {video.title}
                                           </div>
                                       }
                                       description={(
                                           <div style={{
                                               display: 'flex',
                                               flexWrap: 'wrap',
                                               gap: '4px',
                                               marginTop: '8px'
                                           }}>
                                               {video.is_zh && (<Tag color={'blue'} bordered={false}>中文</Tag>)}
                                               {video.is_uncensored && (<Tag color={'green'} bordered={false}>无码</Tag>)}
                                               {video.actors.slice(0, 3).map((actor: any) => (
                                                   <Tag key={actor.name} color={'purple'} bordered={false}>{actor.name}</Tag>
                                               ))}
                                               {video.actors.length > 3 && (
                                                   <Tag color={'default'} bordered={false}>+{video.actors.length - 3}</Tag>
                                               )}
                                           </div>
                                       )}
                            />
                        </Card>
                    </Col>
                ))
            ) : (
                <Col span={24}>
                    <Card title={'视频'}>
                        <Empty
                            description={
                                <div>
                                    <div style={{ fontSize: '16px', marginBottom: '8px' }}>
                                        {hasFilter ? '没有找到符合条件的视频' : '暂无视频'}
                                    </div>
                                    <div style={{ fontSize: '14px', color: '#999' }}>
                                        {hasFilter
                                            ? '请尝试调整筛选条件'
                                            : (<span>请先 <Link to={'/setting'} hash={'video'} style={{ fontWeight: 500 }}>配置视频路径</Link> 以添加视频</span>)
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
                            <FloatButton icon={<RedoOutlined/>} onClick={() => run(true)}/>
                            <FloatButton icon={<FilterOutlined/>} type={hasFilter ? 'primary' : 'default'}
                                         onClick={() => setFilterOpen(true)}/>
                        </>
                    ), document.getElementsByClassName('index-float-button-group')[0]
                )}
            </>
        </Row>
    )
}
