import {Form, Input, Switch} from "antd";
import {createFileRoute} from "@tanstack/react-router";

import {SettingsPage} from "./-component/SettingsPage";
import {useSectionSettings} from "./-context/SettingsContext";
import { useThemeColors } from '../../../hooks/useThemeColors';

export const Route = createFileRoute('/_index/setting/cookiecloud')({
    component: SettingCookieCloud,
})

function SettingCookieCloud() {
    const colors = useThemeColors()
    const {form, loading, saving, submit} = useSectionSettings('cookiecloud')

    return (
        <SettingsPage
            title="CookieCloud"
            subtitle="配置浏览器 Cookie 同步参数"
            loading={loading}
            form={form}
            onFinish={submit}
            saving={saving}
            maxWidth="5xl"
            headerGradient="elevated"
            cardBorder="solid"
            saveButtonVariant="plain"
        >
            <Form.Item name={'enabled'} valuePropName={'checked'} label={<span style={{ color: colors.textPrimary }}>启用同步</span>}>
                <Switch className="custom-switch-gold" />
            </Form.Item>
            <Form.Item name={'host'} label={<span style={{ color: colors.textPrimary }}>服务地址</span>}>
                <Input placeholder="https://cookiecloud.example.com" />
            </Form.Item>
            <Form.Item name={'uuid'} label={<span style={{ color: colors.textPrimary }}>UUID</span>}>
                <Input placeholder="CookieCloud UUID" />
            </Form.Item>
            <Form.Item name={'password'} label={<span style={{ color: colors.textPrimary }}>密码</span>}>
                <Input.Password placeholder="CookieCloud Password" />
            </Form.Item>
        </SettingsPage>
    )
}
