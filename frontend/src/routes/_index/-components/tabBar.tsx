/*
 * @Author: Await
 * @Date: 2025-05-24 17:05:38
 * @LastEditors: Await
 * @LastEditTime: 2025-05-27 18:08:05
 * @Description: TISSUE+ 底部导航栏 - 电影美学风格
 */
import { CarryOutOutlined, HomeOutlined, MenuOutlined, SearchOutlined, VideoCameraOutlined, RobotOutlined } from "@ant-design/icons";
import React from "react";
import { Badge } from "antd";
import { Link, useLocation } from "@tanstack/react-router";

function TabBar() {

    const location = useLocation()

    const menus = [
        {
            link: '/home',
            icon: <HomeOutlined />,
            title: '首页'
        },
        {
            link: '/video',
            icon: <VideoCameraOutlined />,
            title: '影片'
        },
        {
            link: '/subscribe',
            icon: <CarryOutOutlined />,
            title: '订阅'
        },
        {
            link: '/search',
            icon: <SearchOutlined />,
            title: '搜索'
        },
        {
            link: '/auto-download',
            icon: <RobotOutlined />,
            title: '智能'
        },
        {
            link: '/menu',
            icon: <MenuOutlined />,
            title: '菜单'
        }
    ]

    // 检查当前路径是否匹配菜单项
    const isActive = (menuLink: string) => {
        const currentPath = location.pathname.replace(/^\/+/, '');
        const menuPath = menuLink.replace(/^\/+/, '');
        return currentPath === menuPath || currentPath.startsWith(menuPath + '/');
    };

    return (
        <div
            className={'flex justify-around items-center'}
            style={{
                marginBottom: 'env(safe-area-inset-bottom, 0)',
                padding: '6px 0 8px',
            }}
        >
            {menus.map(item => {
                const active = isActive(item.link);
                return (
                    <Link
                        key={item.link}
                        to={item.link}
                        className="flex flex-col items-center relative group"
                        style={{
                            padding: '6px 12px',
                            borderRadius: 12,
                            transition: 'all 200ms cubic-bezier(0.4, 0, 0.2, 1)',
                            background: active
                                ? 'linear-gradient(135deg, rgba(212, 168, 82, 0.15) 0%, rgba(212, 168, 82, 0.05) 100%)'
                                : 'transparent',
                        }}
                    >
                        {/* 激活指示器 */}
                        {active && (
                            <div
                                style={{
                                    position: 'absolute',
                                    top: 0,
                                    left: '50%',
                                    transform: 'translateX(-50%)',
                                    width: 20,
                                    height: 2,
                                    borderRadius: 1,
                                    background: 'linear-gradient(90deg, #d4a852 0%, #e8c780 100%)',
                                    boxShadow: '0 0 8px rgba(212, 168, 82, 0.5)',
                                }}
                            />
                        )}

                        {/* 图标 */}
                        <Badge dot={false}>
                            <div
                                style={{
                                    fontSize: 20,
                                    marginBottom: 2,
                                    color: active ? '#d4a852' : '#6a6a72',
                                    transition: 'all 200ms cubic-bezier(0.4, 0, 0.2, 1)',
                                    transform: active ? 'scale(1.1)' : 'scale(1)',
                                    filter: active ? 'drop-shadow(0 0 6px rgba(212, 168, 82, 0.4))' : 'none',
                                }}
                            >
                                {item.icon}
                            </div>
                        </Badge>

                        {/* 标题 */}
                        <div
                            style={{
                                fontSize: 10,
                                lineHeight: 1.2,
                                fontWeight: active ? 600 : 400,
                                color: active ? '#d4a852' : '#6a6a72',
                                transition: 'all 200ms cubic-bezier(0.4, 0, 0.2, 1)',
                                letterSpacing: active ? '0.02em' : '0',
                            }}
                        >
                            {item.title}
                        </div>
                    </Link>
                );
            })}
        </div>
    )
}

export default TabBar
