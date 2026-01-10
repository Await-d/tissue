import { Button, Form, Input, message, Select, Skeleton, Switch } from "antd";
import * as api from "../../../apis/setting.ts";
import { useRequest } from "ahooks";
import { createFileRoute } from "@tanstack/react-router";
import { TransModeOptions } from "../../../utils/constants.ts";
import { AxiosResponse } from "axios";

export const Route = createFileRoute('/_index/setting/download')({
    component: SettingDownload
})

function SettingDownload() {

    const [form] = Form.useForm()

    const { loading } = useRequest(api.getSettings, {
        onSuccess: (res) => {
            form.setFieldsValue(res.download)
        }
    })

    const { run, loading: saving } = useRequest(api.saveSetting, {
        manual: true,
        onSuccess: () => {
            message.success("设置成功")
        }
    })

    // 测试qBittorrent连接
    const { run: testConnection, loading: testing } = useRequest(api.testQBittorrentConnection, {
        manual: true,
        onSuccess: (res: AxiosResponse<any>) => {
            console.log("测试连接响应:", res);

            // 检查各种可能的数据格式
            if (res.data?.data?.status) {
                message.success(res.data.data.message);
            } else if (res.data?.status) {
                message.success(res.data.message);
            } else if (res.data?.success === false) {
                message.error(res.data.details || "连接失败");
            } else {
                message.error("连接测试失败，请检查设置");
            }
        },
        onError: (err) => {
            console.error("测试连接错误:", err);
            message.error("测试连接失败：" + (err.message || "未知错误"));
        }
    });

    function onFinish(data: any) {
        run('download', data)
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
                            下载设置
                        </h2>
                        <p className="text-[#a0a0a8] text-sm mt-2 ml-6">配置 qBittorrent 下载器连接和自动化选项</p>
                    </div>

                    <div className="p-8">
                        <Form layout={'vertical'} form={form} onFinish={onFinish}>
                            {/* qBittorrent 连接配置 */}
                            <div className="mb-8">
                                <h3 className="text-[#e8c780] text-lg font-semibold mb-4 flex items-center gap-2">
                                    <span className="w-1 h-5 bg-[#d4a852] rounded-full"></span>
                                    连接配置
                                </h3>
                                <div className="space-y-4">
                                    <Form.Item label={<span className="text-[#f0f0f2]">地址(qBittorrent)</span>} name={'host'}>
                                        <Input
                                            className="bg-[#141416] border-white/8 text-[#f0f0f2] hover:border-[#d4a852]/50 focus:border-[#d4a852] focus:shadow-[0_0_0_2px_rgba(212,168,82,0.1)]"
                                            placeholder="http://localhost:8080"
                                        />
                                    </Form.Item>
                                    <div className="grid grid-cols-2 gap-4">
                                        <Form.Item label={<span className="text-[#f0f0f2]">用户名</span>} name={'username'}>
                                            <Input
                                                className="bg-[#141416] border-white/8 text-[#f0f0f2] hover:border-[#d4a852]/50 focus:border-[#d4a852] focus:shadow-[0_0_0_2px_rgba(212,168,82,0.1)]"
                                                placeholder="admin"
                                            />
                                        </Form.Item>
                                        <Form.Item label={<span className="text-[#f0f0f2]">密码</span>} name={'password'}>
                                            <Input.Password
                                                autoComplete={'new-password'}
                                                className="bg-[#141416] border-white/8 text-[#f0f0f2] hover:border-[#d4a852]/50 focus:border-[#d4a852] focus:shadow-[0_0_0_2px_rgba(212,168,82,0.1)]"
                                            />
                                        </Form.Item>
                                    </div>
                                    <Form.Item label={<span className="text-[#f0f0f2]">连接测试</span>}>
                                        <div className="flex items-center gap-3">
                                            <Button
                                                loading={testing}
                                                onClick={() => testConnection()}
                                                className="bg-[#222226] border-white/8 text-[#d4a852] hover:border-[#d4a852] hover:text-[#e8c780] hover:bg-[#222226]/80"
                                            >
                                                测试连接
                                            </Button>
                                            <span className="text-[#6a6a72] text-sm">
                                                保存设置后再测试连接
                                            </span>
                                        </div>
                                    </Form.Item>
                                </div>
                            </div>

                            {/* 路径配置 */}
                            <div className="mb-8 pt-8 border-t border-white/8">
                                <h3 className="text-[#e8c780] text-lg font-semibold mb-4 flex items-center gap-2">
                                    <span className="w-1 h-5 bg-[#d4a852] rounded-full"></span>
                                    路径配置
                                </h3>
                                <div className="space-y-4">
                                    <Form.Item
                                        label={<span className="text-[#f0f0f2]">转移模式</span>}
                                        name={'trans_mode'}
                                        tooltip={'手动或自动转移使用的转移模式'}
                                    >
                                        <Select className="custom-select-dark">
                                            {TransModeOptions.map(i => (<Select.Option key={i.value}>{i.name}</Select.Option>))}
                                        </Select>
                                    </Form.Item>
                                    <div className="grid grid-cols-2 gap-4">
                                        <Form.Item
                                            label={<span className="text-[#f0f0f2]">下载路径</span>}
                                            name={'download_path'}
                                            tooltip={'将下载路径对应到系统路径，解决下载器和系统下载路径不一致的问题'}
                                        >
                                            <Input
                                                className="bg-[#141416] border-white/8 text-[#f0f0f2] hover:border-[#d4a852]/50 focus:border-[#d4a852] focus:shadow-[0_0_0_2px_rgba(212,168,82,0.1)]"
                                                placeholder="/downloads"
                                            />
                                        </Form.Item>
                                        <Form.Item label={<span className="text-[#f0f0f2]">对应路径</span>} name={'mapping_path'}>
                                            <Input
                                                className="bg-[#141416] border-white/8 text-[#f0f0f2] hover:border-[#d4a852]/50 focus:border-[#d4a852] focus:shadow-[0_0_0_2px_rgba(212,168,82,0.1)]"
                                                placeholder="/mnt/downloads"
                                            />
                                        </Form.Item>
                                    </div>
                                    <Form.Item
                                        label={<span className="text-[#f0f0f2]">默认保存路径</span>}
                                        name={'savepath'}
                                        tooltip={'设置qBittorrent默认保存路径，留空则使用qBittorrent默认设置'}
                                    >
                                        <Input
                                            placeholder={'例如：/downloads/av'}
                                            className="bg-[#141416] border-white/8 text-[#f0f0f2] hover:border-[#d4a852]/50 focus:border-[#d4a852] focus:shadow-[0_0_0_2px_rgba(212,168,82,0.1)]"
                                        />
                                    </Form.Item>
                                </div>
                            </div>

                            {/* 自动化选项 */}
                            <div className="mb-8 pt-8 border-t border-white/8">
                                <h3 className="text-[#e8c780] text-lg font-semibold mb-4 flex items-center gap-2">
                                    <span className="w-1 h-5 bg-[#d4a852] rounded-full"></span>
                                    自动化选项
                                </h3>
                                <div className="grid grid-cols-1 gap-6">
                                    <Form.Item
                                        label={<span className="text-[#f0f0f2]">自动转移(Beta)</span>}
                                        name={'trans_auto'}
                                        valuePropName={'checked'}
                                        tooltip={'下载完成后是否自动转移到影片任务'}
                                        className="mb-0"
                                    >
                                        <Switch className="custom-switch-gold" />
                                    </Form.Item>
                                    <Form.Item
                                        label={<span className="text-[#f0f0f2]">自动删种(Beta)</span>}
                                        name={'delete_auto'}
                                        valuePropName={'checked'}
                                        tooltip={'整理完成后自动删除种子及数据'}
                                        className="mb-0"
                                    >
                                        <Switch className="custom-switch-gold" />
                                    </Form.Item>
                                    <Form.Item
                                        label={<span className="text-[#f0f0f2]">完成后停止做种</span>}
                                        name={'stop_seeding'}
                                        valuePropName={'checked'}
                                        tooltip={'种子下载完成并整理成功后自动停止做种，默认开启'}
                                        className="mb-0"
                                    >
                                        <Switch className="custom-switch-gold" />
                                    </Form.Item>
                                </div>
                            </div>

                            {/* 高级选项 */}
                            <div className="mb-8 pt-8 border-t border-white/8">
                                <h3 className="text-[#e8c780] text-lg font-semibold mb-4 flex items-center gap-2">
                                    <span className="w-1 h-5 bg-[#d4a852] rounded-full"></span>
                                    高级选项
                                </h3>
                                <div className="space-y-4">
                                    <Form.Item
                                        label={<span className="text-[#f0f0f2]">任务分类</span>}
                                        name={'category'}
                                        tooltip="只有指定类别的任务会被识别，留空则为所有任务"
                                    >
                                        <Input
                                            placeholder={'留空则为所有任务'}
                                            className="bg-[#141416] border-white/8 text-[#f0f0f2] hover:border-[#d4a852]/50 focus:border-[#d4a852] focus:shadow-[0_0_0_2px_rgba(212,168,82,0.1)]"
                                        />
                                    </Form.Item>
                                    <Form.Item
                                        label={<span className="text-[#f0f0f2]">订阅Tracker</span>}
                                        name={'tracker_subscribe'}
                                        tooltip={(
                                            <span>通过Tracker订阅链接，自动为任务添加Tracker列表。
                                                <a target='_blank' href={'https://trackerslist.com/'} className="text-[#d4a852] hover:text-[#e8c780]">示例</a>
                                            </span>
                                        )}
                                    >
                                        <Input
                                            placeholder={'请输入Tracker订阅链接'}
                                            className="bg-[#141416] border-white/8 text-[#f0f0f2] hover:border-[#d4a852]/50 focus:border-[#d4a852] focus:shadow-[0_0_0_2px_rgba(212,168,82,0.1)]"
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
