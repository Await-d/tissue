import {Button, Card, Form, Input, message, Select, Skeleton, Space, Switch, Divider} from "antd";
import * as api from "../../../apis/setting.ts";
import {useRequest} from "ahooks";
import {createFileRoute} from "@tanstack/react-router";
import {TransModeOptions} from "../../../utils/constants.ts";
import {
    CloudDownloadOutlined,
    UserOutlined,
    LockOutlined,
    FolderOutlined,
    SwapOutlined,
    ThunderboltOutlined,
    DeleteOutlined,
    TagOutlined,
    LinkOutlined,
    InfoCircleOutlined,
    ReloadOutlined,
    SaveOutlined,
    ApiOutlined,
    CheckCircleOutlined
} from "@ant-design/icons";

export const Route = createFileRoute('/_index/setting/download')({
    component: SettingDownload
})

function SettingDownload() {
    const [form] = Form.useForm()

    const {loading, data: settingsData} = useRequest(api.getSettings, {
        onSuccess: (res) => {
            form.setFieldsValue(res.download)
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

    // 测试qBittorrent连接
    const {run: testConnection, loading: testing} = useRequest(api.testQBittorrentConnection, {
        manual: true,
        onSuccess: (res) => {
            if (res.data.status) {
                message.success(res.data.data.message);
            } else {
                message.error(res.data.message);
            }
        },
        onError: (err) => {
            message.error("测试连接失败：" + (err.message || "未知错误"));
        }
    });

    function onFinish(data: any) {
        run('download', data)
    }

    function handleReset() {
        if (settingsData?.download) {
            form.setFieldsValue(settingsData.download)
            message.info("已重置为当前保存的值")
        }
    }

    return (
        loading ? (
            <Skeleton active/>
        ) : (
            <div className={'w-[800px] max-w-full my-0 mx-auto px-4'}>
                <Form layout={'vertical'} form={form} onFinish={onFinish}>
                    {/* qBittorrent 连接配置 */}
                    <Card
                        title={
                            <Space>
                                <ApiOutlined />
                                <span>qBittorrent 连接</span>
                            </Space>
                        }
                        className="mb-6 shadow-sm"
                    >
                        <Form.Item
                            label={
                                <Space>
                                    <CloudDownloadOutlined />
                                    <span>服务器地址</span>
                                </Space>
                            }
                            name={'host'}
                            tooltip={{
                                title: "qBittorrent Web UI 的访问地址",
                                icon: <InfoCircleOutlined />
                            }}
                        >
                            <Input placeholder="例如: http://localhost:8080" />
                        </Form.Item>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <Form.Item
                                label={
                                    <Space>
                                        <UserOutlined />
                                        <span>用户名</span>
                                    </Space>
                                }
                                name={'username'}
                            >
                                <Input placeholder="admin" />
                            </Form.Item>

                            <Form.Item
                                label={
                                    <Space>
                                        <LockOutlined />
                                        <span>密码</span>
                                    </Space>
                                }
                                name={'password'}
                            >
                                <Input.Password autoComplete={'new-password'} placeholder="请输入密码" />
                            </Form.Item>
                        </div>

                        <Form.Item
                            label={
                                <Space>
                                    <CheckCircleOutlined />
                                    <span>测试连接</span>
                                </Space>
                            }
                        >
                            <Space>
                                <Button
                                    type="default"
                                    loading={testing}
                                    onClick={() => testConnection()}
                                >
                                    测试连接
                                </Button>
                                <span className="text-gray-400 text-sm">
                                    (保存设置后再测试连接)
                                </span>
                            </Space>
                        </Form.Item>
                    </Card>

                    {/* 路径配置 */}
                    <Card
                        title={
                            <Space>
                                <FolderOutlined />
                                <span>路径配置</span>
                            </Space>
                        }
                        className="mb-6 shadow-sm"
                    >
                        <Form.Item
                            label={
                                <Space>
                                    <FolderOutlined />
                                    <span>下载路径</span>
                                </Space>
                            }
                            name={'download_path'}
                            tooltip={{
                                title: "qBittorrent 中配置的下载路径",
                                icon: <InfoCircleOutlined />
                            }}
                        >
                            <Input placeholder="例如: /downloads" />
                        </Form.Item>

                        <Form.Item
                            label={
                                <Space>
                                    <SwapOutlined />
                                    <span>对应路径</span>
                                </Space>
                            }
                            name={'mapping_path'}
                            tooltip={{
                                title: "系统中实际的下载路径，用于路径映射",
                                icon: <InfoCircleOutlined />
                            }}
                        >
                            <Input placeholder="例如: /mnt/downloads" />
                        </Form.Item>

                        <Form.Item
                            label={
                                <Space>
                                    <FolderOutlined />
                                    <span>默认保存路径</span>
                                </Space>
                            }
                            name={'savepath'}
                            tooltip={{
                                title: "设置qBittorrent默认保存路径，留空则使用qBittorrent默认设置",
                                icon: <InfoCircleOutlined />
                            }}
                        >
                            <Input placeholder="例如: /downloads/av" />
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
                                title: "手动或自动转移时使用的文件转移模式",
                                icon: <InfoCircleOutlined />
                            }}
                        >
                            <Select placeholder="请选择转移模式">
                                {TransModeOptions.map(i => (
                                    <Select.Option key={i.value} value={i.value}>
                                        {i.name}
                                    </Select.Option>
                                ))}
                            </Select>
                        </Form.Item>
                    </Card>

                    {/* 自动化配置 */}
                    <Card
                        title={
                            <Space>
                                <ThunderboltOutlined />
                                <span>自动化配置</span>
                            </Space>
                        }
                        className="mb-6 shadow-sm"
                    >
                        <div className="space-y-4">
                            <Form.Item
                                label={
                                    <Space>
                                        <ThunderboltOutlined />
                                        <span>自动转移</span>
                                    </Space>
                                }
                                name={'trans_auto'}
                                valuePropName={'checked'}
                                tooltip={{
                                    title: "下载完成后自动转移到影片任务（Beta 功能）",
                                    icon: <InfoCircleOutlined />
                                }}
                            >
                                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
                            </Form.Item>

                            <Divider className="my-4" />

                            <Form.Item
                                label={
                                    <Space>
                                        <DeleteOutlined />
                                        <span>自动删种</span>
                                    </Space>
                                }
                                name={'delete_auto'}
                                valuePropName={'checked'}
                                tooltip={{
                                    title: "整理完成后自动删除种子及数据（Beta 功能）",
                                    icon: <InfoCircleOutlined />
                                }}
                            >
                                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
                            </Form.Item>
                        </div>
                    </Card>

                    {/* 高级配置 */}
                    <Card
                        title={
                            <Space>
                                <TagOutlined />
                                <span>高级配置</span>
                            </Space>
                        }
                        className="mb-6 shadow-sm"
                    >
                        <Form.Item
                            label={
                                <Space>
                                    <TagOutlined />
                                    <span>任务分类</span>
                                </Space>
                            }
                            name={'category'}
                            tooltip={{
                                title: "只识别指定类别的下载任务，留空则识别所有任务",
                                icon: <InfoCircleOutlined />
                            }}
                        >
                            <Input placeholder={'留空则为所有任务'} />
                        </Form.Item>

                        <Form.Item
                            label={
                                <Space>
                                    <LinkOutlined />
                                    <span>Tracker 订阅</span>
                                </Space>
                            }
                            name={'tracker_subscribe'}
                            tooltip={{
                                title: (
                                    <span>
                                        通过 Tracker 订阅链接，自动为任务添加 Tracker 列表。
                                        <a
                                            target='_blank'
                                            href={'https://trackerslist.com/'}
                                            className="text-blue-400 hover:text-blue-300 ml-1"
                                        >
                                            查看示例
                                        </a>
                                    </span>
                                ),
                                icon: <InfoCircleOutlined />
                            }}
                        >
                            <Input placeholder={'请输入 Tracker 订阅链接'} />
                        </Form.Item>
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
