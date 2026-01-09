import {Card, Tabs} from "antd";
import React from "react";
import {AppstoreOutlined, CloudDownloadOutlined, FolderOpenOutlined, NotificationOutlined, RobotOutlined, BranchesOutlined, FilterOutlined} from "@ant-design/icons";
import {createFileRoute, Outlet, useLocation, useNavigate} from "@tanstack/react-router";

export const Route = createFileRoute('/_index/setting')({
    component: Setting
})

function Setting() {

    const navigate = useNavigate()
    const selected = useLocation().pathname

    const items = [
        {
            key: '/setting/app',
            label: '通用',
            icon: <AppstoreOutlined/>,
        },
        {
            key: '/setting/file',
            label: '文件',
            icon: <FolderOpenOutlined/>,
        },
        {
            key: '/setting/download',
            label: '下载',
            icon: <CloudDownloadOutlined/>,
        },
        {
            key: '/setting/download-filter',
            label: '下载过滤',
            icon: <FilterOutlined/>,
        },
        {
            key: '/setting/notify',
            label: '通知',
            icon: <NotificationOutlined/>,
        },
        {
            key: '/setting/auto-download',
            label: '智能下载',
            icon: <RobotOutlined/>,
        },
        {
            key: '/setting/version',
            label: '版本管理',
            icon: <BranchesOutlined/>,
        },
    ]


    return (
        <Card>
            <Tabs
                activeKey={selected}
                items={items}
                onChange={key => navigate({to: key})}
            />
            <Outlet/>
        </Card>
    )
}

