import {Button, Card, Form, Input, InputNumber, message, Skeleton, Space, Tooltip} from "antd";
import * as api from "../../../apis/setting.ts";
import {useRequest} from "ahooks";
import {createFileRoute} from "@tanstack/react-router";
import {
    FolderOutlined,
    FileTextOutlined,
    DatabaseOutlined,
    GlobalOutlined,
    ClockCircleOutlined,
    InfoCircleOutlined,
    ReloadOutlined,
    SaveOutlined
} from "@ant-design/icons";

export const Route = createFileRoute('/_index/setting/app')({
    component: SettingApp
})

function SettingApp() {
    const [form] = Form.useForm()

    const {loading, data: settingsData} = useRequest(api.getSettings, {
        onSuccess: (res) => {
            form.setFieldsValue(res.app)
        }
    })

    const {run, loading: saving} = useRequest(api.saveSetting, {
        manual: true,
        onSuccess: () => {
            message.success("设置保存成功")
        },
        onError: (error) => {
            message.error(`保存失败: ${error.message}`)
        }
    })

    function onFinish(data: any) {
        run('app', data)
    }

    function handleReset() {
        if (settingsData?.app) {
            form.setFieldsValue(settingsData.app)
            message.info("已重置为当前保存的值")
        }
    }

    return (
        loading ? (
            <Skeleton active />
        ) : (
            <div className={'w-[800px] max-w-full my-0 mx-auto px-4'}>
                <Form layout={'vertical'} form={form} onFinish={onFinish}>
                    {/* 视频配置 */}
                    <Card
                        title={
                            <Space>
                                <FileTextOutlined />
                                <span>视频配置</span>
                            </Space>
                        }
                        className="mb-6 shadow-sm"
                    >
                        <Form.Item
                            label={
                                <Space>
                                    <FolderOutlined />
                                    <span>视频路径</span>
                                </Space>
                            }
                            name={'video_path'}
                            tooltip={{
                                title: "视频文件存储的根目录路径",
                                icon: <InfoCircleOutlined />
                            }}
                        >
                            <Input placeholder="例如: /media/videos" />
                        </Form.Item>

                        <Form.Item
                            label={
                                <Space>
                                    <FileTextOutlined />
                                    <span>视频格式</span>
                                </Space>
                            }
                            name={'video_format'}
                            tooltip={{
                                title: "支持的视频文件格式，多个格式用逗号分隔",
                                icon: <InfoCircleOutlined />
                            }}
                        >
                            <Input placeholder="例如: mp4,mkv,avi" />
                        </Form.Item>

                        <Form.Item
                            label={
                                <Space>
                                    <DatabaseOutlined />
                                    <span>视频最小容量</span>
                                </Space>
                            }
                            name={'video_size_minimum'}
                            tooltip={{
                                title: "过滤小于此大小的视频文件，支持单位如 100MB, 1GB",
                                icon: <InfoCircleOutlined />
                            }}
                        >
                            <Input placeholder="例如: 100MB" />
                        </Form.Item>
                    </Card>

                    {/* 网络配置 */}
                    <Card
                        title={
                            <Space>
                                <GlobalOutlined />
                                <span>网络配置</span>
                            </Space>
                        }
                        className="mb-6 shadow-sm"
                    >
                        <Form.Item
                            label={
                                <Space>
                                    <GlobalOutlined />
                                    <span>User Agent</span>
                                </Space>
                            }
                            name={'user_agent'}
                            tooltip={{
                                title: "HTTP 请求时使用的 User Agent 标识",
                                icon: <InfoCircleOutlined />
                            }}
                        >
                            <Input.TextArea
                                rows={2}
                                placeholder="例如: Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
                            />
                        </Form.Item>

                        <Form.Item
                            label={
                                <Space>
                                    <ClockCircleOutlined />
                                    <span>超时时间</span>
                                </Space>
                            }
                            name={'timeout'}
                            tooltip={{
                                title: "网络请求的超时时间，单位为秒",
                                icon: <InfoCircleOutlined />
                            }}
                        >
                            <InputNumber
                                style={{width: '100%'}}
                                min={1}
                                max={300}
                                placeholder="30"
                                addonAfter="秒"
                            />
                        </Form.Item>
                    </Card>

                    {/* 操作按钮 */}
                    <div className="flex justify-center gap-4 pb-6">
                        <Button
                            icon={<ReloadOutlined />}
                            onClick={handleReset}
                            disabled={saving}
                        >
                            重置
                        </Button>
                        <Button
                            type={'primary'}
                            icon={<SaveOutlined />}
                            loading={saving}
                            htmlType={"submit"}
                            size="large"
                            className="min-w-[150px]"
                        >
                            保存设置
                        </Button>
                    </div>
                </Form>
            </div>
        )
    )
}
