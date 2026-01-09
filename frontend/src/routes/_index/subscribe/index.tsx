import {
    Card,
    Col,
    Empty,
    FloatButton,
    Input,
    message,
    Row,
    Skeleton,
    Space,
    Tag,
    Tooltip,
    Button,
    Badge,
    Progress
} from "antd";
import React, {useState, useMemo} from "react";
import * as api from "../../../apis/subscribe";
import {useRequest} from "ahooks";
import ModifyModal from "./-components/modifyModal.tsx";
import {createPortal} from "react-dom";
import {
    HistoryOutlined,
    PlusOutlined,
    SearchOutlined,
    EditOutlined,
    DeleteOutlined
} from "@ant-design/icons";
import VideoCover from "../../../components/VideoCover";
import {useFormModal} from "../../../utils/useFormModal.ts";
import {createFileRoute, useNavigate} from "@tanstack/react-router";
import HistoryModal from "./-components/historyModal.tsx";

export const Route = createFileRoute('/_index/subscribe/')({
    component: Subscribe
})

interface SubscribeItem {
    id: number;
    num: string;
    title: string;
    cover: string;
    premiered?: string;
    actors?: string;
    is_hd: boolean;
    is_zh: boolean;
    is_uncensored: boolean;
    include_keyword?: string;
    exclude_keyword?: string;
}

function Subscribe() {
    const navigate = useNavigate();

    const {data = [], loading, refresh} = useRequest(api.getSubscribes, {});
    const [searchText, setSearchText] = useState<string>('');
    const {setOpen, modalProps} = useFormModal({
        service: api.modifySubscribe,
        onOk: () => {
            setOpen(false);
            refresh();
        }
    });

    const [historyModalOpen, setHistoryModalOpen] = useState(false);

    const {run: onDelete} = useRequest(api.deleteSubscribe, {
        manual: true,
        onSuccess: () => {
            message.success("删除成功");
            setOpen(false);
            refresh();
        }
    });

    // Filter subscribes based on search text
    const filteredSubscribes = useMemo(() => {
        if (!searchText) return data;
        const searchLower = searchText.toLowerCase();
        return data.filter((item: SubscribeItem) => {
            return item.title?.toLowerCase().includes(searchLower) ||
                   item.num?.toLowerCase().includes(searchLower) ||
                   item.actors?.toLowerCase().includes(searchLower);
        });
    }, [data, searchText]);

    // Handle quick edit
    const handleQuickEdit = (e: React.MouseEvent, subscribe: SubscribeItem) => {
        e.stopPropagation();
        setOpen(true, subscribe);
    };

    // Handle quick delete
    const handleQuickDelete = (e: React.MouseEvent, id: number) => {
        e.stopPropagation();
        onDelete(id);
    };

    if (loading) {
        return (
            <Card>
                <Skeleton active/>
            </Card>
        );
    }

    return (
        <div>
            <Row style={{marginBottom: 15}}>
                <Col span={24} lg={{span: 6, offset: 18}}>
                    <Input.Search
                        allowClear
                        enterButton
                        placeholder="搜索订阅..."
                        value={searchText}
                        onChange={(e) => setSearchText(e.target.value)}
                        onSearch={setSearchText}
                    />
                </Col>
            </Row>

            <Row gutter={[15, 15]}>
                {filteredSubscribes.length > 0 ? (
                    filteredSubscribes.map((subscribe: SubscribeItem) => (
                        <Col key={subscribe.id} span={24} md={12} lg={6}>
                            <Badge.Ribbon
                                text={subscribe.is_uncensored ? "无码" : undefined}
                                color={subscribe.is_uncensored ? "green" : undefined}
                                style={{display: subscribe.is_uncensored ? 'block' : 'none'}}
                            >
                                <Card
                                    hoverable
                                    size="small"
                                    className="subscribe-card"
                                    cover={<VideoCover src={subscribe.cover}/>}
                                    onClick={() => setOpen(true, subscribe)}
                                >
                                    <Card.Meta
                                        title={(
                                            <div className="text-sm font-semibold truncate">
                                                {subscribe.title || subscribe.num}
                                            </div>
                                        )}
                                        description={(
                                            <div className="space-y-2">
                                                <div className="flex flex-wrap gap-1">
                                                    {subscribe.premiered && (
                                                        <Tag bordered={false} className="text-xs">
                                                            {subscribe.premiered}
                                                        </Tag>
                                                    )}
                                                    {subscribe.is_hd && (
                                                        <Tag color="red" bordered={false} className="text-xs">
                                                            高清
                                                        </Tag>
                                                    )}
                                                    {subscribe.is_zh && (
                                                        <Tag color="blue" bordered={false} className="text-xs">
                                                            中文
                                                        </Tag>
                                                    )}
                                                </div>

                                                {subscribe.actors && (
                                                    <div className="text-xs text-gray-500 truncate">
                                                        {subscribe.actors}
                                                    </div>
                                                )}

                                                <div className="card-actions flex justify-between items-center pt-2 border-t">
                                                    <Tooltip title="搜索">
                                                        <Button
                                                            type="text"
                                                            size="small"
                                                            icon={<SearchOutlined/>}
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                navigate({
                                                                    to: '/search',
                                                                    search: {num: subscribe.num}
                                                                });
                                                            }}
                                                        />
                                                    </Tooltip>
                                                    <Tooltip title="编辑">
                                                        <Button
                                                            type="text"
                                                            size="small"
                                                            icon={<EditOutlined/>}
                                                            onClick={(e) => handleQuickEdit(e, subscribe)}
                                                        />
                                                    </Tooltip>
                                                    <Tooltip title="删除">
                                                        <Button
                                                            type="text"
                                                            size="small"
                                                            danger
                                                            icon={<DeleteOutlined/>}
                                                            onClick={(e) => handleQuickDelete(e, subscribe.id)}
                                                        />
                                                    </Tooltip>
                                                </div>
                                            </div>
                                        )}
                                    />
                                </Card>
                            </Badge.Ribbon>
                        </Col>
                    ))
                ) : (
                    <Col span={24}>
                        <Card>
                            <Empty
                                description={searchText ? '没有找到匹配的订阅' : '暂无订阅'}
                            >
                                {!searchText && (
                                    <Button type="primary" icon={<PlusOutlined/>} onClick={() => setOpen(true)}>
                                        创建订阅
                                    </Button>
                                )}
                            </Empty>
                        </Card>
                    </Col>
                )}
            </Row>

            {/* Modals */}
            <ModifyModal width={1100} onDelete={onDelete} {...modalProps} />
            <HistoryModal
                open={historyModalOpen}
                onCancel={() => setHistoryModalOpen(false)}
                onResubscribe={() => {
                    refresh();
                    setHistoryModalOpen(false);
                }}
            />

            {/* Float Buttons */}
            <>
                {createPortal(
                    <>
                        <FloatButton icon={<PlusOutlined/>} type="primary" onClick={() => setOpen(true)}/>
                        <FloatButton icon={<HistoryOutlined/>} onClick={() => setHistoryModalOpen(true)}/>
                    </>,
                    document.getElementsByClassName('index-float-button-group')[0]
                )}
            </>

            <style>{`
                .subscribe-card {
                    transition: all 0.3s ease;
                }
                .subscribe-card:hover {
                    transform: translateY(-4px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                }
                .subscribe-card .card-actions {
                    opacity: 0.7;
                    transition: opacity 0.3s ease;
                }
                .subscribe-card:hover .card-actions {
                    opacity: 1;
                }
            `}</style>
        </div>
    );
}
