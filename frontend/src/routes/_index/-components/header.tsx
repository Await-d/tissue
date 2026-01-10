import { Divider, Dropdown, Modal, Space, theme } from "antd";
import type { MenuProps } from 'antd';

import {
    ArrowLeftOutlined,
    CodeOutlined,
    EyeInvisibleOutlined,
    EyeOutlined,
    LockOutlined,
    LogoutOutlined,
    MenuOutlined,
    UserOutlined
} from "@ant-design/icons";
import { useDispatch, useSelector } from "react-redux";
import { Dispatch, RootState } from "../../../models";
import { themes } from "../../../utils/constants";
import React, { useRef, useState } from "react";
import IconButton from "../../../components/IconButton";
import Log from "./log";
import Logo from "../../../assets/logo.svg";
import { useResponsive } from "ahooks";
import PinView, { PinMode } from "../../../components/PinView";
import { Link, useRouter } from "@tanstack/react-router";


const { useToken } = theme

interface Props {
    collapsible: boolean
    onCollapse: () => void
}

function Header(props: Props) {

    const responsive = useResponsive()
    const { history } = useRouter()
    const menuIconRef = useRef(null)
    const eyeIconRef = useRef(null)
    const themeIconRef = useRef(null)
    const userIconRef = useRef(null)
    const backIconRef = useRef(null)

    const { token } = useToken()
    const isGoodBoy = useSelector((state: RootState) => state.app.goodBoy)
    const canBack = useSelector((state: RootState) => state.app?.canBack)
    const appDispatch = useDispatch<Dispatch>().app
    const { userInfo } = useSelector((state: RootState) => state.auth)
    const authDispatch = useDispatch<Dispatch>().auth
    const [logOpen, setLogOpen] = useState(false)
    const [pinVisible, setPinVisible] = useState(false)

    const themeMode = useSelector((state: RootState) => state.app?.themeMode)
    const CurrentTheme = themes.find(i => i.name === themeMode) || themes[0]

    function onGoodBoyChange() {
        appDispatch.setGoodBoy(!isGoodBoy)
    }

    const themeItems: MenuProps['items'] = themes.map(i => ({
        key: i.name,
        label: i.title,
        icon: <i.icon></i.icon>
    })) as any

    function onThemeClick(event: any) {
        appDispatch.setThemeMode(event.key)
    }

    const userItems: MenuProps['items'] = [
        ...[!responsive.lg && {
            key: 'pin',
            label: '设置PIN',
            icon: <LockOutlined />
        }],
        {
            key: 'log',
            label: '日志',
            icon: <CodeOutlined />
        },
        {
            key: 'logout',
            label: '退出登录',
            icon: <LogoutOutlined />
        }
    ] as any

    function onUserClick(event: any) {
        switch (event.key) {
            case 'pin':
                setPinVisible(true)
                break
            case 'log':
                setLogOpen(true)
                break
            case 'logout':
                authDispatch.logout()
                break
        }
    }

    function renderDropdown(menu: any) {
        return (
            <div style={{
                backgroundColor: '#1a1a1d',
                borderRadius: 14,
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                overflow: 'hidden',
            }}>
                {/* 用户信息头部 */}
                <div style={{
                    padding: '16px 20px',
                    background: 'linear-gradient(135deg, rgba(212, 168, 82, 0.08) 0%, transparent 100%)',
                    borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
                }}>
                    <div style={{
                        fontSize: 15,
                        fontWeight: 600,
                        color: '#f0f0f2',
                        marginBottom: 4,
                    }}>{userInfo.name}</div>
                    <div style={{
                        fontSize: 12,
                        color: '#6a6a72',
                    }}>{userInfo.username}</div>
                </div>
                {menu}
            </div>
        )
    }


    return (
        <div className={`h-full flex items-center`}>
            <div className={'cursor-pointer flex items-center'} onClick={() => props.onCollapse?.()}>
                {props.collapsible && (
                    <IconButton ref={menuIconRef}>
                        <MenuOutlined style={{ color: '#a0a0a8', fontSize: 18 }} />
                    </IconButton>
                )}
                {!props.collapsible && (
                    (canBack && !responsive.lg) ? (
                        <IconButton ref={backIconRef} onClick={() => history.go(-1)}>
                            <ArrowLeftOutlined style={{ fontSize: 18, color: '#a0a0a8' }} />
                        </IconButton>
                    ) : (
                        <Link to={'/'}
                            className={'flex items-center group'}>
                            <img
                                className={`${responsive.lg ? 'ml-4 mr-4 h-12' : 'mr-1 h-10'} transition-all duration-300 group-hover:drop-shadow-[0_0_12px_rgba(212,168,82,0.4)]`}
                                src={Logo}
                                alt=""
                            />
                        </Link>
                    )
                )}
            </div>
            <div className={'flex-1 flex flex-row-reverse items-center h-full'}>
                <Space size={4} align="center">
                    {/* 隐私模式按钮 */}
                    <IconButton
                        ref={eyeIconRef}
                        onClick={() => onGoodBoyChange()}
                        style={{
                            background: isGoodBoy ? 'rgba(212, 168, 82, 0.1)' : 'transparent',
                            border: isGoodBoy ? '1px solid rgba(212, 168, 82, 0.3)' : '1px solid transparent',
                        }}
                    >
                        {isGoodBoy ? (
                            <EyeInvisibleOutlined style={{ fontSize: 18, color: '#d4a852' }} />
                        ) : (
                            <EyeOutlined style={{ fontSize: 18, color: '#a0a0a8' }} />
                        )}
                    </IconButton>

                    {/* 主题切换按钮 */}
                    <Dropdown menu={{ items: themeItems, onClick: onThemeClick }} arrow placement="bottomRight">
                        <IconButton ref={themeIconRef}>
                            <CurrentTheme.icon style={{ fontSize: 18, color: '#a0a0a8' }} />
                        </IconButton>
                    </Dropdown>

                    {/* 用户菜单按钮 */}
                    <Dropdown menu={{ items: userItems, onClick: onUserClick }} arrow placement="bottomRight" popupRender={renderDropdown}>
                        <IconButton
                            ref={userIconRef}
                            style={{
                                background: 'linear-gradient(135deg, rgba(212, 168, 82, 0.15) 0%, rgba(212, 168, 82, 0.05) 100%)',
                                border: '1px solid rgba(212, 168, 82, 0.2)',
                            }}
                        >
                            <UserOutlined style={{ fontSize: 18, color: '#d4a852' }} />
                        </IconButton>
                    </Dropdown>
                </Space>
            </div>
            <Modal
                title={'日志'}
                open={logOpen}
                onCancel={() => setLogOpen(false)}
                footer={null}
                destroyOnHidden
                width={1000}
                centered
                styles={{
                    content: {
                        background: '#1a1a1d',
                        borderRadius: 14,
                        border: '1px solid rgba(255, 255, 255, 0.08)',
                    },
                    header: {
                        background: 'transparent',
                        borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
                        paddingBottom: 16,
                    },
                }}
            >
                <Log />
            </Modal>
            {pinVisible && (
                <PinView pin={null} onClose={() => setPinVisible(false)} mode={PinMode.setting} />
            )}
        </div>
    )
}

export default Header
