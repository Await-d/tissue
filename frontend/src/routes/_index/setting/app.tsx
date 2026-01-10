import {Button, Form, Input, InputNumber, message, Skeleton, Switch, Divider} from "antd";
import * as api from "../../../apis/setting.ts";
import {useRequest} from "ahooks";
import {createFileRoute} from "@tanstack/react-router";
import { useThemeColors } from "../../../hooks/useThemeColors";


export const Route = createFileRoute('/_index/setting/app')({
    component: SettingApp
})

function SettingApp() {
    const colors = useThemeColors();
    const [form] = Form.useForm()

    const {loading} = useRequest(api.getSettings, {
        onSuccess: (res) => {
            form.setFieldsValue(res.app)
        }
    })

    const {run, loading: saving} = useRequest(api.saveSetting, {
        manual: true,
        onSuccess: () => {
            message.success("设置成功")
        }
    })

    function onFinish(data: any) {
        run('app', data)
    }

    return (
        loading ? (
            <Skeleton active />
        ) : (
            <div className="max-w-5xl mx-auto px-6 py-8">
                <div style={{ background: colors.cardBg }} className="rounded-2xl border shadow-2xl overflow-hidden" style={{ borderColor: colors.border }}>
                    {/* 页面标题 */}
                    <div className="px-8 py-6 border-b" style={{
                        borderColor: colors.border,
                        background: `linear-gradient(to right, ${colors.bgDark}, ${colors.cardBg})`
                    }}>
                        <h2 className="text-2xl font-bold flex items-center gap-3" style={{ color: colors.gold }}>
                            <span className="w-1.5 h-8 rounded-full" style={{
                                background: `linear-gradient(to bottom, ${colors.gold}, ${colors.goldDark})`
                            }}></span>
                            应用设置
                        </h2>
                        <p className="text-sm mt-2 ml-6" style={{ color: colors.textMuted }}>配置应用基础选项和刮削参数</p>
                    </div>

                    <div className="p-8">
                        <Form layout={'vertical'} form={form} onFinish={onFinish}>
                            {/* 视频配置 */}
                            <div className="mb-8">
                                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ color: colors.goldLight }}>
                                    <span className="w-1 h-5 rounded-full" style={{ background: colors.gold }}></span>
                                    视频配置
                                </h3>
                                <div className="space-y-4">
                                    <Form.Item label={<span style={{ color: colors.text }}>视频路径</span>} name={'video_path'}>
                                        <Input
                                            style={{
                                                background: colors.bgDark,
                                                borderColor: colors.border,
                                                color: colors.text
                                            }}
                                            className="hover:border-opacity-50 focus:shadow-sm"
                                            placeholder="/path/to/videos"
                                        />
                                    </Form.Item>
                                    <div className="grid grid-cols-2 gap-4">
                                        <Form.Item label={<span style={{ color: colors.text }}>视频格式</span>} name={'video_format'}>
                                            <Input
                                                style={{
                                                    background: colors.bgDark,
                                                    borderColor: colors.border,
                                                    color: colors.text
                                                }}
                                                className="hover:border-opacity-50 focus:shadow-sm"
                                                placeholder="mp4,mkv,avi"
                                            />
                                        </Form.Item>
                                        <Form.Item label={<span style={{ color: colors.text }}>视频最小容量</span>} name={'video_size_minimum'}>
                                            <Input
                                                style={{
                                                    background: colors.bgDark,
                                                    borderColor: colors.border,
                                                    color: colors.text
                                                }}
                                                className="hover:border-opacity-50 focus:shadow-sm"
                                                placeholder="100MB"
                                            />
                                        </Form.Item>
                                    </div>
                                </div>
                            </div>

                            {/* 网络配置 */}
                            <div className="mb-8 pt-8 border-t" style={{ borderColor: colors.border }}>
                                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ color: colors.goldLight }}>
                                    <span className="w-1 h-5 rounded-full" style={{ background: colors.gold }}></span>
                                    网络配置
                                </h3>
                                <div className="space-y-4">
                                    <Form.Item label={<span style={{ color: colors.text }}>User Agent</span>} name={'user_agent'}>
                                        <Input
                                            style={{
                                                background: colors.bgDark,
                                                borderColor: colors.border,
                                                color: colors.text
                                            }}
                                            className="hover:border-opacity-50 focus:shadow-sm"
                                            placeholder="Mozilla/5.0..."
                                        />
                                    </Form.Item>
                                    <Form.Item label={<span style={{ color: colors.text }}>超时时间(秒)</span>} name={'timeout'}>
                                        <InputNumber
                                            style={{
                                                width: '100%',
                                                background: colors.bgDark,
                                                borderColor: colors.border,
                                                color: colors.text
                                            }}
                                            className="hover:border-opacity-50 focus:shadow-sm"
                                            placeholder="30"
                                        />
                                    </Form.Item>
                                </div>
                            </div>

                            {/* 并发刮削设置 */}
                            <div className="mb-8 pt-8 border-t" style={{ borderColor: colors.border }}>
                                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ color: colors.goldLight }}>
                                    <span className="w-1 h-5 rounded-full" style={{ background: colors.gold }}></span>
                                    并发刮削设置
                                </h3>
                                <div className="space-y-6">
                                    <Form.Item
                                        label={<span style={{ color: colors.text }}>启用并发刮削</span>}
                                        name={'concurrent_scraping'}
                                        valuePropName={'checked'}
                                        tooltip={'启用后可同时从多个数据源获取信息，显著提升刮削速度'}
                                        className="mb-0"
                                    >
                                        <Switch className="custom-switch-gold" />
                                    </Form.Item>
                                    <Form.Item
                                        label={<span style={{ color: colors.text }}>最大并发数</span>}
                                        name={'max_concurrent_spiders'}
                                        tooltip={'同时处理的爬虫数量，建议2-6个，过多可能被限制访问'}
                                    >
                                        <InputNumber
                                            min={1}
                                            max={10}
                                            style={{
                                                width: '100%',
                                                background: colors.bgDark,
                                                borderColor: colors.border,
                                                color: colors.text
                                            }}
                                            className="hover:border-opacity-50 focus:shadow-sm"
                                            placeholder="4"
                                        />
                                    </Form.Item>
                                </div>
                            </div>

                            <div className="flex justify-center pt-6">
                                <Button
                                    type={'primary'}
                                    size="large"
                                    loading={saving}
                                    htmlType={"submit"}
                                    style={{
                                        background: `linear-gradient(to right, ${colors.gold}, ${colors.goldDark})`,
                                        border: 0,
                                        color: colors.buttonText,
                                        fontWeight: 600
                                    }}
                                    className="w-48 h-11 shadow-lg hover:shadow-xl"
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

