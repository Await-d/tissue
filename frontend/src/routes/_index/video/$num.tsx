/*
 * @Author: Await
 * @Date: 2025-05-27 06:17:01
 * @LastEditors: Await
 * @LastEditTime: 2025-05-27 17:35:20
 * @Description: 请填写简介
 */
import React from 'react';
import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { Card, Skeleton } from 'antd';
import * as api from '../../../apis/video';
import VideoDetail from '../../../components/VideoDetail';

export const Route = createFileRoute('/_index/video/$num')({
    component: VideoDetailPage,
    loader: async ({ params, context }) => {
        // 从params中获取num，从URL查询参数中获取source和url
        const { num } = params;
        const urlParams = new URLSearchParams(window.location.search);
        const source = urlParams.get('source');
        const url = urlParams.get('url');

        if (!source || !url) return null;

        try {
            const data = await api.getVideoDetail(num, source, url);
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
    const data = Route.useLoaderData();
    const [open, setOpen] = React.useState(true);

    const handleClose = () => {
        setOpen(false);
        navigate({ to: '/home' });
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