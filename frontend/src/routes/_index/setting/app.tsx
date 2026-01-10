import {Button, Form, Input, InputNumber, message, Skeleton, Switch, Divider} from "antd";
import * as api from "../../../apis/setting.ts";
import {useRequest} from "ahooks";
import {createFileRoute} from "@tanstack/react-router";


export const Route = createFileRoute('/_index/setting/app')({
    component: SettingApp
})

function SettingApp() {

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
                <div className="bg-[#1a1a1d] rounded-2xl border border-white/8 shadow-2xl overflow-hidden">
                    {/* 页面标题 */}
                    <div className="px-8 py-6 border-b border-white/8 bg-gradient-to-r from-[#141416] to-[#1a1a1d]">
                        <h2 className="text-2xl font-bold text-[#d4a852] flex items-center gap-3">
                            <span className="w-1.5 h-8 bg-gradient-to-b from-[#d4a852] to-[#b08d3e] rounded-full"></span>
                            应用设置
                        </h2>
                        <p className="text-[#a0a0a8] text-sm mt-2 ml-6">配置应用基础选项和刮削参数</p>
                    </div>

                    <div className="p-8">
                        <Form layout={'vertical'} form={form} onFinish={onFinish}>
                            {/* 视频配置 */}
                            <div className="mb-8">
                                <h3 className="text-[#e8c780] text-lg font-semibold mb-4 flex items-center gap-2">
                                    <span className="w-1 h-5 bg-[#d4a852] rounded-full"></span>
                                    视频配置
                                </h3>
                                <div className="space-y-4">
                                    <Form.Item label={<span className="text-[#f0f0f2]">视频路径</span>} name={'video_path'}>
                                        <Input
                                            className="bg-[#141416] border-white/8 text-[#f0f0f2] hover:border-[#d4a852]/50 focus:border-[#d4a852] focus:shadow-[0_0_0_2px_rgba(212,168,82,0.1)]"
                                            placeholder="/path/to/videos"
                                        />
                                    </Form.Item>
                                    <div className="grid grid-cols-2 gap-4">
                                        <Form.Item label={<span className="text-[#f0f0f2]">视频格式</span>} name={'video_format'}>
                                            <Input
                                                className="bg-[#141416] border-white/8 text-[#f0f0f2] hover:border-[#d4a852]/50 focus:border-[#d4a852] focus:shadow-[0_0_0_2px_rgba(212,168,82,0.1)]"
                                                placeholder="mp4,mkv,avi"
                                            />
                                        </Form.Item>
                                        <Form.Item label={<span className="text-[#f0f0f2]">视频最小容量</span>} name={'video_size_minimum'}>
                                            <Input
                                                className="bg-[#141416] border-white/8 text-[#f0f0f2] hover:border-[#d4a852]/50 focus:border-[#d4a852] focus:shadow-[0_0_0_2px_rgba(212,168,82,0.1)]"
                                                placeholder="100MB"
                                            />
                                        </Form.Item>
                                    </div>
                                </div>
                            </div>

                            {/* 网络配置 */}
                            <div className="mb-8 pt-8 border-t border-white/8">
                                <h3 className="text-[#e8c780] text-lg font-semibold mb-4 flex items-center gap-2">
                                    <span className="w-1 h-5 bg-[#d4a852] rounded-full"></span>
                                    网络配置
                                </h3>
                                <div className="space-y-4">
                                    <Form.Item label={<span className="text-[#f0f0f2]">User Agent</span>} name={'user_agent'}>
                                        <Input
                                            className="bg-[#141416] border-white/8 text-[#f0f0f2] hover:border-[#d4a852]/50 focus:border-[#d4a852] focus:shadow-[0_0_0_2px_rgba(212,168,82,0.1)]"
                                            placeholder="Mozilla/5.0..."
                                        />
                                    </Form.Item>
                                    <Form.Item label={<span className="text-[#f0f0f2]">超时时间(秒)</span>} name={'timeout'}>
                                        <InputNumber
                                            style={{width: '100%'}}
                                            className="bg-[#141416] border-white/8 text-[#f0f0f2] hover:border-[#d4a852]/50 focus:border-[#d4a852] focus:shadow-[0_0_0_2px_rgba(212,168,82,0.1)]"
                                            placeholder="30"
                                        />
                                    </Form.Item>
                                </div>
                            </div>

                            {/* 并发刮削设置 */}
                            <div className="mb-8 pt-8 border-t border-white/8">
                                <h3 className="text-[#e8c780] text-lg font-semibold mb-4 flex items-center gap-2">
                                    <span className="w-1 h-5 bg-[#d4a852] rounded-full"></span>
                                    并发刮削设置
                                </h3>
                                <div className="space-y-6">
                                    <Form.Item
                                        label={<span className="text-[#f0f0f2]">启用并发刮削</span>}
                                        name={'concurrent_scraping'}
                                        valuePropName={'checked'}
                                        tooltip={'启用后可同时从多个数据源获取信息，显著提升刮削速度'}
                                        className="mb-0"
                                    >
                                        <Switch className="custom-switch-gold" />
                                    </Form.Item>
                                    <Form.Item
                                        label={<span className="text-[#f0f0f2]">最大并发数</span>}
                                        name={'max_concurrent_spiders'}
                                        tooltip={'同时处理的爬虫数量，建议2-6个，过多可能被限制访问'}
                                    >
                                        <InputNumber
                                            min={1}
                                            max={10}
                                            style={{width: '100%'}}
                                            className="bg-[#141416] border-white/8 text-[#f0f0f2] hover:border-[#d4a852]/50 focus:border-[#d4a852] focus:shadow-[0_0_0_2px_rgba(212,168,82,0.1)]"
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

