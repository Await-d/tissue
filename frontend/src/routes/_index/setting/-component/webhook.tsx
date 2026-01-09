import {Form, Input, Space} from "antd";
import {LinkOutlined, InfoCircleOutlined} from "@ant-design/icons";

function Webhook() {
    return (
        <>
            <Form.Item
                name={'url'}
                label={
                    <Space>
                        <LinkOutlined />
                        <span>Webhook URL</span>
                    </Space>
                }
                tooltip={{
                    title: "接收通知的 Webhook 接口地址",
                    icon: <InfoCircleOutlined />
                }}
            >
                <Input
                    placeholder="例如: https://your-domain.com/webhook"
                    size="large"
                />
            </Form.Item>

            {/* 说明信息 */}
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mt-4">
                <div className="flex items-start gap-2">
                    <InfoCircleOutlined className="text-purple-500 mt-1" />
                    <div className="text-sm text-gray-700">
                        <p className="font-medium mb-2">Webhook 说明：</p>
                        <ul className="list-disc list-inside space-y-1 text-gray-600">
                            <li>系统将通过 POST 请求发送通知到指定 URL</li>
                            <li>请求体格式为 JSON，包含通知的详细信息</li>
                            <li>确保 Webhook 接口可以正常访问</li>
                            <li>建议配置 HTTPS 以保证数据安全</li>
                        </ul>
                        <div className="mt-3 bg-white border border-purple-200 rounded p-2">
                            <p className="text-xs font-medium mb-1">请求示例：</p>
                            <pre className="text-xs text-gray-600 overflow-x-auto">
{`{
  "type": "notification",
  "title": "任务完成",
  "message": "视频整理完成",
  "timestamp": "2026-01-09T12:00:00Z"
}`}
                            </pre>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
}

export default Webhook
