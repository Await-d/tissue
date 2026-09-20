import {Form, Input, Select} from "antd";
import {createFileRoute} from "@tanstack/react-router";
import {TransModeOptions} from "../../../utils/constants.ts";
import {useThemeColors} from "../../../hooks/useThemeColors";
import {SettingsPage} from "./-component/SettingsPage";
import {useSectionSettings} from "./-context/SettingsContext";


export const Route = createFileRoute('/_index/setting/file')({
    component: SettingFile
})

function SettingFile(_props: { data?: any }) {
    const colors = useThemeColors()
    const {form, loading, saving, submit} = useSectionSettings('file')

    return (
        <SettingsPage
            title="文件设置"
            subtitle="配置文件路径和转移模式"
            loading={loading}
            form={form}
            onFinish={submit}
            saving={saving}
            maxWidth="5xl"
            headerGradient="elevated"
            cardBorder="none"
            saveButtonVariant="file"
        >
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
                            {TransModeOptions.map(i => (<Select.Option key={i.value} value={i.value}>{i.name}</Select.Option>))}
                        </Select>
                    </Form.Item>
                </div>
            </div>
        </SettingsPage>
    )
}
