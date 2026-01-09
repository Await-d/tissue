import {Button, Card, Col, Empty, Input, message, Modal, Row, Space, Statistic, Table, Tag, Tooltip, theme} from "antd";
import {ColumnsType} from "antd/lib/table";
import dayjs from "dayjs";
import * as api from "../../../apis/schedule";
import {useDebounce, useRequest} from "ahooks";
import React, {useMemo, useState} from "react";
import {createFileRoute} from "@tanstack/react-router";
import {
    ClockCircleOutlined,
    PlayCircleOutlined,
    CheckCircleOutlined,
    PauseCircleOutlined,
    ThunderboltOutlined,
    SearchOutlined
} from "@ant-design/icons";

const {useToken} = theme;

export const Route = createFileRoute('/_index/schedule/')({
    component: Schedule,
})

interface ScheduleItem {
    key: string;
    name: string;
    status: boolean;
    next_run_time: string;
}

function Schedule() {
    const {token} = useToken();
    const [keyword, setKeyword] = useState<string>('');
    const keywordDebounce = useDebounce(keyword, {wait: 300});

    const {data = [], loading, refresh} = useRequest(api.getSchedules, {});

    const {run: onFire, loading: onFiring} = useRequest(api.fireSchedule, {
        manual: true,
        onSuccess: () => {
            message.success('手动执行成功');
            refresh();
        }
    });

    // 过滤数据
    const filteredData = useMemo(() => {
        if (!keywordDebounce) return data;
        return data.filter((item: ScheduleItem) =>
            item.name.toLowerCase().includes(keywordDebounce.toLowerCase())
        );
    }, [data, keywordDebounce]);

    // 统计数据
    const statistics = useMemo(() => {
        const total = data.length;
        const running = data.filter((item: ScheduleItem) => !item.status).length;
        const waiting = total - running;
        const nextRun = data.length > 0
            ? data.reduce((earliest: ScheduleItem, current: ScheduleItem) => {
                return dayjs(current.next_run_time).isBefore(dayjs(earliest.next_run_time))
                    ? current
                    : earliest;
            })
            : null;

        return {
            total,
            running,
            waiting,
            nextRun: nextRun ? dayjs(nextRun.next_run_time).format('MM-DD HH:mm') : '-'
        };
    }, [data]);

    // 立即执行
    const handleFire = (record: ScheduleItem) => {
        Modal.confirm({
            title: '确认立即执行',
            content: `是否立即执行任务 "${record.name}"？`,
            icon: <ThunderboltOutlined style={{color: token.colorWarning}} />,
            onOk: () => onFire(record.key)
        });
    };

    const columns: ColumnsType<ScheduleItem> = [
        {
            title: '任务名称',
            dataIndex: 'name',
            key: 'name',
            render: (text: string) => (
                <span style={{fontWeight: 500}}>{text}</span>
            )
        },
        {
            title: '状态',
            dataIndex: 'status',
            key: 'status',
            width: 120,
            align: 'center',
            render: (value: boolean) => (
                value ? (
                    <Tag icon={<PauseCircleOutlined />} color="warning">等待中</Tag>
                ) : (
                    <Tag icon={<CheckCircleOutlined />} color="success">运行中</Tag>
                )
            )
        },
        {
            title: '下次执行时间',
            dataIndex: 'next_run_time',
            key: 'next_run_time',
            width: 180,
            render: (value: string) => (
                <Tooltip title={dayjs(value).format('YYYY-MM-DD HH:mm:ss')}>
                    <span style={{color: token.colorTextSecondary}}>
                        <ClockCircleOutlined className="mr-1" />
                        {dayjs(value).format('MM-DD HH:mm')}
                    </span>
                </Tooltip>
            )
        },
        {
            title: '操作',
            key: 'operations',
            width: 120,
            align: 'center',
            render: (_: any, record: ScheduleItem) => (
                <Tooltip title="立即执行">
                    <Button
                        type="primary"
                        icon={<PlayCircleOutlined />}
                        onClick={() => handleFire(record)}
                        loading={onFiring}
                        size="small"
                    >
                        执行
                    </Button>
                </Tooltip>
            )
        }
    ];

    return (
        <Space direction="vertical" size="middle" style={{width: '100%'}}>
            {/* 统计面板 */}
            <Row gutter={[16, 16]}>
                <Col xs={12} sm={6}>
                    <Card size="small" hoverable>
                        <Statistic
                            title="总任务数"
                            value={statistics.total}
                            prefix={<ClockCircleOutlined style={{color: token.colorPrimary}} />}
                        />
                    </Card>
                </Col>
                <Col xs={12} sm={6}>
                    <Card size="small" hoverable>
                        <Statistic
                            title="运行中"
                            value={statistics.running}
                            valueStyle={{color: token.colorSuccess}}
                            prefix={<CheckCircleOutlined />}
                        />
                    </Card>
                </Col>
                <Col xs={12} sm={6}>
                    <Card size="small" hoverable>
                        <Statistic
                            title="等待中"
                            value={statistics.waiting}
                            valueStyle={{color: token.colorWarning}}
                            prefix={<PauseCircleOutlined />}
                        />
                    </Card>
                </Col>
                <Col xs={12} sm={6}>
                    <Card size="small" hoverable>
                        <Statistic
                            title="最近执行"
                            value={statistics.nextRun}
                            valueStyle={{fontSize: 16}}
                            prefix={<ThunderboltOutlined style={{color: token.colorInfo}} />}
                        />
                    </Card>
                </Col>
            </Row>

            {/* 任务列表 */}
            <Card
                title={
                    <Space>
                        <ClockCircleOutlined />
                        <span>任务调度</span>
                        <Tag color="blue">{filteredData.length} 个任务</Tag>
                    </Space>
                }
                extra={
                    <Input
                        placeholder="搜索任务名称..."
                        prefix={<SearchOutlined style={{color: token.colorTextSecondary}} />}
                        value={keyword}
                        onChange={e => setKeyword(e.target.value)}
                        allowClear
                        style={{width: 200}}
                    />
                }
            >
                {filteredData.length > 0 ? (
                    <Table
                        rowKey="key"
                        columns={columns}
                        dataSource={filteredData}
                        loading={loading}
                        pagination={false}
                        rowClassName={(record) =>
                            record.status ? 'schedule-row-waiting' : 'schedule-row-running'
                        }
                    />
                ) : (
                    <Empty description={keyword ? '未找到匹配的任务' : '暂无任务'} />
                )}
            </Card>

            <style>{`
                .schedule-row-running {
                    background-color: ${token.colorSuccessBg};
                }
                .schedule-row-waiting {
                    background-color: ${token.colorWarningBg};
                }
                .schedule-row-running:hover td,
                .schedule-row-waiting:hover td {
                    background-color: ${token.colorBgTextHover} !important;
                }
            `}</style>
        </Space>
    );
}
