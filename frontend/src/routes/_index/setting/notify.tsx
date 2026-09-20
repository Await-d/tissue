import {Form, Select} from "antd";
import Telegram from "./-component/telegram.tsx";
import Webhook from "./-component/webhook.tsx";
import {createFileRoute} from "@tanstack/react-router";
import {SettingsPage} from "./-component/SettingsPage.tsx";
import {useSectionSettings} from "./-context/SettingsContext.tsx";
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
    const {form, loading, saving, submit} = useSectionSettings('notify')

    const type = Form.useWatch('type', form)

    const ItemElement = notifications.find(item => item.value === type)?.element

    return (
        <SettingsPage
            title="通知设置"
            subtitle="配置消息通知方式和参数"
            loading={loading}
            form={form}
            onFinish={submit}
            saving={saving}
            maxWidth="5xl"
            headerGradient="elevated"
            cardBorder="solid"
            saveButtonVariant="hover"
        >
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
        </SettingsPage>
    )
}
