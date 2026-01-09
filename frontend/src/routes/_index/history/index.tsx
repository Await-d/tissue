import {Card, Col, Input, message, Modal, Row, Select, Statistic, Table, Tag, theme} from "antd";
import {ColumnsType} from "antd/lib/table";
import * as api from "../../../apis/history";
import {useDebounce, useRequest} from "ahooks";
import dayjs from "dayjs";
import React, {useMemo, useState} from "react";
import {
    DeleteOutlined,
    EditOutlined,
    CheckCircleOutlined,
    CloseCircleOutlined,
    HistoryOutlined,
    SearchOutlined,
    FileTextOutlined
} from "@ant-design/icons";
import More from "../../../components/More";
import {createFileRoute} from "@tanstack/react-router";
import VideoDetail from "../../../components/VideoDetail";
import {TransModeOptions} from "../../../utils/constants.ts";

export const Route = createFileRoute('/_index/history/')({
    component: History,
})

interface HistoryItem {
    id: number;
    num: string;
    status: boolean;
    source_path: string;
    dest_path: string;
    trans_method: string;
    create_time: string;
    is_zh?: boolean;
    is_uncensored?: boolean;
}

function History() {
    const {token} = theme.useToken()
    const {data = [], loading, refresh} = useRequest(api.getHistories, {})
    const [selected, setSelected] = useState<HistoryItem | undefined>()
    const [keyword, setKeyword] = useState<string>('')
    const [statusFilter, setStatusFilter] = useState<string>('all')
    const keywordDebounce = useDebounce(keyword, {wait: 300})

    // 统计数据
    const statistics = useMemo(() => {
        const total = data.length;
        const success = data.filter((item: HistoryItem) => item.status).length;
        const failed = total - success;
        const today = data.filter((item: HistoryItem) =>
            dayjs(item.create_time).isAfter(dayjs().startOf('day'))
        ).length;
        return {total, success, failed, today};
    }, [data])

    // 过滤数据
    const filteredData = useMemo(() => {
        return data.filter((item: HistoryItem) => {
            // 关键词过滤
            const matchKeyword = !keywordDebounce ||
                item.num?.toLowerCase().includes(keywordDebounce.toLowerCase()) ||
                item.source_path?.toLowerCase().includes(keywordDebounce.toLowerCase()) ||
                item.dest_path?.toLowerCase().includes(keywordDebounce.toLowerCase());

            // 状态过滤
            const matchStatus = statusFilter === 'all' ||
                (statusFilter === 'success' && item.status) ||
                (statusFilter === 'failed' && !item.status);

            return matchKeyword && matchStatus;
        })
    }, [data, keywordDebounce, statusFilter])

    const {run: onDelete} = useRequest(api.deleteHistory, {
        manual: true,
        onSuccess: () => {
            refresh()
            message.success("删除成功")
        }
    })

    const columns: ColumnsType<HistoryItem> = [
        {
            title: '状态',
            dataIndex: 'status',
            width: 80,
            render: (value) => (
                value ? (
                    <Tag color={'success'} icon={<CheckCircleOutlined />}>成功</Tag>
                ) : (
                    <Tag color={'error'} icon={<CloseCircleOutlined />}>失败</Tag>
                )
            )
        },
        {
            title: '番号',
            dataIndex: 'num',
            width: 150,
            render: (value, record) => (
                <div>
                    <b style={{color: token.colorPrimary}}>{value}</b>
                    <div className="mt-1">
                        {record.is_zh && (<Tag color={'blue'}>中文</Tag>)}
                        {record.is_uncensored && (<Tag color={'green'}>无码</Tag>)}
                    </div>
                </div>
            )
        },
        {
            title: '路径',
            dataIndex: 'path',
            render: (_, record) => (
                <div style={{fontSize: 13, maxWidth: 500}}>
                    <div className="text-gray-500 truncate" title={record.source_path}>
                        {record.source_path}
                    </div>
                    <div style={{color: token.colorPrimary}}>↓</div>
                    <div className="truncate" title={record.dest_path}>
                        {record.dest_path}
                    </div>
                </div>
            )
        },
        {
            title: '转移方式',
            dataIndex: 'trans_method',
            width: 100,
            render: (value: string) => {
                const method = TransModeOptions.find((i: any) => i.value === value)
                return (
                    <Tag color={method?.color}>{method?.name || value}</Tag>
                )
            }
        },
        {
            title: '时间',
            dataIndex: 'create_time',
            width: 160,
            render: (value) => (
                <span style={{color: token.colorTextSecondary}}>
                    {dayjs(value).format('YYYY-MM-DD HH:mm')}
                </span>
            )
        },
        {
            title: '操作',
            dataIndex: 'operations',
            width: 60,
            fixed: 'right',
            render: (_, record) => (
                <More items={items} onClick={(key) => onMoreClick(key, record)}/>
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
            icon: <DeleteOutlined/>,
            danger: true
        },
    ] as any

    function onMoreClick(key: string, record: HistoryItem) {
        if (key === 'edit') {
            setSelected(record)
        } else if (key === 'delete') {
            Modal.confirm({
                title: '确认删除',
                content: `是否确认删除 ${record.num} 的整理记录？`,
                okText: '删除',
                okType: 'danger',
                onOk: () => {
                    onDelete(record.id)
                }
            })
        }
    }

    return (
        <>
            {/* 统计面板 */}
            <Row gutter={[16, 16]} className="mb-4">
                <Col xs={12} sm={6}>
                    <Card size="small" hoverable>
                        <Statistic
                            title="总记录数"
                            value={statistics.total}
                            prefix={<HistoryOutlined style={{color: token.colorPrimary}} />}
                        />
                    </Card>
                </Col>
                <Col xs={12} sm={6}>
                    <Card size="small" hoverable>
                        <Statistic
                            title="成功"
                            value={statistics.success}
                            valueStyle={{color: token.colorSuccess}}
                            prefix={<CheckCircleOutlined />}
                        />
                    </Card>
                </Col>
                <Col xs={12} sm={6}>
                    <Card size="small" hoverable>
                        <Statistic
                            title="失败"
                            value={statistics.failed}
                            valueStyle={{color: token.colorError}}
                            prefix={<CloseCircleOutlined />}
                        />
                    </Card>
                </Col>
                <Col xs={12} sm={6}>
                    <Card size="small" hoverable>
                        <Statistic
                            title="今日整理"
                            value={statistics.today}
                            valueStyle={{color: token.colorInfo}}
                            prefix={<FileTextOutlined />}
                        />
                    </Card>
                </Col>
            </Row>

            {/* 主内容 */}
            <Card
                title={
                    <span>
                        <HistoryOutlined className="mr-2" />
                        历史记录
                    </span>
                }
                extra={(
                    <div className="flex gap-2 items-center">
                        <Select
                            value={statusFilter}
                            onChange={setStatusFilter}
                            style={{width: 100}}
                            options={[
                                {value: 'all', label: '全部'},
                                {value: 'success', label: '成功'},
                                {value: 'failed', label: '失败'},
                            ]}
                        />
                        <Input.Search
                            value={keyword}
                            onChange={e => setKeyword(e.target.value)}
                            placeholder="搜索番号或路径"
                            allowClear
                            style={{width: 200}}
                        />
                    </div>
                )}
            >
                <Table
                    rowKey={'id'}
                    scroll={{x: 'max-content'}}
                    columns={columns}
                    loading={loading}
                    dataSource={filteredData}
                    pagination={{
                        showSizeChanger: true,
                        showQuickJumper: true,
                        showTotal: (total) => `共 ${total} 条记录`
                    }}
                />
            </Card>

            <VideoDetail
                title={'重新整理'}
                mode={'history'}
                transMode={selected?.status ? 'move' : selected?.trans_method}
                width={1100}
                path={selected?.status ? selected?.dest_path : selected?.source_path}
                open={!!selected}
                onCancel={() => setSelected(undefined)}
                onOk={() => {
                    setSelected(undefined)
                    refresh()
                }}
            />
        </>
    )
}
