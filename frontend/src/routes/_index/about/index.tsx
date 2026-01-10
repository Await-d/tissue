import Logo from "../../../assets/logo.svg";
import { Card, Space, Tag, Typography, Divider } from "antd";
import { useResponsive } from "ahooks";
import { useSelector } from "react-redux";
import { RootState } from "../../../models";
import { DockerOutlined, GithubOutlined } from "@ant-design/icons";
import { createFileRoute } from "@tanstack/react-router";
import React from "react";
import { useThemeColors } from '../../../hooks/useThemeColors';

const { Paragraph, Link } = Typography;

export const Route = createFileRoute('/_index/about/')({
    component: About
})

function About() {

    const responsive = useResponsive()
    const themeColors = useThemeColors()
    const { versions } = useSelector((state: RootState) => state.auth)
    const [hoveredIcon, setHoveredIcon] = React.useState<string | null>(null);

    // 兼容旧结构的颜色对象
    const colors = {
        bg: {
            base: themeColors.bgBase,
            elevated: themeColors.bgElevated,
            container: themeColors.bgContainer,
            spotlight: themeColors.bgSpotlight
        },
        gold: {
            primary: themeColors.goldPrimary,
            light: themeColors.goldLight,
            dark: themeColors.goldDark
        },
        text: {
            primary: themeColors.textPrimary,
            secondary: themeColors.textSecondary,
            tertiary: themeColors.textTertiary
        },
        border: themeColors.borderPrimary
    }

    return (
        <>
            <style>
                {`
                    @keyframes logoGlow {
                        0%, 100% {
                            filter: drop-shadow(0 0 20px ${colors.gold.primary}40);
                        }
                        50% {
                            filter: drop-shadow(0 0 30px ${colors.gold.primary}60);
                        }
                    }
                    
                    @keyframes fadeInUp {
                        from {
                            opacity: 0;
                            transform: translateY(20px);
                        }
                        to {
                            opacity: 1;
                            transform: translateY(0);
                        }
                    }
                    
                    @keyframes fadeIn {
                        from {
                            opacity: 0;
                        }
                        to {
                            opacity: 1;
                        }
                    }
                    
                    @keyframes scaleIn {
                        from {
                            opacity: 0;
                            transform: scale(0.9);
                        }
                        to {
                            opacity: 1;
                            transform: scale(1);
                        }
                    }
                `}
            </style>
            <Card
                variant="borderless"
                style={{
                    background: colors.bg.elevated,
                    borderRadius: '16px',
                    overflow: 'hidden'
                }}
                styles={{
                    body: {
                        background: `linear-gradient(180deg, ${colors.bg.elevated} 0%, ${colors.bg.base} 100%)`,
                        padding: responsive.md ? '48px 32px' : '32px 20px'
                    }
                }}
            >
                <div className="flex flex-col justify-center items-center">
                    {/* Logo with golden glow */}
                    <div style={{
                        animation: 'logoGlow 3s ease-in-out infinite, scaleIn 0.6s ease-out'
                    }}>
                        <img 
                            className={'h-20'} 
                            src={Logo} 
                            alt="TISSUE+ Logo"
                            style={{
                                filter: `drop-shadow(0 0 20px ${colors.gold.primary}40)`
                            }}
                        />
                    </div>
                    
                    {/* Version info card */}
                    <div
                        style={{
                            marginTop: '24px',
                            padding: '16px 24px',
                            background: colors.bg.container,
                            borderRadius: '12px',
                            border: `1px solid ${colors.border}`,
                            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.2)',
                            animation: 'fadeInUp 0.6s ease-out 0.2s both'
                        }}
                    >
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                            flexWrap: 'wrap',
                            justifyContent: 'center'
                        }}>
                            <span style={{ 
                                color: colors.text.secondary,
                                fontSize: '14px'
                            }}>
                                当前版本：
                            </span>
                            <span style={{
                                color: colors.gold.primary,
                                fontSize: '16px',
                                fontWeight: 600,
                                fontFamily: 'monospace'
                            }}>
                                {versions?.current}
                            </span>
                            {versions?.hasNew && (
                                <Tag 
                                    style={{
                                        background: `linear-gradient(135deg, ${colors.gold.dark}, ${colors.gold.primary})`,
                                        color: colors.bg.base,
                                        border: 'none',
                                        fontWeight: 600,
                                        padding: '4px 12px',
                                        borderRadius: '6px'
                                    }}
                                >
                                    新版本：{versions?.latest}
                                </Tag>
                            )}
                        </div>
                    </div>
                    
                    {/* Social icons */}
                    <Space 
                        size={"large"} 
                        className={'mt-6'}
                        style={{
                            fontSize: '40px',
                            animation: 'fadeIn 0.6s ease-out 0.4s both'
                        }}
                    >
                        <div 
                            className={'cursor-pointer'} 
                            onClick={() => window.open('https://github.com/Await-d/tissue')}
                            onMouseEnter={() => setHoveredIcon('github')}
                            onMouseLeave={() => setHoveredIcon(null)}
                            style={{
                                color: hoveredIcon === 'github' ? colors.gold.light : colors.gold.primary,
                                transition: 'all 0.3s ease',
                                filter: hoveredIcon === 'github' 
                                    ? `drop-shadow(0 0 12px ${colors.gold.primary})` 
                                    : 'none',
                                transform: hoveredIcon === 'github' ? 'translateY(-3px) scale(1.1)' : 'scale(1)'
                            }}
                        >
                            <GithubOutlined />
                        </div>
                        <div 
                            className={'cursor-pointer'}
                            onClick={() => window.open('https://hub.docker.com/r/chris2s/tissue-plus')}
                            onMouseEnter={() => setHoveredIcon('docker')}
                            onMouseLeave={() => setHoveredIcon(null)}
                            style={{
                                color: hoveredIcon === 'docker' ? colors.gold.light : colors.gold.primary,
                                transition: 'all 0.3s ease',
                                filter: hoveredIcon === 'docker' 
                                    ? `drop-shadow(0 0 12px ${colors.gold.primary})` 
                                    : 'none',
                                transform: hoveredIcon === 'docker' ? 'translateY(-3px) scale(1.1)' : 'scale(1)'
                            }}
                        >
                            <DockerOutlined />
                        </div>
                    </Space>
                    
                    {/* Badges */}
                    <div style={{
                        animation: 'fadeIn 0.6s ease-out 0.6s both'
                    }}>
                        {responsive.md ? (
                            <Space align={"center"} wrap={true} className={'mt-4'}>
                                <img src="https://img.shields.io/github/license/Await-d/tissue" alt="" />
                                <img src="https://img.shields.io/docker/v/chris2s/tissue-plus/latest" alt="" />
                                <img src="https://img.shields.io/docker/image-size/chris2s/tissue-plus/latest" alt="" />
                                <img src="https://img.shields.io/github/actions/workflow/status/Await-d/tissue/build.yml"
                                    alt="" />
                            </Space>
                        ) : (
                            <>
                                <Space align={"center"} wrap={true} className={'mt-4'}>
                                    <img src="https://img.shields.io/github/license/Await-d/tissue" alt="" />
                                    <img src="https://img.shields.io/docker/v/chris2s/tissue-plus" alt="" />
                                </Space>
                                <Space align={"center"} wrap={true} className={'mt-2'}>
                                    <img src="https://img.shields.io/docker/image-size/chris2s/tissue-plus" alt="" />
                                    <img src="https://img.shields.io/github/actions/workflow/status/Await-d/tissue/build.yml"
                                        alt="" />
                                </Space>
                            </>
                        )}
                    </div>
                    
                    {/* Description */}
                    <div 
                        className={'text-center mt-6'}
                        style={{
                            color: colors.text.secondary,
                            fontSize: '15px',
                            lineHeight: '1.8',
                            maxWidth: '600px',
                            padding: '20px',
                            background: colors.bg.container,
                            borderRadius: '12px',
                            border: `1px solid ${colors.border}`,
                            animation: 'fadeInUp 0.6s ease-out 0.7s both'
                        }}
                    >
                        老师教材刮削工具，提供海报下载、元数据匹配等功能，使教材能够在Jellyfin、Emby、Kodi等工具里装订成册，便于学习。
                    </div>
                    
                    <Divider style={{ 
                        borderColor: colors.border,
                        margin: '32px 0',
                        animation: 'fadeIn 0.6s ease-out 0.8s both'
                    }} />
                    
                    {/* Attribution */}
                    <Paragraph 
                        className="text-center"
                        style={{
                            color: colors.text.secondary,
                            fontSize: '14px',
                            marginBottom: '16px',
                            animation: 'fadeIn 0.6s ease-out 0.9s both'
                        }}
                    >
                        本项目基于 <Link 
                            href="https://github.com/chris-2s/tissue" 
                            target="_blank"
                            style={{
                                color: colors.gold.primary,
                                textDecoration: 'none',
                                borderBottom: `1px solid ${colors.gold.dark}`,
                                transition: 'all 0.3s ease'
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.color = colors.gold.light;
                                e.currentTarget.style.borderColor = colors.gold.light;
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.color = colors.gold.primary;
                                e.currentTarget.style.borderColor = colors.gold.dark;
                            }}
                        >
                            chris-2s/tissue
                        </Link> 进行二次开发，感谢原作者的贡献。
                    </Paragraph>
                    
                    {/* Disclaimer */}
                    <div style={{
                        maxWidth: '600px',
                        animation: 'fadeIn 0.6s ease-out 1s both'
                    }}>
                        <div 
                            className={'text-center mt-4'}
                            style={{
                                color: colors.text.tertiary,
                                fontSize: '13px',
                                lineHeight: '1.8'
                            }}
                        >
                            本软件所涉及的数据均通过互联网爬取获取，数据版权归原作者或发布平台所有。
                        </div>
                        <div 
                            className={'text-center mt-2'}
                            style={{
                                color: colors.text.tertiary,
                                fontSize: '13px',
                                lineHeight: '1.8'
                            }}
                        >
                            本软件仅作为数据展示与整合的工具，并不提供任何数据的原创或拥有权。
                        </div>
                    </div>
                </div>
            </Card>
        </>
    )
}

