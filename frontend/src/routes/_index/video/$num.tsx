/*
 * @Author: Await
 * @Date: 2025-05-27 06:17:01
 * @LastEditors: Await
 * @LastEditTime: 2025-05-27 06:17:51
 * @Description: 请填写简介
 */
import React from 'react';
import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { Card, Skeleton } from 'antd';
import * as api from '../../../apis/video';
import VideoDetail from '../../../components/VideoDetail';

export const Route = createFileRoute('/_index/video/$num')({
    component: VideoDetailPage,
    loader: async ({ params, search }) => {
        const { source, url } = search;
        if (!source || !url) return null;

        try {
            const data = await api.getVideoDetail(params.num, source, url);
            return data;
        } catch (error) {
            console.error('加载视频详情失败:', error);
            return null;
        }
    },
});

function VideoDetailPage() {
    const navigate = useNavigate();
    const { num } = Route.useParams();
    const { source, url } = Route.useSearch<{ source?: string; url?: string }>();
    const data = Route.useLoaderData();
    const [open, setOpen] = React.useState(true);

    const handleClose = () => {
        setOpen(false);
        navigate({ to: '/_index/home' });
    };

    if (!data) {
        return (
            <Card>
                <Skeleton active />
            </Card>
        );
    }

    return (
        <VideoDetail
            title={`${num} 详情`}
            open={open}
            onCancel={handleClose}
            onOk={handleClose}
            width={1100}
            // 传递视频数据
            path={data.path || ''}
            mode="detail"
        />
    );
} 