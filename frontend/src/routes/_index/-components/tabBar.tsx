/*
 * @Author: Await
 * @Date: 2025-05-24 17:05:38
 * @LastEditors: Await
 * @LastEditTime: 2025-05-27 18:08:05
 * @Description: 请填写简介
 */
import { CarryOutOutlined, HomeOutlined, MenuOutlined, SearchOutlined, UserOutlined, VideoCameraOutlined } from "@ant-design/icons";
import React from "react";
import { theme, Badge } from "antd";
import { Link, useLocation } from "@tanstack/react-router";

const { useToken } = theme

function TabBar() {

    const { token } = useToken()
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
            link: '/actor',
            icon: <UserOutlined />,
            title: '演员'
        },
        {
            link: '/menu',
            icon: <MenuOutlined />,
            title: '菜单'
        }
    ]

    // 检查当前路径是否匹配菜单项
    const isActive = (menuLink: string) => {
        // 移除开头的斜杠以进行一致比较
        const currentPath = location.pathname.replace(/^\/+/, '');
        const menuPath = menuLink.replace(/^\/+/, '');

        return currentPath === menuPath || currentPath.startsWith(menuPath + '/');
    };

    return (
        <div className={'flex justify-around items-center'}
            style={{
                marginBottom: 'env(safe-area-inset-bottom,0)',
                padding: '8px 0',
                boxShadow: '0 -1px 2px rgba(0,0,0,0.05)'
            }}>
            {menus.map(item => {
                const active = isActive(item.link);
                return (
                    <div key={item.link} className={'flex flex-col items-center'}>
                        <Link to={item.link}
                            style={{
                                color: active ? token.colorPrimary : token.colorText,
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                padding: '4px 0'
                            }}>
                            <Badge dot={false}>
                                <div className={'text-xl mb-1'}>
                                    {item.icon}
                                </div>
                            </Badge>
                            <div style={{
                                fontSize: '12px',
                                lineHeight: '1',
                                fontWeight: active ? 'bold' : 'normal'
                            }}>
                                {item.title}
                            </div>
                        </Link>
                    </div>
                );
            })}
        </div>
    )
}

export default TabBar
