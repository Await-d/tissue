import routes from "../../../routes.tsx";
import { Card, Divider, theme } from "antd";
import { useResponsive } from "ahooks";
import React from "react";
import { createFileRoute, Link, Navigate } from "@tanstack/react-router";
import { HomeOutlined, SearchOutlined, UserOutlined, StarOutlined, HeartOutlined, ClockCircleOutlined, FileOutlined, SettingOutlined, HistoryOutlined, DownloadOutlined, InfoCircleOutlined } from "@ant-design/icons";

const { useToken } = theme

export const Route = createFileRoute('/_index/menu/')({
    component: Menu,
})

function Menu() {

    const { token } = useToken();
    const responsive = useResponsive()

    // 添加演员订阅菜单项
    const menuItems = [
        {
            key: 'home',
            icon: <HomeOutlined />,
            label: '首页'
        },
        {
            key: 'search',
            icon: <SearchOutlined />,
            label: '搜索'
        },
        {
            key: 'actor',
            icon: <UserOutlined />,
            label: '演员'
        },
        {
            key: 'actor-subscribe',
            icon: <StarOutlined />,
            label: '演员订阅'
        },
        {
            key: 'subscribe',
            icon: <HeartOutlined />,
            label: '订阅'
        },
        {
            key: 'schedule',
            icon: <ClockCircleOutlined />,
            label: '定时任务'
        },
        {
            key: 'file',
            icon: <FileOutlined />,
            label: '文件'
        },
        {
            key: 'setting',
            icon: <SettingOutlined />,
            label: '设置'
        },
        {
            key: 'history',
            icon: <HistoryOutlined />,
            label: '历史'
        },
        {
            key: 'download',
            icon: <DownloadOutlined />,
            label: '下载'
        },
        {
            key: 'about',
            icon: <InfoCircleOutlined />,
            label: '关于'
        }
    ]

    function renderMenuSection() {
        return routes.filter(i => i.hidden !== true).map(item => (
            <div key={item.title}>
                <Divider>{item.title}</Divider>
                <div className={'flex justify-center'}>
                    {item.children ? (
                        item.children.map((child: any) => (renderMenu(child)))
                    ) : (
                        renderMenu(item)
                    )}
                </div>
            </div>
        ))
    }

    function renderMenu(menu: any) {
        return (
            <Link key={menu.path} to={menu.path} style={{ color: token.colorText }}>
                <div className={'px-4 py-2 flex flex-col items-center'}>
                    <div className={'text-4xl'}>
                        {menu.icon}
                    </div>
                    <div className={'mt-2'}>
                        {menu.title}
                    </div>
                </div>
            </Link>
        )
    }

    if (responsive.md) {
        return <Navigate to={'/'} />
    }

    return (
        <Card>
            {renderMenuSection()}
        </Card>
    )
}
