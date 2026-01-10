import {Button, Card, message, Table, Tag} from "antd";
import {ColumnsType} from "antd/lib/table";
import dayjs from "dayjs";
import * as api from "../../../apis/schedule";
import {useRequest} from "ahooks";
import React from "react";
import {createFileRoute} from "@tanstack/react-router";
import {PlayCircleOutlined} from "@ant-design/icons";
import { useThemeColors } from '../../../hooks/useThemeColors';
import './style.css';

export const Route = createFileRoute('/_index/schedule/')({
    component: Schedule,
})

function Schedule() {
    const colors = useThemeColors()

    const {data = [], loading, refresh} = useRequest(api.getSchedules, {})
    const {run: onFire, loading: onFiring} = useRequest(api.fireSchedule, {
        manual: true,
        onSuccess: () => {
            message.success('手动执行成功')
            refresh()
        }
    })

    const columns: ColumnsType<any> = [
        {
            title: '任务名称',
            dataIndex: 'name',
            render: (value) => (
                <span style={{ color: colors.textPrimary, fontWeight: 500 }}>{value}</span>
            )
        },
        {
            title: '状态',
            dataIndex: 'status',
            render: (value) => (
                value ? (
                    <Tag
                        style={{
                            background: colors.rgba('gold', 0.1),
                            border: `1px solid ${colors.borderGold}`,
                            color: colors.textGold,
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 6
                        }}
                    >
                        <span className="status-dot running"></span>
                        运行中
                    </Tag>
                ) : (
                    <Tag
                        style={{
                            background: colors.rgba('white', 0.1),
                            border: `1px solid ${colors.borderSecondary}`,
                            color: colors.textSecondary,
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 6
                        }}
                    >
                        <span className="status-dot waiting"></span>
                        等待
                    </Tag>
                )
            )
        },
        {
            title: '下次执行时间',
            dataIndex: 'next_run_time',
            render: (value) => (
                <span style={{ color: colors.textSecondary, fontSize: 13 }}>
                    {dayjs(value).format('lll')}
                </span>
            )
        },
        {
            title: '操作',
            dataIndex: 'operations',
            render: (_, record: any) => (
                <Button
                    type={'primary'}
                    onClick={() => onFire(record.key)}
                    loading={onFiring}
                    icon={<PlayCircleOutlined />}
                    style={{
                        background: colors.goldGradient,
                        border: 'none',
                        boxShadow: colors.shadowGold,
                        transition: 'all 0.3s'
                    }}
                    className="execute-btn"
                >
                    手动执行
                </Button>
            )
        }
    ]

    return (
        <div className="schedule-page-wrapper animate-fade-in">
            <Card
                title={<span style={{ color: colors.textPrimary, fontSize: 18, fontWeight: 500 }}>任务调度</span>}
                className="dark-card"
                style={{
                    background: colors.bgElevated,
                    border: `1px solid ${colors.borderPrimary}`,
                    borderRadius: 8
                }}
            >
                <Table 
                    rowKey={'key'} 
                    columns={columns} 
                    dataSource={data} 
                    loading={loading} 
                    pagination={false}
                    className="dark-table"
                    rowClassName="dark-table-row"
                />
            </Card>
        </div>
    )
}

