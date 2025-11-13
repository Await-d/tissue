/*
 * @Author: Await
 * @Date: 2025-05-24 17:05:38
 * @LastEditors: Await
 * @LastEditTime: 2025-05-29 17:23:46
 * @Description: 请填写简介
 */
import Filter, { FilterField } from "./-components/filter.tsx";
import React from "react";
import { Col, Empty, message, Row, Skeleton } from "antd";
import JavDBItem from "./-components/item.tsx";
import Selector from "../../../components/Selector";
import Slider from "../../../components/Slider";
import * as api from "../../../apis/home.ts";
import { Await, createFileRoute, redirect, useNavigate } from "@tanstack/react-router";

export const Route = createFileRoute('/_index/home/')({
    component: JavDB,
    beforeLoad: ({ search }) => {
        if (Object.keys(search).length === 0)
            throw redirect({ search: { video_type: 'censored', cycle: 'daily', rank: 0, sort_by: 'rank', sort_order: 'desc' } as any })
    },
    loaderDeps: ({ search }) => ({ ...search, rank: 0 }),
    loader: async ({ deps }) => ({
        data: api.getRankings({ ...deps, source: 'JavDB' }).catch(() => {
        })
    }),
    staleTime: Infinity
})

function JavDB() {
    const { data } = Route.useLoaderData()
    const filter = Route.useSearch<any>()
    const navigate = useNavigate()

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
            let aValue, bValue;

            switch (sortBy) {
                case 'rank_count':
                    aValue = a.rank_count || 0;
                    bValue = b.rank_count || 0;
                    break;
                case 'publish_date':
                    aValue = new Date(a.publish_date || '1970-01-01').getTime();
                    bValue = new Date(b.publish_date || '1970-01-01').getTime();
                    break;
                case 'rank':
                default:
                    aValue = a.rank || 0;
                    bValue = b.rank || 0;
                    break;
            }

            if (sortOrder === 'asc') {
                return aValue - bValue;
            } else {
                return bValue - aValue;
            }
        });
    };

    return (
        <div>
            <Filter initialValues={filter} onChange={(values, field) => {
                return navigate({ search: values as any })
            }} fields={filterFields} />
            <Await promise={data} fallback={(
                <Row className={'mt-2'} gutter={[12, 12]}>
                    {[...Array(8)].map((_, index) => (
                        <Col key={index} span={24} md={12} lg={6}>
                            <div style={{
                                background: '#fff',
                                borderRadius: '8px',
                                overflow: 'hidden',
                                border: '1px solid #f0f0f0'
                            }}>
                                <Skeleton.Image active style={{ width: '100%', height: '200px' }} />
                                <div style={{ padding: '12px' }}>
                                    <Skeleton active paragraph={{ rows: 3 }} />
                                </div>
                            </div>
                        </Col>
                    ))}
                </Row>
            )}>
                {(data = []) => {
                    // 先按评分过滤，再排序
                    const filteredVideos = data.filter((item: any) => item.rank >= filter.rank);
                    const sortedVideos = sortVideos(filteredVideos, filter.sort_by || 'rank', filter.sort_order || 'desc');

                    return sortedVideos.length > 0 ? (
                        <Row className={'mt-2 cursor-pointer'} gutter={[12, 12]}>
                            {sortedVideos.map((item: any) => (
                                <Col key={item.url} span={24} md={12} lg={6}
                                    onClick={() => navigate({
                                        to: '/home/detail',
                                        search: { source: 'JavDB', url: item.url, num: item.num }
                                    })}><JavDBItem
                                        item={item} /></Col>
                            ))}
                        </Row>
                    ) : (
                        <Empty
                            className={'mt-10'}
                            description={
                                <div>
                                    <div style={{ fontSize: '16px', marginBottom: '8px' }}>没有找到符合条件的视频</div>
                                    <div style={{ fontSize: '14px', color: '#999' }}>
                                        {filter.rank > 0 ? '请尝试降低评分要求或调整其他筛选条件' : '请调整筛选条件重试'}
                                    </div>
                                </div>
                            }
                        />
                    )
                }}
            </Await>
        </div>
    )
}

export default JavDB
