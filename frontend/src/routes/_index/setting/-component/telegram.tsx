import {Form, Input, Space} from "antd";
import {KeyOutlined, MessageOutlined, InfoCircleOutlined} from "@ant-design/icons";

function Telegram() {
    return (
        <>
            <Form.Item
                name={'telegram_token'}
                label={
                    <Space>
                        <KeyOutlined />
                        <span>Bot Token</span>
                    </Space>
                }
                tooltip={{
                    title: "从 @BotFather 获取的 Telegram Bot Token",
                    icon: <InfoCircleOutlined />
                }}
            >
                <Input
                    placeholder="例如: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
                    size="large"
                />
            </Form.Item>
            <Form.Item
                name={'telegram_chat_id'}
                label={
                    <Space>
                        <MessageOutlined />
                        <span>Chat ID</span>
                    </Space>
                }
                tooltip={{
                    title: "接收消息的 Telegram Chat ID，可以是个人或群组 ID",
                    icon: <InfoCircleOutlined />
                }}
            >
                <Input
                    placeholder="例如: 123456789"
                    size="large"
                />
            </Form.Item>

            {/* 说明信息 */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mt-4">
                <div className="flex items-start gap-2">
                    <InfoCircleOutlined className="text-green-500 mt-1" />
                    <div className="text-sm text-gray-700">
                        <p className="font-medium mb-2">配置步骤：</p>
                        <ol className="list-decimal list-inside space-y-1 text-gray-600">
                            <li>在 Telegram 中搜索 <strong>@BotFather</strong></li>
                            <li>发送 <code className="bg-gray-200 px-1 rounded">/newbot</code> 创建新机器人</li>
                            <li>按提示设置机器人名称，获取 Token</li>
                            <li>搜索 <strong>@userinfobot</strong> 获取你的 Chat ID</li>
                            <li>将 Token 和 Chat ID 填入上方表单</li>
                        </ol>
                    </div>
                </div>
            </div>
        </>
    )
}

export default Telegram
