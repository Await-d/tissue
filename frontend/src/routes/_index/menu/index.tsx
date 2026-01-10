import routes from "../../../routes.tsx";
import { Card, Divider, theme, Row, Col } from "antd";
import { useResponsive } from "ahooks";
import React from "react";
import { createFileRoute, Link, Navigate } from "@tanstack/react-router";
import { HomeOutlined, SearchOutlined, UserOutlined, StarOutlined, HeartOutlined, ClockCircleOutlined, FileOutlined, SettingOutlined, HistoryOutlined, DownloadOutlined, InfoCircleOutlined, RobotOutlined } from "@ant-design/icons";
import { useThemeColors } from '../../../hooks/useThemeColors';

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
    const colors = useThemeColors();

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
        return menuGroups.map((group, index) => (
            <div 
                key={group.title}
                style={{
                    animation: `menuFadeIn 0.4s ease-out ${index * 0.1}s both`
                }}
            >
                <Divider
                    style={{
                        borderColor: colors.borderPrimary,
                        marginTop: index === 0 ? '0' : '24px',
                        marginBottom: '20px'
                    }}
                >
                    <span style={{
                        color: colors.goldPrimary,
                        fontSize: '13px',
                        fontWeight: 600,
                        letterSpacing: '0.5px',
                        textTransform: 'uppercase'
                    }}>
                        {group.title}
                    </span>
                </Divider>
                <Row gutter={[12, 12]} justify="center">
                    {group.items.map((itemKey, itemIndex) => {
                        const item = getItemByKey(itemKey);
                        return item ? (
                            <Col key={item.key} span={6}>
                                <MenuItemCard item={item} groupIndex={index} itemIndex={itemIndex} />
                            </Col>
                        ) : null;
                    })}
                </Row>
            </div>
        ));
    }

    // MenuItem 组件 - 使用组件以支持 React Hooks
    const MenuItemCard: React.FC<{ item: MenuItem; groupIndex: number; itemIndex: number }> = ({ item, groupIndex, itemIndex }) => {
        const [isHovered, setIsHovered] = React.useState(false);

        return (
            <Link to={item.path} style={{ textDecoration: 'none' }}>
                <div
                    className={'p-3 flex flex-col items-center'}
                    onMouseEnter={() => setIsHovered(true)}
                    onMouseLeave={() => setIsHovered(false)}
                    style={{
                        background: isHovered ? colors.bgSpotlight : colors.bgContainer,
                        borderRadius: '12px',
                        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                        border: `1px solid ${isHovered ? colors.goldDark : colors.borderPrimary}`,
                        height: '100%',
                        cursor: 'pointer',
                        boxShadow: isHovered
                            ? `0 8px 24px rgba(212, 168, 82, 0.12), 0 0 0 1px ${colors.goldDark}`
                            : '0 2px 8px rgba(0, 0, 0, 0.15)',
                        transform: isHovered ? 'translateY(-2px)' : 'translateY(0)',
                        animation: `menuItemFadeIn 0.3s ease-out ${groupIndex * 0.1 + itemIndex * 0.05}s both`
                    }}>
                    <div
                        className={'text-3xl'}
                        style={{
                            color: isHovered ? colors.goldLight : colors.goldPrimary,
                            transition: 'all 0.3s ease',
                            filter: isHovered ? `drop-shadow(0 0 8px ${colors.goldPrimary})` : 'none',
                            transform: isHovered ? 'scale(1.1)' : 'scale(1)'
                        }}
                    >
                        {item.icon}
                    </div>
                    <div
                        className={'mt-2 text-center'}
                        style={{
                            fontSize: '12px',
                            color: isHovered ? colors.textPrimary : colors.textSecondary,
                            transition: 'color 0.3s ease',
                            fontWeight: isHovered ? 500 : 400
                        }}
                    >
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
        <>
            <style>
                {`
                    @keyframes menuFadeIn {
                        from {
                            opacity: 0;
                            transform: translateY(10px);
                        }
                        to {
                            opacity: 1;
                            transform: translateY(0);
                        }
                    }
                    
                    @keyframes menuItemFadeIn {
                        from {
                            opacity: 0;
                            transform: scale(0.95);
                        }
                        to {
                            opacity: 1;
                            transform: scale(1);
                        }
                    }
                `}
            </style>
            <Card
                title={
                    <span style={{
                        color: colors.goldPrimary,
                        fontSize: '18px',
                        fontWeight: 600
                    }}>
                        功能菜单
                    </span>
                }
                variant="borderless"
                style={{
                    background: colors.bgElevated,
                    borderRadius: '16px'
                }}
                styles={{
                    header: {
                        borderBottom: `1px solid ${colors.borderPrimary}`,
                        background: colors.bgBase
                    },
                    body: {
                        background: colors.bgElevated
                    }
                }}
            >
                {renderGroupedMenu()}
            </Card>
        </>
    )
}
