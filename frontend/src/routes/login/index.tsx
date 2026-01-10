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

    useEffect(() => {
        document.body.style.backgroundColor = '#0d0d0f'
    }, [])

    return (
        <div
            className="h-dvh flex flex-col justify-center items-center relative overflow-hidden"
            style={{
                background: 'linear-gradient(135deg, #0d0d0f 0%, #141416 50%, #0d0d0f 100%)',
            }}
        >
            {/* 背景装饰 - 金色光晕 */}
            <div
                className="absolute top-1/4 -left-32 w-96 h-96 rounded-full opacity-5 blur-3xl"
                style={{
                    background: 'radial-gradient(circle, #d4a852 0%, transparent 70%)',
                    animation: 'pulse 8s cubic-bezier(0.4, 0, 0.6, 1) infinite'
                }}
            />
            <div
                className="absolute bottom-1/4 -right-32 w-96 h-96 rounded-full opacity-5 blur-3xl"
                style={{
                    background: 'radial-gradient(circle, #e8c780 0%, transparent 70%)',
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
                        background: 'radial-gradient(circle, #d4a852 0%, transparent 70%)',
                    }}
                />
                <img
                    className="h-20 relative z-10"
                    src={Logo}
                    alt="TISSUE+"
                    style={{
                        filter: 'drop-shadow(0 0 20px rgba(212, 168, 82, 0.3))'
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
                        background: 'rgba(26, 26, 29, 0.6)',
                        backdropFilter: 'blur(40px) saturate(180%)',
                        WebkitBackdropFilter: 'blur(40px) saturate(180%)',
                        border: '1px solid rgba(255, 255, 255, 0.08)',
                        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05)'
                    }}
                >
                    {/* 顶部微光 */}
                    <div
                        className="absolute top-0 left-0 right-0 h-px"
                        style={{
                            background: 'linear-gradient(90deg, transparent 0%, rgba(212, 168, 82, 0.3) 50%, transparent 100%)'
                        }}
                    />

                    <Form
                        size="large"
                        form={form}
                        onFinish={(values) => login(values)}
                        style={{
                            '--ant-color-bg-container': '#1a1a1d',
                            '--ant-color-border': 'rgba(255, 255, 255, 0.08)',
                            '--ant-color-primary': '#d4a852',
                            '--ant-color-text': '#f0f0f2',
                            '--ant-color-text-placeholder': '#6a6a72',
                        } as React.CSSProperties}
                    >
                        {/* 用户名输入框 */}
                        <Form.Item name="username">
                            <Input
                                prefix={
                                    <UserOutlined
                                        style={{
                                            color: '#6a6a72',
                                            fontSize: '16px'
                                        }}
                                    />
                                }
                                placeholder="用户名"
                                style={{
                                    height: '48px',
                                    backgroundColor: '#141416',
                                    border: '1px solid rgba(255, 255, 255, 0.08)',
                                    borderRadius: '10px',
                                    color: '#f0f0f2',
                                    fontSize: '15px',
                                    transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)'
                                }}
                                onFocus={(e) => {
                                    e.target.style.backgroundColor = '#1a1a1d'
                                    e.target.style.borderColor = '#d4a852'
                                    e.target.style.boxShadow = '0 0 0 2px rgba(212, 168, 82, 0.1)'
                                }}
                                onBlur={(e) => {
                                    e.target.style.backgroundColor = '#141416'
                                    e.target.style.borderColor = 'rgba(255, 255, 255, 0.08)'
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
                                            color: '#6a6a72',
                                            fontSize: '16px'
                                        }}
                                    />
                                }
                                placeholder="密码"
                                style={{
                                    height: '48px',
                                    backgroundColor: '#141416',
                                    border: '1px solid rgba(255, 255, 255, 0.08)',
                                    borderRadius: '10px',
                                    color: '#f0f0f2',
                                    fontSize: '15px',
                                    transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)'
                                }}
                                onFocus={(e) => {
                                    e.target.parentElement!.style.backgroundColor = '#1a1a1d'
                                    e.target.parentElement!.style.borderColor = '#d4a852'
                                    e.target.parentElement!.style.boxShadow = '0 0 0 2px rgba(212, 168, 82, 0.1)'
                                }}
                                onBlur={(e) => {
                                    e.target.parentElement!.style.backgroundColor = '#141416'
                                    e.target.parentElement!.style.borderColor = 'rgba(255, 255, 255, 0.08)'
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
                                    color: '#a0a0a8',
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
                                background: 'linear-gradient(135deg, #d4a852 0%, #b08d3e 100%)',
                                border: 'none',
                                borderRadius: '10px',
                                fontSize: '16px',
                                fontWeight: 600,
                                color: '#0d0d0f',
                                boxShadow: '0 4px 16px rgba(212, 168, 82, 0.25)',
                                transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
                                cursor: logging ? 'not-allowed' : 'pointer'
                            }}
                            onMouseEnter={(e) => {
                                if (!logging) {
                                    e.currentTarget.style.background = 'linear-gradient(135deg, #e8c780 0%, #d4a852 100%)'
                                    e.currentTarget.style.boxShadow = '0 0 24px rgba(212, 168, 82, 0.4), 0 8px 24px rgba(0, 0, 0, 0.3)'
                                    e.currentTarget.style.transform = 'translateY(-2px)'
                                }
                            }}
                            onMouseLeave={(e) => {
                                if (!logging) {
                                    e.currentTarget.style.background = 'linear-gradient(135deg, #d4a852 0%, #b08d3e 100%)'
                                    e.currentTarget.style.boxShadow = '0 4px 16px rgba(212, 168, 82, 0.25)'
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
                        background: 'radial-gradient(ellipse, #d4a852 0%, transparent 70%)',
                    }}
                />
            </div>

            {/* 底部版权信息 */}
            <div
                className="absolute bottom-8 text-center"
                style={{
                    color: '#6a6a72',
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
                    background-color: #141416 !important;
                    border: 1px solid rgba(255, 255, 255, 0.08) !important;
                    color: #f0f0f2 !important;
                }

                .ant-input::placeholder,
                .ant-input-password input::placeholder {
                    color: #6a6a72 !important;
                }

                .ant-input:focus,
                .ant-input-password:focus,
                .ant-input-password-focused,
                .ant-input:hover,
                .ant-input-password:hover {
                    background-color: #1a1a1d !important;
                    border-color: #d4a852 !important;
                    box-shadow: 0 0 0 2px rgba(212, 168, 82, 0.1) !important;
                }

                .ant-input-password .ant-input {
                    background-color: transparent !important;
                    border: none !important;
                }

                .ant-input-suffix {
                    color: #6a6a72 !important;
                }

                .ant-checkbox-wrapper {
                    color: #a0a0a8 !important;
                }

                .ant-checkbox-inner {
                    background-color: #141416 !important;
                    border-color: rgba(255, 255, 255, 0.08) !important;
                }

                .ant-checkbox-checked .ant-checkbox-inner {
                    background-color: #d4a852 !important;
                    border-color: #d4a852 !important;
                }

                .ant-checkbox:hover .ant-checkbox-inner {
                    border-color: #d4a852 !important;
                }

                .ant-form-item {
                    margin-bottom: 20px;
                }

                .ant-form-item-explain-error {
                    color: #ff4d4f !important;
                    font-size: 13px;
                    margin-top: 4px;
                }
            `}</style>
        </div>
    )
}

