import {useEffect} from "react";
import {Button, Form, message, Select, Skeleton} from "antd";
import {useRequest} from "ahooks";
import * as api from "../../../apis/setting.ts";
import Telegram from "./-component/telegram.tsx";
import Webhook from "./-component/webhook.tsx";
import {createFileRoute} from "@tanstack/react-router";
import { useThemeColors } from '../../../hooks/useThemeColors';

const notifications = [
    {name: 'Telegram', value: 'telegram', element: Telegram},
    {name: 'Webhook', value: 'webhook', element: Webhook},
]

export const Route = createFileRoute('/_index/setting/notify')({
    component: SettingNotify
})

function SettingNotify() {

    const colors = useThemeColors()
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
                <div style={{ backgroundColor: colors.bgContainer, borderColor: colors.borderPrimary }} className="rounded-2xl border shadow-2xl overflow-hidden">
                    {/* 页面标题 */}
                    <div style={{ borderBottomColor: colors.borderPrimary, backgroundImage: `linear-gradient(to right, ${colors.bgElevated}, ${colors.bgContainer})` }} className="px-8 py-6 border-b">
                        <h2 style={{ color: colors.goldPrimary }} className="text-2xl font-bold flex items-center gap-3">
                            <span style={{ backgroundImage: `linear-gradient(to bottom, ${colors.goldPrimary}, ${colors.goldDark})` }} className="w-1.5 h-8 rounded-full"></span>
                            通知设置
                        </h2>
                        <p style={{ color: colors.textSecondary }} className="text-sm mt-2 ml-6">配置消息通知方式和参数</p>
                    </div>

                    <div className="p-8">
                        <Form layout={'vertical'} form={form} onFinish={onFinish}>
                            <div className="mb-8">
                                <h3 style={{ color: colors.goldLight }} className="text-lg font-semibold mb-4 flex items-center gap-2">
                                    <span style={{ backgroundColor: colors.goldPrimary }} className="w-1 h-5 rounded-full"></span>
                                    通知配置
                                </h3>
                                <div className="space-y-4">
                                    <Form.Item name={'type'} label={<span style={{ color: colors.textPrimary }}>类型</span>} initialValue={'telegram'}>
                                        <Select className="custom-select-dark">
                                            {notifications.map(item => (
                                                <Select.Option key={item.value} value={item.value}>{item.name}</Select.Option>
                                            ))}
                                        </Select>
                                    </Form.Item>
                                    {ItemElement && (
                                        <div style={{ backgroundColor: colors.bgElevated, borderColor: colors.borderPrimary }} className="rounded-lg p-6 border">
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
                                    style={{
                                        width: '192px',
                                        height: '44px',
                                        background: colors.goldGradient,
                                        border: 'none',
                                        color: colors.bgBase,
                                        fontWeight: '600'
                                    }}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.backgroundImage = colors.goldGradientHover;
                                        e.currentTarget.style.boxShadow = `0 0 20px ${colors.rgba('gold', 0.2)}`;
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.backgroundImage = colors.goldGradient;
                                        e.currentTarget.style.boxShadow = 'none';
                                    }}
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

