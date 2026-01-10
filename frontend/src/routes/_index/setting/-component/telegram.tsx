import {Form, Input} from "antd";

function Telegram() {
    return (
        <>
            <Form.Item name={'telegram_token'} label={<span className="text-[#f0f0f2]">Token</span>}>
                <Input
                    className="bg-[#0d0d0f] border-white/8 text-[#f0f0f2] hover:border-[#d4a852]/50 focus:border-[#d4a852] focus:shadow-[0_0_0_2px_rgba(212,168,82,0.1)]"
                    placeholder="输入 Telegram Bot Token"
                />
            </Form.Item>
            <Form.Item name={'telegram_chat_id'} label={<span className="text-[#f0f0f2]">Chat ID</span>}>
                <Input
                    className="bg-[#0d0d0f] border-white/8 text-[#f0f0f2] hover:border-[#d4a852]/50 focus:border-[#d4a852] focus:shadow-[0_0_0_2px_rgba(212,168,82,0.1)]"
                    placeholder="输入 Chat ID"
                />
            </Form.Item>
        </>
    )
}

export default Telegram
