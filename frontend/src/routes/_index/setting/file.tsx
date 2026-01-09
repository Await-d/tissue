import {Button, Card, Form, Input, message, Select, Skeleton, Space} from "antd";
import * as api from "../../../apis/setting.ts";
import {useRequest} from "ahooks";
import {createFileRoute} from "@tanstack/react-router";
import {TransModeOptions} from "../../../utils/constants.ts";
import {
    FolderOutlined,
    SwapOutlined,
    InfoCircleOutlined,
    ReloadOutlined,
    SaveOutlined,
    FileOutlined
} from "@ant-design/icons";

export const Route = createFileRoute('/_index/setting/file')({
    component: SettingFile
})

function SettingFile() {
    const [form] = Form.useForm()

    const {loading, data: settingsData} = useRequest(api.getSettings, {
        onSuccess: (res) => {
            form.setFieldsValue(res.file)
        }
    })

    const {run, loading: saving} = useRequest(api.saveSetting, {
        manual: true,
        onSuccess: () => {
            message.success("设置保存成功")
        },
        onError: (error) => {
            message.error(`保存失败: ${error.message}`)
        }
    })

    function onFinish(data: any) {
        run('file', data)
    }

    function handleReset() {
        if (settingsData?.file) {
            form.setFieldsValue(settingsData.file)
            message.info("已重置为当前保存的值")
        }
    }

    return (
        loading ? (
            <Skeleton active/>
        ) : (
            <div className={'w-[800px] max-w-full my-0 mx-auto px-4'}>
                <Form layout={'vertical'} form={form} onFinish={onFinish}>
                    {/* 文件配置 */}
                    <Card
                        title={
                            <Space>
                                <FileOutlined />
                                <span>文件管理配置</span>
                            </Space>
                        }
                        className="mb-6 shadow-sm"
                        extra={
                            <span className="text-sm text-gray-500">
                                配置文件整理相关参数
                            </span>
                        }
                    >
                        <Form.Item
                            label={
                                <Space>
                                    <FolderOutlined />
                                    <span>文件路径</span>
                                </Space>
                            }
                            name={'path'}
                            tooltip={{
                                title: "需要整理的文件所在的根目录路径",
                                icon: <InfoCircleOutlined />
                            }}
                        >
                            <Input
                                placeholder="例如: /media/files"
                                size="large"
                            />
                        </Form.Item>

                        <Form.Item
                            label={
                                <Space>
                                    <SwapOutlined />
                                    <span>转移模式</span>
                                </Space>
                            }
                            name={'trans_mode'}
                            tooltip={{
                                title: "文件整理时使用的转移模式，不同模式对原文件的处理方式不同",
                                icon: <InfoCircleOutlined />
                            }}
                        >
                            <Select
                                placeholder="请选择转移模式"
                                size="large"
                            >
                                {TransModeOptions.map(i => (
                                    <Select.Option key={i.value} value={i.value}>
                                        <Space>
                                            <SwapOutlined />
                                            <span>{i.name}</span>
                                        </Space>
                                    </Select.Option>
                                ))}
                            </Select>
                        </Form.Item>

                        {/* 说明信息 */}
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
                            <div className="flex items-start gap-2">
                                <InfoCircleOutlined className="text-blue-500 mt-1" />
                                <div className="text-sm text-gray-700">
                                    <p className="font-medium mb-2">转移模式说明：</p>
                                    <ul className="list-disc list-inside space-y-1 text-gray-600">
                                        <li><strong>复制</strong>：保留原文件，复制到目标位置</li>
                                        <li><strong>移动</strong>：将文件移动到目标位置，删除原文件</li>
                                        <li><strong>硬链接</strong>：创建硬链接，节省磁盘空间（需要同一文件系统）</li>
                                        <li><strong>软链接</strong>：创建符号链接，指向原文件</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </Card>

                    {/* 操作按钮 */}
                    <div className="flex justify-center gap-4 pb-6">
                        <Button
                            icon={<ReloadOutlined />}
                            onClick={handleReset}
                            disabled={saving}
                        >
                            重置
                        </Button>
                        <Button
                            type={'primary'}
                            icon={<SaveOutlined />}
                            loading={saving}
                            htmlType={"submit"}
                            size="large"
                            className="min-w-[150px]"
                        >
                            保存设置
                        </Button>
                    </div>
                </Form>
            </div>
        )
    )
}
