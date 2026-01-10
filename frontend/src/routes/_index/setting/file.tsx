import {Button, Form, Input, message, Select, Skeleton} from "antd";
import * as api from "../../../apis/setting.ts";
import {useRequest} from "ahooks";
import {createFileRoute} from "@tanstack/react-router";
import {TransModeOptions} from "../../../utils/constants.ts";
import {useThemeColors} from "../../../hooks/useThemeColors";


export const Route = createFileRoute('/_index/setting/file')({
    component: SettingFile
})

function SettingFile(props: { data?: any }) {
    const colors = useThemeColors()
    const [form] = Form.useForm()

    const {loading} = useRequest(api.getSettings, {
        onSuccess: (res) => {
            form.setFieldsValue(res.file)
        }
    })

    const {run, loading: saving} = useRequest(api.saveSetting, {
        manual: true,
        onSuccess: () => {
            message.success("设置成功")
        }
    })

    function onFinish(data: any) {
        run('file', data)
    }

    return (
        loading ? (
            <Skeleton active/>
        ) : (
            <div className="max-w-5xl mx-auto px-6 py-8">
                <div className="rounded-2xl shadow-2xl overflow-hidden" style={{ backgroundColor: colors.bgContainer, borderColor: colors.borderPrimary, borderWidth: '1px' }}>
                    {/* 页面标题 */}
                    <div className="px-8 py-6 border-b" style={{ borderColor: colors.borderPrimary, backgroundImage: `linear-gradient(to right, ${colors.bgElevated}, ${colors.bgContainer})` }}>
                        <h2 className="text-2xl font-bold flex items-center gap-3" style={{ color: colors.goldPrimary }}>
                            <span className="w-1.5 h-8 rounded-full" style={{ backgroundImage: `linear-gradient(to bottom, ${colors.goldPrimary}, ${colors.goldDark})` }}></span>
                            文件设置
                        </h2>
                        <p className="text-sm mt-2 ml-6" style={{ color: colors.textSecondary }}>配置文件路径和转移模式</p>
                    </div>

                    <div className="p-8">
                        <Form layout={'vertical'} form={form} onFinish={onFinish}>
                            <div className="mb-8">
                                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ color: colors.goldLight }}>
                                    <span className="w-1 h-5 rounded-full" style={{ backgroundColor: colors.goldPrimary }}></span>
                                    文件配置
                                </h3>
                                <div className="space-y-4">
                                    <Form.Item label={<span style={{ color: colors.textPrimary }}>文件路径</span>} name={'path'}>
                                        <Input
                                            style={{
                                                backgroundColor: colors.bgElevated,
                                                borderColor: colors.borderPrimary,
                                                color: colors.textPrimary
                                            }}
                                            onMouseEnter={(e) => {
                                                (e.target as HTMLInputElement).style.borderColor = colors.rgba('gold', 0.5)
                                            }}
                                            onMouseLeave={(e) => {
                                                (e.target as HTMLInputElement).style.borderColor = colors.borderPrimary
                                            }}
                                            onFocus={(e) => {
                                                (e.target as HTMLInputElement).style.borderColor = colors.goldPrimary;
                                                (e.target as HTMLInputElement).style.boxShadow = `0 0 0 2px ${colors.rgba('gold', 0.1)}`
                                            }}
                                            onBlur={(e) => {
                                                (e.target as HTMLInputElement).style.borderColor = colors.borderPrimary;
                                                (e.target as HTMLInputElement).style.boxShadow = 'none'
                                            }}
                                            placeholder="/path/to/files"
                                        />
                                    </Form.Item>
                                    <Form.Item label={<span style={{ color: colors.textPrimary }}>转移模式</span>} name={'trans_mode'}>
                                        <Select className="custom-select-dark">
                                            {TransModeOptions.map(i => (<Select.Option key={i.value}>{i.name}</Select.Option>))}
                                        </Select>
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
                                        width: '192px',
                                        height: '44px',
                                        backgroundImage: `linear-gradient(to right, ${colors.goldPrimary}, ${colors.goldDark})`,
                                        borderWidth: 0,
                                        color: colors.bgBase,
                                        fontWeight: 'bold',
                                        boxShadow: `0 8px 16px ${colors.goldPrimary}30`
                                    }}
                                    onMouseEnter={(e) => {
                                        (e.target as HTMLElement).style.backgroundImage = `linear-gradient(to right, ${colors.goldLight}, ${colors.goldPrimary})`
                                        ;(e.target as HTMLElement).style.boxShadow = `0 8px 16px ${colors.goldPrimary}50`
                                    }}
                                    onMouseLeave={(e) => {
                                        (e.target as HTMLElement).style.backgroundImage = `linear-gradient(to right, ${colors.goldPrimary}, ${colors.goldDark})`
                                        ;(e.target as HTMLElement).style.boxShadow = `0 8px 16px ${colors.goldPrimary}30`
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

