import {Button, Form, Input, message, Skeleton, Switch} from "antd";
import {useRequest} from "ahooks";
import {createFileRoute} from "@tanstack/react-router";

import * as api from "../../../apis/setting.ts";
import { useThemeColors } from '../../../hooks/useThemeColors';

export const Route = createFileRoute('/_index/setting/cookiecloud')({
    component: SettingCookieCloud,
})

function SettingCookieCloud() {
    const colors = useThemeColors()
    const [form] = Form.useForm()

    const {loading} = useRequest(api.getSettings, {
        onSuccess: (res) => {
            form.setFieldsValue(res.cookiecloud)
        },
    })

    const {run, loading: saving} = useRequest(api.saveSetting, {
        manual: true,
        onSuccess: () => {
            message.success("设置成功")
        },
    })

    function onFinish(data: unknown) {
        run('cookiecloud', data)
    }

    return loading ? (
        <Skeleton active/>
    ) : (
        <div className="max-w-5xl mx-auto px-6 py-8">
            <div style={{ backgroundColor: colors.bgContainer, borderColor: colors.borderPrimary }} className="rounded-2xl border shadow-2xl overflow-hidden">
                <div style={{ borderBottomColor: colors.borderPrimary, backgroundImage: `linear-gradient(to right, ${colors.bgElevated}, ${colors.bgContainer})` }} className="px-8 py-6 border-b">
                    <h2 style={{ color: colors.goldPrimary }} className="text-2xl font-bold flex items-center gap-3">
                        <span style={{ backgroundImage: `linear-gradient(to bottom, ${colors.goldPrimary}, ${colors.goldDark})` }} className="w-1.5 h-8 rounded-full"></span>
                        CookieCloud
                    </h2>
                    <p style={{ color: colors.textSecondary }} className="text-sm mt-2 ml-6">配置浏览器 Cookie 同步参数</p>
                </div>

                <div className="p-8">
                    <Form layout={'vertical'} form={form} onFinish={onFinish}>
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
                        <div className="flex justify-center pt-6">
                            <Button type={'primary'} size="large" loading={saving} htmlType={"submit"} style={{
                                width: '192px',
                                height: '44px',
                                background: colors.goldGradient,
                                border: 'none',
                                color: colors.bgBase,
                                fontWeight: '600'
                            }}>
                                保存设置
                            </Button>
                        </div>
                    </Form>
                </div>
            </div>
        </div>
    )
}
