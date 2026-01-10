import {useEffect} from "react";
import {Button, Form, message, Select, Skeleton} from "antd";
import {useRequest} from "ahooks";
import * as api from "../../../apis/setting.ts";
import Telegram from "./-component/telegram.tsx";
import Webhook from "./-component/webhook.tsx";
import {createFileRoute} from "@tanstack/react-router";

const notifications = [
    {name: 'Telegram', value: 'telegram', element: Telegram},
    {name: 'Webhook', value: 'webhook', element: Webhook},
]

export const Route = createFileRoute('/_index/setting/notify')({
    component: SettingNotify
})

function SettingNotify() {

    const [form] = Form.useForm()

    const type = Form.useWatch('type', form)

    const {loading} = useRequest(api.getSettings, {
        onSuccess: (res) => {
            form.setFieldsValue(res.notify)
        }
    })

    const {run, loading: saving} = useRequest(api.saveSetting, {
        manual: true,
        onSuccess: () => {
            message.success("设置成功")
        }
    })

    function onFinish(data: any) {
        run('notify', data)
    }

    const ItemElement = notifications.find(item => item.value === type)?.element

    return (
        loading ? (
            <Skeleton active/>
        ) : (
            <div className="max-w-5xl mx-auto px-6 py-8">
                <div className="bg-[#1a1a1d] rounded-2xl border border-white/8 shadow-2xl overflow-hidden">
                    {/* 页面标题 */}
                    <div className="px-8 py-6 border-b border-white/8 bg-gradient-to-r from-[#141416] to-[#1a1a1d]">
                        <h2 className="text-2xl font-bold text-[#d4a852] flex items-center gap-3">
                            <span className="w-1.5 h-8 bg-gradient-to-b from-[#d4a852] to-[#b08d3e] rounded-full"></span>
                            通知设置
                        </h2>
                        <p className="text-[#a0a0a8] text-sm mt-2 ml-6">配置消息通知方式和参数</p>
                    </div>

                    <div className="p-8">
                        <Form layout={'vertical'} form={form} onFinish={onFinish}>
                            <div className="mb-8">
                                <h3 className="text-[#e8c780] text-lg font-semibold mb-4 flex items-center gap-2">
                                    <span className="w-1 h-5 bg-[#d4a852] rounded-full"></span>
                                    通知配置
                                </h3>
                                <div className="space-y-4">
                                    <Form.Item name={'type'} label={<span className="text-[#f0f0f2]">类型</span>} initialValue={'telegram'}>
                                        <Select className="custom-select-dark">
                                            {notifications.map(item => (
                                                <Select.Option key={item.value} value={item.value}>{item.name}</Select.Option>
                                            ))}
                                        </Select>
                                    </Form.Item>
                                    {ItemElement && (
                                        <div className="bg-[#141416] rounded-lg p-6 border border-white/8">
                                            <ItemElement/>
                                        </div>
                                    )}
                                </div>
                            </div>

                            <div className="flex justify-center pt-6">
                                <Button
                                    type={'primary'}
                                    size="large"
                                    loading={saving}
                                    htmlType={"submit"}
                                    className="w-48 h-11 bg-gradient-to-r from-[#d4a852] to-[#b08d3e] border-0 text-[#0d0d0f] font-semibold hover:from-[#e8c780] hover:to-[#d4a852] shadow-lg hover:shadow-[#d4a852]/20"
                                >
                                    保存设置
                                </Button>
                            </div>
                        </Form>
                    </div>
                </div>
            </div>
        )
    )
}

