import {createFileRoute} from "@tanstack/react-router";
import {Badge, Card, Col, Empty, FloatButton, Input, List, message, Row, Skeleton, Space, Statistic, Tag, theme, Tooltip} from "antd";
import ModifyModal from "./-components/modifyModal.tsx";
import {useFormModal} from "../../../utils/useFormModal.ts";
import * as api from "../../../apis/site.ts";
import {useDebounce, useRequest} from "ahooks";
import {createPortal} from "react-dom";
import {
    RedoOutlined,
    SearchOutlined,
    GlobalOutlined,
    CheckCircleOutlined,
    CloseCircleOutlined,
    CloudServerOutlined
} from "@ant-design/icons";
import React, {useMemo, useState} from "react";


export const Route = createFileRoute('/_index/site/')({
    component: Site
})

interface SiteItem {
    id: number;
    name: string;
    status: boolean;
    priority: number;
    alternate_host?: string;
    downloadable?: boolean;
}

function Site() {
    const {token} = theme.useToken()
    const [keyword, setKeyword] = useState<string>('')
    const keywordDebounce = useDebounce(keyword, {wait: 300})

    const {data = [], refresh, loading} = useRequest(api.getSites, {})

    const {modalProps, setOpen} = useFormModal({
        service: api.modifySite,
        onOk: () => {
            setOpen(false)
            refresh()
        }
    })

    const {run: onTesting, loading: testingLoading} = useRequest(api.testingSits, {
        manual: true,
        onSuccess: () => {
            message.success("站点刷新提交成功")
        }
    })

    // 过滤数据
    const filteredData = useMemo(() => {
        if (!keywordDebounce) return data;
        return data.filter((item: SiteItem) =>
            item.name?.toLowerCase().includes(keywordDebounce.toLowerCase()) ||
            item.alternate_host?.toLowerCase().includes(keywordDebounce.toLowerCase())
        );
    }, [data, keywordDebounce])

    // 统计数据
    const statistics = useMemo(() => {
        const total = data.length;
        const enabled = data.filter((item: SiteItem) => item.status).length;
        const disabled = total - enabled;
        const downloadable = data.filter((item: SiteItem) => item.downloadable).length;
        return {total, enabled, disabled, downloadable};
    }, [data])

    function renderItem(item: SiteItem) {
        return (
            <List.Item>
                <Badge.Ribbon text={item.status ? '启用' : '停用'}
                              color={item.status ? token.colorPrimary : token.colorTextDisabled}>
                    <Card size={'default'}
                          hoverable
                          title={(
                              <div className={'flex items-center'}>
                                  <Tag bordered={false} color="blue">{item.priority}</Tag>
                                  <Tooltip title={item.name}>
                                      <div className="truncate max-w-[150px]">{item.name}</div>
                                  </Tooltip>
                              </div>
                          )}
                          className={'cursor-pointer transition-all duration-300'}
                          style={{
                              borderColor: item.status ? token.colorPrimary : token.colorBorder,
                              opacity: item.status ? 1 : 0.7
                          }}
                          onClick={() => setOpen(true, item)}
                    >
                        <Space direction={"vertical"} size={'middle'} className="w-full">
                            <div style={{color: token.colorTextSecondary}} className="truncate">
                                <GlobalOutlined className="mr-2" />
                                <span>{item.alternate_host || '未设置替代域名'}</span>
                            </div>
                            <div>
                                <Tag color={'blue'} bordered={false}>元数据</Tag>
                                {item.downloadable && <Tag color={'green'} bordered={false}>下载</Tag>}
                            </div>
                        </Space>
                    </Card>
                </Badge.Ribbon>
            </List.Item>
        )
    }

    if (loading) {
        return (
            <Card>
                <Skeleton active/>
            </Card>
        )
    }

    return (
        <>
            {/* 统计面板 */}
            <Row gutter={[16, 16]} className="mb-4">
                <Col xs={12} sm={6}>
                    <Card size="small" hoverable>
                        <Statistic
                            title="总站点数"
                            value={statistics.total}
                            prefix={<CloudServerOutlined style={{color: token.colorPrimary}} />}
                        />
                    </Card>
                </Col>
                <Col xs={12} sm={6}>
                    <Card size="small" hoverable>
                        <Statistic
                            title="已启用"
                            value={statistics.enabled}
                            valueStyle={{color: token.colorSuccess}}
                            prefix={<CheckCircleOutlined />}
                        />
                    </Card>
                </Col>
                <Col xs={12} sm={6}>
                    <Card size="small" hoverable>
                        <Statistic
                            title="已停用"
                            value={statistics.disabled}
                            valueStyle={{color: token.colorTextDisabled}}
                            prefix={<CloseCircleOutlined />}
                        />
                    </Card>
                </Col>
                <Col xs={12} sm={6}>
                    <Card size="small" hoverable>
                        <Statistic
                            title="支持下载"
                            value={statistics.downloadable}
                            valueStyle={{color: token.colorInfo}}
                            prefix={<GlobalOutlined />}
                        />
                    </Card>
                </Col>
            </Row>

            {/* 搜索栏 */}
            <Card size="small" className="mb-4">
                <Input
                    placeholder="搜索站点名称或域名..."
                    prefix={<SearchOutlined style={{color: token.colorTextSecondary}} />}
                    value={keyword}
                    onChange={e => setKeyword(e.target.value)}
                    allowClear
                    style={{maxWidth: 400}}
                />
            </Card>

            {/* 站点列表 */}
            {(filteredData && filteredData.length > 0) ? (
                <List grid={{gutter: 16, xxl: 4, xl: 4, lg: 3, md: 2, xs: 1}}
                      dataSource={filteredData}
                      renderItem={renderItem}/>
            ) : (
                <Card title={'站点'}>
                    <Empty description={(
                        <div>
                            <div>{keyword ? '未找到匹配的站点' : '无可用站点'}</div>
                            {!keyword && (
                                <div>请检查网络连接后 <a onClick={() => onTesting()}>刷新站点</a></div>
                            )}
                        </div>
                    )}/>
                </Card>
            )}
            <ModifyModal {...modalProps} />
            {createPortal((
                    <>
                        <FloatButton
                            icon={<RedoOutlined spin={testingLoading} />}
                            onClick={() => onTesting()}
                            tooltip="刷新站点"
                        />
                    </>
                ), document.getElementsByClassName('index-float-button-group')[0]
            )}
        </>
    )
}
