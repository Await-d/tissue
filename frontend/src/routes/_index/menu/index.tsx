import routes from "../../../routes.tsx";
import { Card, Divider, theme, Row, Col } from "antd";
import { useResponsive } from "ahooks";
import React from "react";
import { createFileRoute, Link, Navigate } from "@tanstack/react-router";
import { HomeOutlined, SearchOutlined, UserOutlined, StarOutlined, HeartOutlined, ClockCircleOutlined, FileOutlined, SettingOutlined, HistoryOutlined, DownloadOutlined, InfoCircleOutlined, RobotOutlined } from "@ant-design/icons";

const { useToken } = theme

export const Route = createFileRoute('/_index/menu/')({
    component: Menu,
})

// 定义菜单项的接口
interface MenuItem {
    key: string;
    icon: React.ReactNode;
    label: string;
    path: string;
}

// 定义菜单组的接口
interface MenuGroup {
    title: string;
    items: string[];
}

function Menu() {

    const { token } = useToken();
    const responsive = useResponsive()

    // 添加演员订阅菜单项
    const menuItems: MenuItem[] = [
        {
            key: 'home',
            icon: <HomeOutlined />,
            label: '首页',
            path: '/home'
        },
        {
            key: 'search',
            icon: <SearchOutlined />,
            label: '搜索',
            path: '/search'
        },
        {
            key: 'actor',
            icon: <UserOutlined />,
            label: '演员',
            path: '/actor'
        },
        {
            key: 'actor-subscribe',
            icon: <StarOutlined />,
            label: '演员订阅',
            path: '/actor-subscribe'
        },
        {
            key: 'subscribe',
            icon: <HeartOutlined />,
            label: '订阅',
            path: '/subscribe'
        },
        {
            key: 'schedule',
            icon: <ClockCircleOutlined />,
            label: '定时任务',
            path: '/schedule'
        },
        {
            key: 'file',
            icon: <FileOutlined />,
            label: '文件',
            path: '/file'
        },
        {
            key: 'setting',
            icon: <SettingOutlined />,
            label: '设置',
            path: '/setting'
        },
        {
            key: 'history',
            icon: <HistoryOutlined />,
            label: '历史',
            path: '/history'
        },
        {
            key: 'download',
            icon: <DownloadOutlined />,
            label: '下载',
            path: '/download'
        },
        {
            key: 'about',
            icon: <InfoCircleOutlined />,
            label: '关于',
            path: '/about'
        },
        {
            key: 'auto-download',
            icon: <RobotOutlined />,
            label: '智能下载',
            path: '/auto-download'
        }
    ]

    // 分组菜单项
    const menuGroups: MenuGroup[] = [
        {
            title: '常用功能',
            items: ['home', 'search', 'actor', 'subscribe', 'auto-download']
        },
        {
            title: '内容管理',
            items: ['file', 'download', 'history']
        },
        {
            title: '系统设置',
            items: ['setting', 'schedule', 'about', 'actor-subscribe']
        }
    ];

    // 通过key找到对应的菜单项
    const getItemByKey = (key: string): MenuItem | undefined => {
        return menuItems.find(item => item.key === key);
    };

    // 渲染分组菜单
    function renderGroupedMenu() {
        return menuGroups.map(group => (
            <div key={group.title}>
                <Divider>{group.title}</Divider>
                <Row gutter={[16, 16]} justify="center">
                    {group.items.map(itemKey => {
                        const item = getItemByKey(itemKey);
                        return item ? (
                            <Col key={item.key} span={6}>
                                {renderMenuItem(item)}
                            </Col>
                        ) : null;
                    })}
                </Row>
            </div>
        ));
    }

    function renderMenuItem(item: MenuItem) {
        return (
            <Link to={item.path} style={{ color: token.colorText }}>
                <div className={'p-3 flex flex-col items-center'}
                    style={{
                        borderRadius: '8px',
                        transition: 'all 0.3s ease',
                        border: `1px solid ${token.colorBorderSecondary}`,
                        height: '100%'
                    }}>
                    <div className={'text-3xl'} style={{ color: token.colorPrimary }}>
                        {item.icon}
                    </div>
                    <div className={'mt-2 text-center'} style={{ fontSize: '14px' }}>
                        {item.label}
                    </div>
                </div>
            </Link>
        );
    }

    if (responsive.md) {
        return <Navigate to={'/'} />
    }

    return (
        <Card title="功能菜单" bordered={false}>
            {renderGroupedMenu()}
        </Card>
    )
}
