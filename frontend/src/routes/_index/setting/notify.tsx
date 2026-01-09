import {Button, Card, Form, message, Select, Skeleton, Space} from "antd";
import {useRequest} from "ahooks";
import * as api from "../../../apis/setting.ts";
import Telegram from "./-component/telegram.tsx";
import Webhook from "./-component/webhook.tsx";
import {createFileRoute} from "@tanstack/react-router";
import {
    BellOutlined,
    InfoCircleOutlined,
    ReloadOutlined,
    SaveOutlined,
    ApiOutlined
} from "@ant-design/icons";

const notifications = [
    {name: 'Telegram', value: 'telegram', element: Telegram, icon: '📱'},
    {name: 'Webhook', value: 'webhook', element: Webhook, icon: '🔗'},
]

export const Route = createFileRoute('/_index/setting/notify')({
    component: SettingNotify
})

function SettingNotify() {
    const [form] = Form.useForm()

    const type = Form.useWatch('type', form)

    const {loading, data: settingsData} = useRequest(api.getSettings, {
        onSuccess: (res) => {
            form.setFieldsValue(res.notify)
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
        run('notify', data)
    }

    function handleReset() {
        if (settingsData?.notify) {
            form.setFieldsValue(settingsData.notify)
            message.info("已重置为当前保存的值")
        }
    }

    const ItemElement = notifications.find(item => item.value === type)?.element
    const selectedNotification = notifications.find(item => item.value === type)

    return (
        loading ? (
            <Skeleton active/>
        ) : (
            <div className={'w-[800px] max-w-full my-0 mx-auto px-4'}>
                <Form layout={'vertical'} form={form} onFinish={onFinish}>
                    {/* 通知类型选择 */}
                    <Card
                        title={
                            <Space>
                                <BellOutlined />
                                <span>通知配置</span>
                            </Space>
                        }
                        className="mb-6 shadow-sm"
                        extra={
                            <span className="text-sm text-gray-500">
                                配置系统通知推送方式
                            </span>
                        }
                    >
                        <Form.Item
                            name={'type'}
                            label={
                                <Space>
                                    <ApiOutlined />
                                    <span>通知类型</span>
                                </Space>
                            }
                            initialValue={'telegram'}
                            tooltip={{
                                title: "选择接收通知的方式",
                                icon: <InfoCircleOutlined />
                            }}
                        >
                            <Select size="large">
                                {notifications.map(item => (
                                    <Select.Option key={item.value} value={item.value}>
                                        <Space>
                                            <span>{item.icon}</span>
                                            <span>{item.name}</span>
                                        </Space>
                                    </Select.Option>
                                ))}
                            </Select>
                        </Form.Item>

                        {/* 说明信息 */}
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                            <div className="flex items-start gap-2">
                                <InfoCircleOutlined className="text-blue-500 mt-1" />
                                <div className="text-sm text-gray-700">
                                    <p className="font-medium mb-1">通知类型说明：</p>
                                    <ul className="list-disc list-inside space-y-1 text-gray-600">
                                        <li><strong>Telegram</strong>：通过 Telegram Bot 发送通知消息</li>
                                        <li><strong>Webhook</strong>：通过自定义 Webhook 接口发送通知</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </Card>

                    {/* 具体配置 */}
                    {ItemElement && (
                        <Card
                            title={
                                <Space>
                                    <span>{selectedNotification?.icon}</span>
                                    <span>{selectedNotification?.name} 配置</span>
                                </Space>
                            }
                            className="mb-6 shadow-sm"
                        >
                            <ItemElement/>
                        </Card>
                    )}

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
