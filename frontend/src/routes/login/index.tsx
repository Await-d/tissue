/*
 * @Author: Await
 * @Date: 2025-05-24 17:05:38
 * @LastEditors: Await
 * @LastEditTime: 2026-01-10 23:00:00
 * @Description: TISSUE+ 登录页 - 暗黑电影美学风格
 */
import { Button, Checkbox, Form, Input } from "antd";
import { LockOutlined, UserOutlined } from "@ant-design/icons";
import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Dispatch, RootState } from "../../models";
import Logo from "../../assets/logo.svg";
import { createFileRoute, redirect } from "@tanstack/react-router";
import { useThemeColors } from "../../hooks/useThemeColors";

export const Route = createFileRoute('/login/')({
    component: Login,
    beforeLoad: ({ context }) => {
        if (context.userToken) {
            throw redirect({
                to: '/'
            })
        }
    }
})

function Login() {

    const [form] = Form.useForm()
    const { logging } = useSelector((state: RootState) => state.auth)
    const { login } = useDispatch<Dispatch>().auth
    const colors = useThemeColors()

    useEffect(() => {
        document.body.style.backgroundColor = colors.bgBase
    }, [colors])

    return (
        <div
            className="h-dvh flex flex-col justify-center items-center relative overflow-hidden"
            style={{
                background: `linear-gradient(135deg, ${colors.bgBase} 0%, ${colors.bgElevated} 50%, ${colors.bgBase} 100%)`,
            }}
        >
            {/* 背景装饰 - 金色光晕 */}
            <div
                className="absolute top-1/4 -left-32 w-96 h-96 rounded-full opacity-5 blur-3xl"
                style={{
                    background: `radial-gradient(circle, ${colors.goldPrimary} 0%, transparent 70%)`,
                    animation: 'pulse 8s cubic-bezier(0.4, 0, 0.6, 1) infinite'
                }}
            />
            <div
                className="absolute bottom-1/4 -right-32 w-96 h-96 rounded-full opacity-5 blur-3xl"
                style={{
                    background: `radial-gradient(circle, ${colors.goldLight} 0%, transparent 70%)`,
                    animation: 'pulse 8s cubic-bezier(0.4, 0, 0.6, 1) infinite 2s'
                }}
            />

            {/* Logo 区域 - 带金色光晕 */}
            <div
                className="flex mb-10 relative"
                style={{
                    animation: 'tissueLogoEnter 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards',
                    opacity: 0
                }}
            >
                <div
                    className="absolute inset-0 blur-2xl opacity-40"
                    style={{
                        background: `radial-gradient(circle, ${colors.goldPrimary} 0%, transparent 70%)`,
                    }}
                />
                <img
                    className="h-20 relative z-10"
                    src={Logo}
                    alt="TISSUE+"
                    style={{
                        filter: `drop-shadow(0 0 20px ${colors.rgba('gold', 0.3)})`
                    }}
                />
            </div>

            {/* 登录卡片 - 玻璃态效果 */}
            <div
                className="w-[380px] relative"
                style={{
                    animation: 'tissueCardEnter 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) 0.2s forwards',
                    opacity: 0
                }}
            >
                <div
                    className="p-8 rounded-2xl relative overflow-hidden"
                    style={{
                        background: colors.rgba('black', 0.6),
                        backdropFilter: 'blur(40px) saturate(180%)',
                        WebkitBackdropFilter: 'blur(40px) saturate(180%)',
                        border: `1px solid ${colors.borderPrimary}`,
                        boxShadow: `0 8px 32px ${colors.rgba('black', 0.4)}, inset 0 1px 0 ${colors.rgba('white', 0.05)}`
                    }}
                >
                    {/* 顶部微光 */}
                    <div
                        className="absolute top-0 left-0 right-0 h-px"
                        style={{
                            background: `linear-gradient(90deg, transparent 0%, ${colors.rgba('gold', 0.3)} 50%, transparent 100%)`
                        }}
                    />

                    <Form
                        size="large"
                        form={form}
                        onFinish={(values) => login(values)}
                        style={{
                            '--ant-color-bg-container': colors.bgContainer,
                            '--ant-color-border': colors.borderPrimary,
                            '--ant-color-primary': colors.goldPrimary,
                            '--ant-color-text': colors.textPrimary,
                            '--ant-color-text-placeholder': colors.textTertiary,
                        } as React.CSSProperties}
                    >
                        {/* 用户名输入框 */}
                        <Form.Item name="username">
                            <Input
                                prefix={
                                    <UserOutlined
                                        style={{
                                            color: colors.textTertiary,
                                            fontSize: '16px'
                                        }}
                                    />
                                }
                                placeholder="用户名"
                                style={{
                                    height: '48px',
                                    backgroundColor: colors.bgElevated,
                                    border: `1px solid ${colors.borderPrimary}`,
                                    borderRadius: '10px',
                                    color: colors.textPrimary,
                                    fontSize: '15px',
                                    transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)'
                                }}
                                onFocus={(e) => {
                                    e.target.style.backgroundColor = colors.bgContainer
                                    e.target.style.borderColor = colors.goldPrimary
                                    e.target.style.boxShadow = `0 0 0 2px ${colors.rgba('gold', 0.1)}`
                                }}
                                onBlur={(e) => {
                                    e.target.style.backgroundColor = colors.bgElevated
                                    e.target.style.borderColor = colors.borderPrimary
                                    e.target.style.boxShadow = 'none'
                                }}
                            />
                        </Form.Item>

                        {/* 密码输入框 */}
                        <Form.Item name="password">
                            <Input.Password
                                prefix={
                                    <LockOutlined
                                        style={{
                                            color: colors.textTertiary,
                                            fontSize: '16px'
                                        }}
                                    />
                                }
                                placeholder="密码"
                                style={{
                                    height: '48px',
                                    backgroundColor: colors.bgElevated,
                                    border: `1px solid ${colors.borderPrimary}`,
                                    borderRadius: '10px',
                                    color: colors.textPrimary,
                                    fontSize: '15px',
                                    transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)'
                                }}
                                onFocus={(e) => {
                                    e.target.parentElement!.style.backgroundColor = colors.bgContainer
                                    e.target.parentElement!.style.borderColor = colors.goldPrimary
                                    e.target.parentElement!.style.boxShadow = `0 0 0 2px ${colors.rgba('gold', 0.1)}`
                                }}
                                onBlur={(e) => {
                                    e.target.parentElement!.style.backgroundColor = colors.bgElevated
                                    e.target.parentElement!.style.borderColor = colors.borderPrimary
                                    e.target.parentElement!.style.boxShadow = 'none'
                                }}
                            />
                        </Form.Item>

                        {/* 记住登录 */}
                        <Form.Item
                            noStyle
                            name="remember"
                            valuePropName="checked"
                        >
                            <Checkbox
                                style={{
                                    marginBottom: 24,
                                    color: colors.textSecondary,
                                    fontSize: '14px'
                                }}
                            >
                                保持登录
                            </Checkbox>
                        </Form.Item>

                        {/* 登录按钮 - 金色渐变 */}
                        <Button
                            type="primary"
                            htmlType="submit"
                            loading={logging}
                            style={{
                                width: '100%',
                                height: '48px',
                                background: colors.goldGradient,
                                border: 'none',
                                borderRadius: '10px',
                                fontSize: '16px',
                                fontWeight: 600,
                                color: colors.bgBase,
                                boxShadow: `0 4px 16px ${colors.rgba('gold', 0.25)}`,
                                transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
                                cursor: logging ? 'not-allowed' : 'pointer'
                            }}
                            onMouseEnter={(e) => {
                                if (!logging) {
                                    e.currentTarget.style.background = colors.goldGradientHover
                                    e.currentTarget.style.boxShadow = `0 0 24px ${colors.rgba('gold', 0.4)}, 0 8px 24px ${colors.rgba('black', 0.3)}`
                                    e.currentTarget.style.transform = 'translateY(-2px)'
                                }
                            }}
                            onMouseLeave={(e) => {
                                if (!logging) {
                                    e.currentTarget.style.background = colors.goldGradient
                                    e.currentTarget.style.boxShadow = `0 4px 16px ${colors.rgba('gold', 0.25)}`
                                    e.currentTarget.style.transform = 'translateY(0)'
                                }
                            }}
                            onMouseDown={(e) => {
                                if (!logging) {
                                    e.currentTarget.style.transform = 'translateY(0) scale(0.98)'
                                }
                            }}
                            onMouseUp={(e) => {
                                if (!logging) {
                                    e.currentTarget.style.transform = 'translateY(-2px) scale(1)'
                                }
                            }}
                        >
                            {logging ? '登录中...' : '登录'}
                        </Button>
                    </Form>
                </div>

                {/* 底部装饰光晕 */}
                <div
                    className="absolute -bottom-10 left-1/2 -translate-x-1/2 w-3/4 h-20 blur-3xl opacity-20 pointer-events-none"
                    style={{
                        background: `radial-gradient(ellipse, ${colors.goldPrimary} 0%, transparent 70%)`,
                    }}
                />
            </div>

            {/* 底部版权信息 */}
            <div
                className="absolute bottom-8 text-center"
                style={{
                    color: colors.textTertiary,
                    fontSize: '13px',
                    animation: 'tissueFadeIn 1s ease-out 0.4s forwards',
                    opacity: 0
                }}
            >
                <div>TISSUE+ · 暗黑电影美学</div>
            </div>

            {/* 动画定义 */}
            <style>{`
                @keyframes tissueLogoEnter {
                    0% {
                        opacity: 0;
                        transform: translateY(-20px) scale(0.9);
                    }
                    100% {
                        opacity: 1;
                        transform: translateY(0) scale(1);
                    }
                }

                @keyframes tissueCardEnter {
                    0% {
                        opacity: 0;
                        transform: translateY(30px) scale(0.95);
                    }
                    100% {
                        opacity: 1;
                        transform: translateY(0) scale(1);
                    }
                }

                @keyframes tissueFadeIn {
                    0% {
                        opacity: 0;
                    }
                    100% {
                        opacity: 1;
                    }
                }

                @keyframes pulse {
                    0%, 100% {
                        transform: scale(1);
                        opacity: 0.05;
                    }
                    50% {
                        transform: scale(1.1);
                        opacity: 0.08;
                    }
                }

                /* Ant Design 输入框样式覆盖 */
                .ant-input,
                .ant-input-password {
                    background-color: ${colors.bgElevated} !important;
                    border: 1px solid ${colors.borderPrimary} !important;
                    color: ${colors.textPrimary} !important;
                }

                .ant-input::placeholder,
                .ant-input-password input::placeholder {
                    color: ${colors.textTertiary} !important;
                }

                .ant-input:focus,
                .ant-input-password:focus,
                .ant-input-password-focused,
                .ant-input:hover,
                .ant-input-password:hover {
                    background-color: ${colors.bgContainer} !important;
                    border-color: ${colors.goldPrimary} !important;
                    box-shadow: 0 0 0 2px ${colors.rgba('gold', 0.1)} !important;
                }

                .ant-input-password .ant-input {
                    background-color: transparent !important;
                    border: none !important;
                }

                .ant-input-suffix {
                    color: ${colors.textTertiary} !important;
                }

                .ant-checkbox-wrapper {
                    color: ${colors.textSecondary} !important;
                }

                .ant-checkbox-inner {
                    background-color: ${colors.bgElevated} !important;
                    border-color: ${colors.borderPrimary} !important;
                }

                .ant-checkbox-checked .ant-checkbox-inner {
                    background-color: ${colors.goldPrimary} !important;
                    border-color: ${colors.goldPrimary} !important;
                }

                .ant-checkbox:hover .ant-checkbox-inner {
                    border-color: ${colors.goldPrimary} !important;
                }

                .ant-form-item {
                    margin-bottom: 20px;
                }

                .ant-form-item-explain-error {
                    color: ${colors.error} !important;
                    font-size: 13px;
                    margin-top: 4px;
                }
            `}</style>
        </div>
    )
}

