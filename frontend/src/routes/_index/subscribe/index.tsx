import { Badge, Button, Card, Col, Empty, FloatButton, Input, App, Row, Skeleton, Space, Tag, Tooltip } from "antd";
import React, { useState, useEffect } from "react";
import * as api from "../../../apis/subscribe";
import { useRequest } from "ahooks";
import ModifyModal from "./-components/modifyModal.tsx";
import { createPortal } from "react-dom";
import { HistoryOutlined, PlusOutlined, SearchOutlined } from "@ant-design/icons";
import VideoCover from "../../../components/VideoCover";
import { useFormModal } from "../../../utils/useFormModal.ts";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import HistoryModal from "./-components/historyModal.tsx";
import { useDownloadStatus } from "../../../hooks/useDownloadStatus";
import './styles.css';

export const Route = createFileRoute('/_index/subscribe/')({
    component: Subscribe
})

function Subscribe() {
    const { message } = App.useApp();
    const navigate = useNavigate()

    const { data = [], loading, refresh } = useRequest(api.getSubscribes, {})
    const [filter, setFilter] = useState<string>()
    const [searchValue, setSearchValue] = useState<string>('')
    const { setOpen, modalProps, form } = useFormModal({
        service: api.modifySubscribe,
        onOk: () => {
            setOpen(false)
            refresh()
        }
    })

    const [historyModalOpen, setHistoryModalOpen] = useState(false)

    const { run: onDelete } = useRequest(api.deleteSubscribe, {
        manual: true,
        onSuccess: () => {
            message.success("删除成功")
            setOpen(false)
            refresh()
        }
    })

    if (loading) {
        return (
            <Card className="subscribe-loading-card">
                <Skeleton active />
            </Card>
        )
    }

    const subscribes = data.filter((item: any) => {
        if (!filter) return true
        return item.title.toUpperCase().includes(filter.toUpperCase()) || item.num.toUpperCase().includes(filter.toUpperCase())
    })

    // 获取下载状态
    const { statusMap, error: downloadStatusError } = useDownloadStatus(subscribes);

    // 监听下载状态检测错误
    useEffect(() => {
        if (downloadStatusError) {
            message.warning(`下载状态检测失败: ${downloadStatusError.message}`);
        }
    }, [downloadStatusError, message]);

    return (
        <div className="subscribe-container">
            <Row>
                <Col span={24} lg={{
                    span: 6,
                    offset: 18,
                }}>
                    <Space.Compact className="subscribe-search-bar">
                        <Input
                            allowClear
                            value={searchValue}
                            onChange={e => setSearchValue(e.target.value)}
                            onPressEnter={() => setFilter(searchValue)}
                            placeholder="搜索番号或标题"
                        />
                        <Button
                            icon={<SearchOutlined />}
                            onClick={() => setFilter(searchValue)}
                            className="subscribe-search-btn"
                        />
                    </Space.Compact>
                </Col>
            </Row>
            <Row gutter={[15, 15]}>
                {subscribes.length > 0 ? (
                    subscribes.map((subscribe: any) => {
                        const isDownloaded = statusMap[subscribe.num] || false;

                        const cardContent = (
                            <Card
                                hoverable
                                size={"small"}
                                className="subscribe-card"
                                cover={(<VideoCover src={subscribe.cover} />)}
                                onClick={() => setOpen(true, subscribe)}
                            >
                                <Card.Meta
                                    title={
                                        <div className="subscribe-card-title">
                                            {subscribe.title || subscribe.num}
                                        </div>
                                    }
                                    description={(
                                        <div className={'flex'}>
                                            <Space size={[0, 'small']} wrap className={'flex-1'}>
                                                {subscribe.premiered && (
                                                    <Tag className="subscribe-tag subscribe-tag-date">{subscribe.premiered}</Tag>
                                                )}
                                                {subscribe.is_hd && (
                                                    <Tag className="subscribe-tag subscribe-tag-hd">高清</Tag>)}
                                                {subscribe.is_zh && (
                                                    <Tag className="subscribe-tag subscribe-tag-zh">中文</Tag>)}
                                                {subscribe.is_uncensored && (
                                                    <Tag className="subscribe-tag subscribe-tag-uncensored">无码</Tag>)}
                                            </Space>
                                            <Tooltip title={'搜索'}>
                                                <div className="subscribe-search-icon" onClick={(e) => {
                                                    e.stopPropagation();
                                                    return navigate({ to: '/search', search: { num: subscribe.num } })
                                                }}>
                                                    <SearchOutlined />
                                                </div>
                                            </Tooltip>
                                        </div>
                                    )}
                                />
                            </Card>
                        );

                        return (
                            <Col key={subscribe.id} span={24} md={12} lg={6}>
                                {isDownloaded ? (
                                    <Badge.Ribbon
                                        text="已下载"
                                        color="green"
                                    >
                                        {cardContent}
                                    </Badge.Ribbon>
                                ) : (
                                    cardContent
                                )}
                            </Col>
                        );
                    })
                ) : (
                    <Col span={24}>
                        <Card className="subscribe-empty-card">
                            <Empty
                                description={'无订阅'}
                                className="subscribe-empty"
                            />
                        </Card>
                    </Col>
                )}
            </Row>
            <ModifyModal width={1100}
                onDelete={onDelete}
                {...modalProps} />
            <HistoryModal open={historyModalOpen}
                          onCancel={() => setHistoryModalOpen(false)}
                          onResubscribe={() => {
                              refresh()
                              setHistoryModalOpen(false)
                          }}
            />
            <>
                {createPortal((
                    <>
                        <FloatButton
                            icon={<PlusOutlined />}
                            type={'primary'}
                            onClick={() => setOpen(true)}
                            className="subscribe-float-btn"
                        />
                        <FloatButton
                            icon={<HistoryOutlined />}
                            onClick={() => setHistoryModalOpen(true)}
                            className="subscribe-float-btn"
                        />
                    </>),
                    document.getElementsByClassName('index-float-button-group')[0]
                )}
            </>
        </div>
    )
}
