import {
    Button,
    Checkbox,
    Col,
    Divider,
    Form,
    Input,
    message,
    Modal,
    ModalProps,
    Row,
    Select,
    Spin,
    Tag,
    Space,
    Tooltip,
    Card,
    Typography,
    Alert,
} from "antd";
import {
    SaveOutlined,
    DeleteOutlined,
    ReloadOutlined,
    ClockCircleOutlined,
    StarOutlined,
    TeamOutlined,
    TagsOutlined,
    VideoCameraOutlined,
    CalendarOutlined,
    FieldTimeOutlined,
    GlobalOutlined,
    CheckCircleOutlined,
    DownloadOutlined,
} from "@ant-design/icons";
import * as api from "../../apis/video.ts";
import React, {useEffect, useState} from "react";
import {useRequest} from "ahooks";
import {useNavigate} from "@tanstack/react-router";
import Styles from "./index.module.css";
import Websites from "../Websites";
import VideoActors from "../VideoActors";
import VideoCoverEditor from "../VideoCover/editor.tsx";
import FavoriteButton from "../FavoriteButton";

const {Text, Title} = Typography;

interface Props extends ModalProps {
    path?: string;
    mode?: string;
    transMode?: string;
}

function VideoDetail(props: Props) {
    const {path, mode, transMode, onOk, ...otherProps} = props;
    const [form] = Form.useForm();
    const [hasError, setHasError] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");
    const navigate = useNavigate();
    const [videoNum, setVideoNum] = useState<string>("");

    const {run: onLoad, loading} = useRequest(loadVideoDetail, {
        manual: true,
        onSuccess: (response) => {
            form.setFieldsValue(response);
            setVideoNum(response.num || "");
            setHasError(false);
            setErrorMessage("");
        },
        onError: (error) => {
            setHasError(true);
            setErrorMessage(error.message || "加载视频详情失败");
        },
    });

    const {run: onScrape, loading: onScraping} = useRequest(api.scrapeVideo, {
        manual: true,
        onSuccess: (response) => {
            delete response.data.data.is_zh;
            delete response.data.data.is_uncensored;
            form.setFieldsValue(response.data.data);
            message.success("刮削成功");
            setHasError(false);
        },
        onError: (error) => {
            message.error(error.message || "刮削失败");
        },
    });

    const {run: onSave, loading: onSaving} = useRequest(api.saveVideo, {
        manual: true,
        onSuccess: (response) => {
            message.success("保存成功");
            onOk?.(response.request.data);
        },
        onError: (error) => {
            message.error(error.message || "保存失败");
        },
    });

    const {run: onDelete, loading: onDeleting} = useRequest(api.deleteVideo, {
        manual: true,
        onSuccess: (response) => {
            message.success("删除成功");
            onOk?.(response.request.data);
        },
        onError: (error) => {
            message.error(error.message || "删除失败");
        },
    });

    async function loadVideoDetail(path: string) {
        let response = await api.getVideoDetail(path);
        if (!response.num) {
            response = await api.parseVideoNum(path);
        }
        return response;
    }

    function handleScrape() {
        const num = form.getFieldValue("num");
        if (!num) {
            return message.error("请输入番号");
        } else {
            return onScrape(num);
        }
    }

    function handleSave(value: any) {
        value.path = path;
        return onSave(value, mode, transMode);
    }

    function handleDelete() {
        Modal.confirm({
            title: "确认删除",
            content: "删除后将无法恢复，是否确认删除该视频？",
            okText: "确认删除",
            cancelText: "取消",
            okButtonProps: {danger: true},
            onOk: () => {
                onDelete(path);
            },
        });
    }

    function handleQuickSave() {
        form.submit();
    }

    useEffect(() => {
        if (otherProps.open && path) {
            onLoad(path);
        } else {
            form.resetFields();
            setHasError(false);
            setErrorMessage("");
        }
    }, [otherProps.open]);

    const renderFooter = () => {
        const buttons = [];

        // Add favorite and download buttons
        if (videoNum) {
            buttons.push(
                <FavoriteButton
                    key="favorite"
                    videoNum={videoNum}
                    videoTitle={form.getFieldValue("title")}
                    videoCover={form.getFieldValue("cover")}
                />
            );
            buttons.push(
                <Tooltip key="download-tooltip" title="搜索下载资源">
                    <Button
                        key="download"
                        icon={<DownloadOutlined />}
                        onClick={() => {
                            navigate({
                                to: "/search",
                                search: { num: videoNum }
                            });
                        }}
                    >
                        下载
                    </Button>
                </Tooltip>
            );
            buttons.push(<Divider key="divider-actions" type="vertical" />);
        }

        if (mode === "video") {
            buttons.push(
                <Tooltip key="delete-tooltip" title="删除视频">
                    <Button
                        key="delete"
                        icon={<DeleteOutlined />}
                        onClick={handleDelete}
                        danger
                        loading={onDeleting}
                    >
                        删除
                    </Button>
                </Tooltip>
            );
            buttons.push(<Divider key="divider" type="vertical" />);
        }

        buttons.push(
            <Tooltip key="scrape-tooltip" title="从网站刮削视频信息">
                <Button
                    key="scrape"
                    icon={<ReloadOutlined />}
                    onClick={handleScrape}
                    loading={onScraping}
                >
                    刮削
                </Button>
            </Tooltip>
        );

        buttons.push(
            <Tooltip key="save-tooltip" title="保存视频信息">
                <Button
                    key="save"
                    type="primary"
                    icon={<SaveOutlined />}
                    loading={onSaving}
                    onClick={handleQuickSave}
                >
                    保存
                </Button>
            </Tooltip>
        );

        return buttons;
    };

    return (
        <Modal
            {...otherProps}
            width={1200}
            className={Styles.videoDetailModal}
            footer={renderFooter()}
            destroyOnClose
        >
            {loading ? (
                <div className={Styles.loadingContainer}>
                    <Spin size="large" tip="加载中..." />
                </div>
            ) : hasError ? (
                <Alert
                    message="加载失败"
                    description={errorMessage}
                    type="error"
                    showIcon
                    action={
                        <Button size="small" onClick={() => path && onLoad(path)}>
                            重试
                        </Button>
                    }
                />
            ) : (
                <Form
                    className={Styles.form}
                    form={form}
                    layout="vertical"
                    onFinish={handleSave}
                >
                    <Row gutter={[24, 0]}>
                        {/* Left Column - Cover and Actors */}
                        <Col span={24} md={10} lg={9}>
                            <div className={Styles.leftColumn}>
                                <Card
                                    className={Styles.coverCard}
                                    bordered={false}
                                    bodyStyle={{padding: 0}}
                                >
                                    <Form.Item noStyle name="cover">
                                        <VideoCoverEditor />
                                    </Form.Item>
                                </Card>

                                <Card
                                    className={Styles.infoCard}
                                    title={
                                        <Space>
                                            <TeamOutlined />
                                            <span>演员信息</span>
                                        </Space>
                                    }
                                    bordered={false}
                                >
                                    <Form.Item name="actors" noStyle>
                                        <VideoActors />
                                    </Form.Item>
                                </Card>

                                <Card
                                    className={Styles.infoCard}
                                    title={
                                        <Space>
                                            <GlobalOutlined />
                                            <span>来源网站</span>
                                        </Space>
                                    }
                                    bordered={false}
                                >
                                    <Form.Item name="website" noStyle>
                                        <Websites />
                                    </Form.Item>
                                </Card>
                            </div>
                        </Col>

                        {/* Right Column - Details */}
                        <Col span={24} md={14} lg={15}>
                            <div className={Styles.rightColumn}>
                                {/* Basic Info Section */}
                                <Card
                                    className={Styles.sectionCard}
                                    title={
                                        <Space>
                                            <VideoCameraOutlined />
                                            <span>基本信息</span>
                                        </Space>
                                    }
                                    bordered={false}
                                >
                                    <Row gutter={[16, 16]}>
                                        <Col span={24} sm={12} md={8}>
                                            <Form.Item
                                                name="num"
                                                label={
                                                    <Space>
                                                        <TagsOutlined />
                                                        <span>番号</span>
                                                    </Space>
                                                }
                                                rules={[
                                                    {required: true, message: "请输入番号"},
                                                ]}
                                            >
                                                <Input placeholder="请输入番号" />
                                            </Form.Item>
                                        </Col>
                                        <Col span={24} sm={12} md={8}>
                                            <Form.Item
                                                name="premiered"
                                                label={
                                                    <Space>
                                                        <CalendarOutlined />
                                                        <span>发行时间</span>
                                                    </Space>
                                                }
                                            >
                                                <Input placeholder="YYYY-MM-DD" />
                                            </Form.Item>
                                        </Col>
                                        <Col span={24} sm={12} md={8}>
                                            <Form.Item
                                                name="rating"
                                                label={
                                                    <Space>
                                                        <StarOutlined />
                                                        <span>评分</span>
                                                    </Space>
                                                }
                                            >
                                                <Input placeholder="0-10" />
                                            </Form.Item>
                                        </Col>
                                        <Col span={24}>
                                            <Form.Item name="title" label="标题">
                                                <Input placeholder="请输入视频标题" />
                                            </Form.Item>
                                        </Col>
                                        <Col span={24}>
                                            <Form.Item name="outline" label="大纲">
                                                <Input.TextArea
                                                    rows={4}
                                                    placeholder="请输入视频简介"
                                                />
                                            </Form.Item>
                                        </Col>
                                    </Row>
                                </Card>

                                {/* Production Info Section */}
                                <Card
                                    className={Styles.sectionCard}
                                    title="制作信息"
                                    bordered={false}
                                >
                                    <Row gutter={[16, 16]}>
                                        <Col span={24} sm={12} md={8}>
                                            <Form.Item name="studio" label="制造商">
                                                <Input placeholder="制造商" />
                                            </Form.Item>
                                        </Col>
                                        <Col span={24} sm={12} md={8}>
                                            <Form.Item name="publisher" label="发行商">
                                                <Input placeholder="发行商" />
                                            </Form.Item>
                                        </Col>
                                        <Col span={24} sm={12} md={8}>
                                            <Form.Item name="director" label="导演">
                                                <Input placeholder="导演" />
                                            </Form.Item>
                                        </Col>
                                        <Col span={24} sm={12}>
                                            <Form.Item name="series" label="系列">
                                                <Input
                                                    placeholder="系列名称"
                                                    suffix={
                                                        form.getFieldValue('series') && (
                                                            <Tooltip title="跳转到该系列">
                                                                <Button
                                                                    type="link"
                                                                    size="small"
                                                                    onClick={() => {
                                                                        const series = form.getFieldValue('series');
                                                                        if (series) {
                                                                            navigate({
                                                                                to: '/video',
                                                                                search: {series}
                                                                            });
                                                                        }
                                                                    }}
                                                                >
                                                                    查看
                                                                </Button>
                                                            </Tooltip>
                                                        )
                                                    }
                                                />
                                            </Form.Item>
                                        </Col>
                                        <Col span={24} sm={12}>
                                            <Form.Item
                                                name="runtime"
                                                label={
                                                    <Space>
                                                        <FieldTimeOutlined />
                                                        <span>时长(分钟)</span>
                                                    </Space>
                                                }
                                            >
                                                <Input
                                                    type="number"
                                                    placeholder="时长"
                                                    min={0}
                                                />
                                            </Form.Item>
                                        </Col>
                                    </Row>
                                </Card>

                                {/* Tags and Attributes Section */}
                                <Card
                                    className={Styles.sectionCard}
                                    title="标签与属性"
                                    bordered={false}
                                >
                                    <Row gutter={[16, 16]}>
                                        <Col span={24}>
                                            <Form.Item
                                                name="tags"
                                                label={
                                                    <Space>
                                                        <TagsOutlined />
                                                        <span>类别标签</span>
                                                    </Space>
                                                }
                                            >
                                                <Select
                                                    mode="tags"
                                                    placeholder="输入或选择标签"
                                                    tokenSeparators={[","]}
                                                    tagRender={(props) => {
                                                        const {label, closable, onClose} = props;
                                                        return (
                                                            <Tag
                                                                closable={closable}
                                                                onClose={onClose}
                                                                style={{cursor: 'pointer'}}
                                                                onClick={(e) => {
                                                                    e.preventDefault();
                                                                    navigate({
                                                                        to: '/video',
                                                                        search: {tag: label as string}
                                                                    });
                                                                }}
                                                            >
                                                                {label}
                                                            </Tag>
                                                        );
                                                    }}
                                                />
                                            </Form.Item>
                                        </Col>
                                        <Col span={12} sm={8}>
                                            <Form.Item
                                                name="is_zh"
                                                valuePropName="checked"
                                                initialValue={false}
                                            >
                                                <Checkbox>
                                                    <Space>
                                                        <CheckCircleOutlined />
                                                        <span>中文字幕</span>
                                                    </Space>
                                                </Checkbox>
                                            </Form.Item>
                                        </Col>
                                        <Col span={12} sm={8}>
                                            <Form.Item
                                                name="is_uncensored"
                                                valuePropName="checked"
                                                initialValue={false}
                                            >
                                                <Checkbox>
                                                    <Space>
                                                        <CheckCircleOutlined />
                                                        <span>无码</span>
                                                    </Space>
                                                </Checkbox>
                                            </Form.Item>
                                        </Col>
                                    </Row>
                                </Card>
                            </div>
                        </Col>
                    </Row>
                </Form>
            )}
        </Modal>
    );
}

export default VideoDetail;
