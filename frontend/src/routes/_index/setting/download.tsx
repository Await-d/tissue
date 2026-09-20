import { App, Button, Form, Input, Select, Switch } from "antd";
import * as api from "../../../apis/setting.ts";
import { useRequest } from "ahooks";
import { createFileRoute } from "@tanstack/react-router";
import { TransModeOptions } from "../../../utils/constants.ts";
import { useThemeColors } from "../../../hooks/useThemeColors";
import { SettingsPage } from "./-component/SettingsPage";
import { useSectionSettings } from "./-context/SettingsContext";

export const Route = createFileRoute('/_index/setting/download')({
    component: SettingDownload
})

function SettingDownload() {
    const colors = useThemeColors();
    const { message } = App.useApp();
    const { form, loading, saving, submit } = useSectionSettings('download')

    // 测试qBittorrent连接
    const { run: testConnection, loading: testing } = useRequest(api.testQBittorrentConnection, {
        manual: true,
        onSuccess: (res) => {
            console.log("测试连接响应:", res);
            const result = res.data;

            if (res.success) {
                message.success(result?.message || "连接成功");
            } else {
                message.error(res.details || result?.message || "连接失败");
            }
        },
        onError: (err) => {
            console.error("测试连接错误:", err);
            message.error("测试连接失败：" + (err.message || "未知错误"));
        }
    });

    return (
        <SettingsPage
            title="下载设置"
            subtitle={<span style={{ color: colors.textMuted }}>配置 qBittorrent 下载器连接和自动化选项</span>}
            loading={loading}
            form={form}
            onFinish={submit}
            saving={saving}
            maxWidth="5xl"
            headerGradient="base"
            cardBorder="solid"
            saveButtonVariant="legacy"
        >
            {/* qBittorrent 连接配置 */}
                            <div className="mb-8">
                                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ color: colors.goldLight }}>
                                    <span className="w-1 h-5 rounded-full" style={{ background: colors.gold }}></span>
                                    连接配置
                                </h3>
                                <div className="space-y-4">
                                    <Form.Item label={<span style={{ color: colors.text }}>地址(qBittorrent)</span>} name={'host'}>
                                        <Input
                                            style={{
                                                background: colors.bgDark,
                                                borderColor: colors.border,
                                                color: colors.text
                                            }}
                                            className="hover:border-opacity-50 focus:shadow-sm"
                                            placeholder="http://localhost:8080"
                                        />
                                    </Form.Item>
                                    <div className="grid grid-cols-2 gap-4">
                                        <Form.Item label={<span style={{ color: colors.text }}>用户名</span>} name={'username'}>
                                            <Input
                                                autoComplete={'username'}
                                                style={{
                                                    background: colors.bgDark,
                                                    borderColor: colors.border,
                                                    color: colors.text
                                                }}
                                                className="hover:border-opacity-50 focus:shadow-sm"
                                                placeholder="admin"
                                            />
                                        </Form.Item>
                                        <Form.Item label={<span style={{ color: colors.text }}>密码</span>} name={'password'}>
                                            <Input.Password
                                                autoComplete={'new-password'}
                                                style={{
                                                    background: colors.bgDark,
                                                    borderColor: colors.border,
                                                    color: colors.text
                                                }}
                                                className="hover:border-opacity-50 focus:shadow-sm"
                                            />
                                        </Form.Item>
                                    </div>
                                    <Form.Item label={<span style={{ color: colors.text }}>连接测试</span>}>
                                        <div className="flex items-center gap-3">
                                            <Button
                                                loading={testing}
                                                onClick={() => testConnection()}
                                                style={{
                                                    background: colors.sidebarBg,
                                                    borderColor: colors.border,
                                                    color: colors.gold
                                                }}
                                                className="hover:border-opacity-80"
                                            >
                                                测试连接
                                            </Button>
                                            <span className="text-sm" style={{ color: colors.textSecondary }}>
                                                保存设置后再测试连接
                                            </span>
                                        </div>
                                    </Form.Item>
                                </div>
                            </div>

                            {/* 路径配置 */}
                            <div className="mb-8 pt-8 border-t" style={{ borderColor: colors.border }}>
                                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ color: colors.goldLight }}>
                                    <span className="w-1 h-5 rounded-full" style={{ background: colors.gold }}></span>
                                    路径配置
                                </h3>
                                <div className="space-y-4">
                                    <Form.Item
                                        label={<span style={{ color: colors.text }}>转移模式</span>}
                                        name={'trans_mode'}
                                        tooltip={'手动或自动转移使用的转移模式'}
                                    >
                                        <Select className="custom-select-dark">
                                            {TransModeOptions.map(i => (<Select.Option key={i.value} value={i.value}>{i.name}</Select.Option>))}
                                        </Select>
                                    </Form.Item>
                                    <div className="grid grid-cols-2 gap-4">
                                        <Form.Item
                                            label={<span style={{ color: colors.text }}>下载路径</span>}
                                            name={'download_path'}
                                            tooltip={'将下载路径对应到系统路径，解决下载器和系统下载路径不一致的问题'}
                                        >
                                            <Input
                                                style={{
                                                    background: colors.bgDark,
                                                    borderColor: colors.border,
                                                    color: colors.text
                                                }}
                                                className="hover:border-opacity-50 focus:shadow-sm"
                                                placeholder="/downloads"
                                            />
                                        </Form.Item>
                                        <Form.Item label={<span style={{ color: colors.text }}>对应路径</span>} name={'mapping_path'}>
                                            <Input
                                                style={{
                                                    background: colors.bgDark,
                                                    borderColor: colors.border,
                                                    color: colors.text
                                                }}
                                                className="hover:border-opacity-50 focus:shadow-sm"
                                                placeholder="/mnt/downloads"
                                            />
                                        </Form.Item>
                                    </div>
                                    <Form.Item
                                        label={<span style={{ color: colors.text }}>默认保存路径</span>}
                                        name={'savepath'}
                                        tooltip={'设置qBittorrent默认保存路径，留空则使用qBittorrent默认设置'}
                                    >
                                        <Input
                                            placeholder={'例如：/downloads/av'}
                                            style={{
                                                background: colors.bgDark,
                                                borderColor: colors.border,
                                                color: colors.text
                                            }}
                                            className="hover:border-opacity-50 focus:shadow-sm"
                                        />
                                    </Form.Item>
                                </div>
                            </div>

                            {/* 自动化选项 */}
                            <div className="mb-8 pt-8 border-t" style={{ borderColor: colors.border }}>
                                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ color: colors.goldLight }}>
                                    <span className="w-1 h-5 rounded-full" style={{ background: colors.gold }}></span>
                                    自动化选项
                                </h3>
                                <div className="grid grid-cols-1 gap-6">
                                    <Form.Item
                                        label={<span style={{ color: colors.text }}>自动转移(Beta)</span>}
                                        name={'trans_auto'}
                                        valuePropName={'checked'}
                                        tooltip={'下载完成后是否自动转移到影片任务'}
                                        className="mb-0"
                                    >
                                        <Switch className="custom-switch-gold" />
                                    </Form.Item>
                                    <Form.Item
                                        label={<span style={{ color: colors.text }}>自动删种(Beta)</span>}
                                        name={'delete_auto'}
                                        valuePropName={'checked'}
                                        tooltip={'整理完成后自动删除种子及数据'}
                                        className="mb-0"
                                    >
                                        <Switch className="custom-switch-gold" />
                                    </Form.Item>
                                    <Form.Item
                                        label={<span style={{ color: colors.text }}>完成后停止做种</span>}
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
                            <div className="mb-8 pt-8 border-t" style={{ borderColor: colors.border }}>
                                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ color: colors.goldLight }}>
                                    <span className="w-1 h-5 rounded-full" style={{ background: colors.gold }}></span>
                                    高级选项
                                </h3>
                                <div className="space-y-4">
                                    <Form.Item
                                        label={<span style={{ color: colors.text }}>任务分类</span>}
                                        name={'category'}
                                        tooltip="只有指定类别的任务会被识别，留空则为所有任务"
                                    >
                                        <Input
                                            placeholder={'留空则为所有任务'}
                                            style={{
                                                background: colors.bgDark,
                                                borderColor: colors.border,
                                                color: colors.text
                                            }}
                                            className="hover:border-opacity-50 focus:shadow-sm"
                                        />
                                    </Form.Item>
                                    <Form.Item
                                        label={<span style={{ color: colors.text }}>订阅Tracker</span>}
                                        name={'tracker_subscribe'}
                                        tooltip={(
                                            <span>通过Tracker订阅链接，自动为任务添加Tracker列表。
                                                <a target='_blank' href={'https://trackerslist.com/'} style={{ color: colors.gold }} className="hover:opacity-80">示例</a>
                                            </span>
                                        )}
                                    >
                                        <Input
                                            placeholder={'请输入Tracker订阅链接'}
                                            style={{
                                                background: colors.bgDark,
                                                borderColor: colors.border,
                                                color: colors.text
                                            }}
                                            className="hover:border-opacity-50 focus:shadow-sm"
                                        />
                                    </Form.Item>
                                </div>
                            </div>

        </SettingsPage>
    )
}
