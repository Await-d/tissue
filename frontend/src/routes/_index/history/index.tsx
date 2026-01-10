import {Button, Card, Input, App, Modal, Space, Table, Tag} from "antd";
import {ColumnsType} from "antd/lib/table";
import * as api from "../../../apis/history";
import {useDebounce, useRequest} from "ahooks";
import dayjs from "dayjs";
import React, {useMemo, useState} from "react";
import {DeleteOutlined, EditOutlined, SearchOutlined} from "@ant-design/icons";
import More from "../../../components/More";
import {createFileRoute} from "@tanstack/react-router";
import VideoDetail from "../../../components/VideoDetail";
import {TransModeOptions} from "../../../utils/constants.ts";

export const Route = createFileRoute('/_index/history/')({
    component: History,
})

function History() {
    const { message, modal } = App.useApp()
    const {data = [], loading, refresh} = useRequest(api.getHistories, {})
    const [selected, setSelected] = useState<any | undefined>()
    const [keyword, setKeyword] = useState<string>()
    const keywordDebounce = useDebounce(keyword, {wait: 1000})

    const realData = useMemo(() => {
        return data.filter((item: any) => {
            return !keywordDebounce ||
                item.num?.indexOf(keywordDebounce) > -1 ||
                item.source_path?.indexOf(keywordDebounce) > -1 ||
                item.dest_path?.indexOf(keywordDebounce) > -1
        })
    }, [data, keywordDebounce])

    const {run: onDelete} = useRequest(api.deleteHistory, {
        manual: true,
        onSuccess: () => {
            refresh()
            message.success("删除成功")
        }
    })

    const columns: ColumnsType<any> = [
        {
            title: '状态',
            dataIndex: 'status',
            render: (value) => (
                value ? (
                    <Tag 
                        style={{
                            background: 'rgba(212, 168, 82, 0.1)',
                            border: '1px solid rgba(212, 168, 82, 0.3)',
                            color: '#d4a852'
                        }}
                    >
                        成功
                    </Tag>
                ) : (
                    <Tag 
                        style={{
                            background: 'rgba(255, 77, 79, 0.1)',
                            border: '1px solid rgba(255, 77, 79, 0.3)',
                            color: '#ff4d4f'
                        }}
                    >
                        失败
                    </Tag>
                )
            )
        },
        {
            title: '番号',
            dataIndex: 'num',
            render: (value, record: any) => (
                <div>
                    <b style={{ color: '#f0f0f2' }}>{value}</b>
                    <div style={{ marginTop: 4 }}>
                        {record.is_zh && (
                            <Tag 
                                style={{
                                    background: 'rgba(212, 168, 82, 0.12)',
                                    border: '1px solid rgba(212, 168, 82, 0.25)',
                                    color: '#e8c780',
                                    marginRight: 4
                                }}
                            >
                                中文
                            </Tag>
                        )}
                        {record.is_uncensored && (
                            <Tag 
                                style={{
                                    background: 'rgba(212, 168, 82, 0.12)',
                                    border: '1px solid rgba(212, 168, 82, 0.25)',
                                    color: '#e8c780'
                                }}
                            >
                                无码
                            </Tag>
                        )}
                    </div>
                </div>
            )
        },
        {
            title: '路径',
            dataIndex: 'path',
            render: (_, record: any) => (
                <div 
                    style={{
                        WebkitTextSizeAdjust: '100%', 
                        fontSize: 13, 
                        maxWidth: 680,
                        color: '#a0a0a8',
                        lineHeight: '1.6'
                    }}
                >
                    <div style={{ marginBottom: 4 }}>{record.source_path}</div>
                    <div style={{ 
                        color: '#d4a852', 
                        fontSize: 12,
                        margin: '6px 0' 
                    }}>
                        ⟹
                    </div>
                    <div>{record.dest_path}</div>
                </div>
            )
        },
        {
            title: '转移方式',
            dataIndex: 'trans_method',
            render: (value: string) => {
                const method = TransModeOptions.find((i: any) => i.value === value)
                return (
                    <Tag 
                        style={{
                            background: 'rgba(212, 168, 82, 0.1)',
                            border: '1px solid rgba(212, 168, 82, 0.3)',
                            color: '#d4a852'
                        }}
                    >
                        {method?.name}
                    </Tag>
                )
            }
        },
        {
            title: '时间',
            dataIndex: 'create_time',
            render: (value) => (
                <span style={{ color: '#a0a0a8', fontSize: 13 }}>
                    {dayjs(value).format('lll')}
                </span>
            )
        },
        {
            title: '',
            dataIndex: 'operations',
            width: 20,
            fixed: 'right',
            render: (_, record) => (
                !record.is_admin && (
                    <More items={items} onClick={(key) => onMoreClick(key, record)}/>
                )
            )
        }
    ]

    const items = [
        {
            key: 'edit',
            label: '重新整理',
            icon: <EditOutlined/>
        },
        {
            key: 'delete',
            label: '删除记录',
            icon: <DeleteOutlined/>
        },
    ] as any

    function onMoreClick(key: string, record: any) {
        if (key === 'edit') {
            setSelected(record)
        } else if (key === 'delete') {
            modal.confirm({
                title: '是否确认删除记录',
                onOk: () => {
                    onDelete(record.id)
                }
            })
        }
    }

    return (
        <div className="history-page-wrapper animate-fade-in">
            <Card 
                title={<span style={{ color: '#f0f0f2', fontSize: 18, fontWeight: 500 }}>历史记录</span>}
                className="dark-card"
                style={{
                    background: '#141416',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: 8
                }}
                extra={(
                    <Space.Compact>
                        <Input 
                            value={keyword} 
                            onChange={e => setKeyword(e.target.value)} 
                            placeholder={'搜索番号或路径'}
                            style={{
                                background: '#1a1a1d',
                                border: '1px solid rgba(255, 255, 255, 0.08)',
                                color: '#f0f0f2'
                            }}
                            className="dark-input"
                        />
                        <Button 
                            icon={<SearchOutlined/>}
                            style={{
                                background: '#1a1a1d',
                                border: '1px solid rgba(255, 255, 255, 0.08)',
                                color: '#d4a852'
                            }}
                        />
                    </Space.Compact>
                )}
            >
                <Table 
                    rowKey={'id'} 
                    scroll={{x: 'max-content'}} 
                    columns={columns} 
                    loading={loading}
                    dataSource={realData}
                    className="dark-table"
                    rowClassName="dark-table-row"
                    style={{
                        background: 'transparent'
                    }}
                />
                <VideoDetail 
                    title={'重新整理'}
                    mode={'history'}
                    transMode={selected?.status ? 'move' : selected?.trans_mode}
                    width={1100}
                    path={selected?.status ? selected?.dest_path : selected?.source_path}
                    open={!!selected}
                    onCancel={() => setSelected(undefined)}
                    onOk={() => {
                        setSelected(undefined)
                        refresh()
                    }}
                />
            </Card>
        </div>
    )
}

