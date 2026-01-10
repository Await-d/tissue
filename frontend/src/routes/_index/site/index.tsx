import {createFileRoute, Link} from "@tanstack/react-router";
import {Badge, Card, Empty, FloatButton, List, message, Skeleton, Space, Tag, theme} from "antd";
import ModifyModal from "./-components/modifyModal.tsx";
import {useFormModal} from "../../../utils/useFormModal.ts";
import * as api from "../../../apis/site.ts";
import {useRequest} from "ahooks";
import {createPortal} from "react-dom";
import {RedoOutlined} from "@ant-design/icons";
import React from "react";


export const Route = createFileRoute('/_index/site/')({
    component: Site
})

function Site() {

    const {token} = theme.useToken()

    const {data, refresh, loading} = useRequest(api.getSites, {})

    const {modalProps, setOpen} = useFormModal({
        service: api.modifySite,
        onOk: () => {
            setOpen(false)
            refresh()
        }
    })

    const {run: onTesting} = useRequest(api.testingSits, {
        manual: true,
        onSuccess: () => {
            message.success("站点刷新提交成功")
        }
    })

    function renderItem(item: any) {
        return (
            <List.Item>
                <Badge.Ribbon
                    text={item.status ? '启用' : '停用'}
                    color={item.status ? '#d4a852' : '#6a6a72'}
                    style={{
                        fontSize: '12px',
                        fontWeight: 500
                    }}
                >
                    <Card
                        size={'default'}
                        title={(
                            <div className={'flex items-center gap-2'}>
                                <Tag
                                    variant="borderless"
                                    style={{
                                        background: 'rgba(212, 168, 82, 0.15)',
                                        color: '#d4a852',
                                        border: '1px solid rgba(212, 168, 82, 0.3)',
                                        fontWeight: 600,
                                        minWidth: '32px',
                                        textAlign: 'center'
                                    }}
                                >
                                    {item.priority}
                                </Tag>
                                <div style={{color: '#f0f0f2', fontWeight: 500}}>{item.name}</div>
                            </div>
                        )}
                        className={'cursor-pointer site-card'}
                        onClick={() => setOpen(true, item)}
                        style={{
                            background: '#1a1a1d',
                            border: '1px solid rgba(255, 255, 255, 0.08)',
                            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
                            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                            overflow: 'hidden'
                        }}
                        styles={{
                            header: {
                                background: '#222226',
                                borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
                                padding: '12px 16px'
                            },
                            body: {
                                padding: '16px'
                            }
                        }}
                    >
                        <Space direction={"vertical"} size={'large'} style={{width: '100%'}}>
                            <div style={{
                                color: '#a0a0a8',
                                fontSize: '13px',
                                lineHeight: '1.5'
                            }}>
                                <span>{item.alternate_host || '未设置替代域名'}</span>
                            </div>
                            <div className={'flex gap-2'}>
                                <Tag
                                    color={'blue'}
                                    variant="borderless"
                                    style={{
                                        background: 'rgba(24, 144, 255, 0.15)',
                                        border: '1px solid rgba(24, 144, 255, 0.3)',
                                        color: '#69b1ff'
                                    }}
                                >
                                    元数据
                                </Tag>
                                {item.downloadable && (
                                    <Tag
                                        color={'green'}
                                        variant="borderless"
                                        style={{
                                            background: 'rgba(82, 196, 26, 0.15)',
                                            border: '1px solid rgba(82, 196, 26, 0.3)',
                                            color: '#95de64'
                                        }}
                                    >
                                        下载
                                    </Tag>
                                )}
                            </div>
                        </Space>
                    </Card>
                </Badge.Ribbon>
            </List.Item>
        )
    }

    if (loading) {
        return (
            <Card
                style={{
                    background: '#1a1a1d',
                    border: '1px solid rgba(255, 255, 255, 0.08)'
                }}
            >
                <Skeleton active/>
            </Card>
        )
    }

    return (
        <>
            <style>{`
                .site-card:hover {
                    transform: translateY(-4px);
                    border-color: rgba(212, 168, 82, 0.4) !important;
                    box-shadow: 0 8px 24px rgba(212, 168, 82, 0.15), 0 0 0 1px rgba(212, 168, 82, 0.2) !important;
                }

                .site-card .ant-card-head-title {
                    padding: 0;
                }
            `}</style>

            {(data && data.length > 0) ? (
                <List grid={{gutter: 16, xxl: 4, xl: 4, lg: 4, md: 2, xs: 1}}
                      dataSource={data}
                      renderItem={renderItem}/>
            ) : (
                <Card
                    title={'站点'}
                    style={{
                        background: '#1a1a1d',
                        border: '1px solid rgba(255, 255, 255, 0.08)'
                    }}
                    styles={{
                        header: {
                            background: '#222226',
                            borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
                            color: '#f0f0f2'
                        }
                    }}
                >
                    <Empty
                        description={(
                            <div style={{color: '#a0a0a8'}}>
                                <div>无可用站点</div>
                                <div>
                                    请检查网络连接后{' '}
                                    <a
                                        onClick={() => onTesting()}
                                        style={{
                                            color: '#d4a852',
                                            textDecoration: 'underline',
                                            cursor: 'pointer'
                                        }}
                                    >
                                        刷新站点
                                    </a>
                                </div>
                            </div>
                        )}
                    />
                </Card>
            )}
            <ModifyModal {...modalProps} />
            {createPortal((
                    <>
                        <FloatButton
                            icon={<RedoOutlined/>}
                            onClick={() => onTesting()}
                            style={{
                                background: '#d4a852',
                                boxShadow: '0 4px 12px rgba(212, 168, 82, 0.3)'
                            }}
                        />
                    </>
                ), document.getElementsByClassName('index-float-button-group')[0]
            )}
        </>
    )
}
