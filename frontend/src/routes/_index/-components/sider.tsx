/*
 * @Author: Await
 * @Date: 2025-05-24 17:05:38
 * @LastEditors: Await
 * @LastEditTime: 2025-05-26 18:51:02
 * @Description: TISSUE+ 侧边栏 - 电影美学风格
 */
import React from "react";
import { Menu } from "antd";
import routes from "../../../routes";
import Logo from "../../../assets/logo.svg";
import { Link, useMatches, useNavigate } from "@tanstack/react-router";

interface Props {
    onSelect?: () => void
    showLogo?: boolean
}

function Sider(props: Props) {

    const { showLogo = true } = props
    const matches = useMatches()
    const selected = matches.slice(2).map((item) => {
        return item.pathname.endsWith('/') ? item.pathname.slice(0, -1) : item.pathname
    })
    const navigate = useNavigate()

    function getItem(item: any): any {
        return {
            key: item.path,
            icon: item.icon,
            label: item.title,
            type: item.type,
        }
    }

    function generateItems(routes: any) {
        return routes.filter((i: any) => i.hidden !== true).map((item: any) => {
            const menuItem = getItem(item)
            if (item.children) {
                menuItem.children = generateItems(item.children)
            }
            return menuItem
        })
    }

    return (
        <div className="h-full flex flex-col">
            {/* Logo 区域 */}
            <div
                className={'h-16 flex items-center'}
                style={{ marginTop: 'env(safe-area-inset-top, 0)' }}
            >
                {showLogo && (
                    <Link to={'/'} className="group flex items-center">
                        <img
                            className={'ml-6 mr-4 h-11 transition-all duration-300 group-hover:drop-shadow-[0_0_16px_rgba(212,168,82,0.5)]'}
                            src={Logo}
                            alt=""
                        />
                    </Link>
                )}
            </div>

            {/* 菜单区域 */}
            <div className="flex-1 overflow-y-auto px-2">
                <Menu
                    selectedKeys={selected}
                    mode={'inline'}
                    items={generateItems(routes)}
                    onSelect={item => {
                        props.onSelect?.()
                        return navigate({ to: item.key })
                    }}
                    style={{
                        background: 'transparent',
                        border: 'none',
                    }}
                />
            </div>

            {/* 底部装饰 */}
            <div
                className="px-6 py-4 mt-auto"
                style={{
                    borderTop: '1px solid rgba(255, 255, 255, 0.04)',
                    background: 'linear-gradient(180deg, transparent 0%, rgba(212, 168, 82, 0.02) 100%)',
                }}
            >
                <div
                    className="text-xs"
                    style={{ color: '#4a4a52' }}
                >
                    TISSUE+
                </div>
            </div>
        </div>
    )
}

export default Sider
