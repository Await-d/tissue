import {Form, Input} from "antd";

function Telegram() {
    return (
        <>
            <Form.Item name={'telegram_token'} label="Token">
                <Input
                    placeholder="输入 Telegram Bot Token"
                />
            </Form.Item>
            <Form.Item name={'telegram_chat_id'} label="Chat ID">
                <Input
                    placeholder="输入 Chat ID"
                />
            </Form.Item>
        </>
    )
}

export default Telegram
