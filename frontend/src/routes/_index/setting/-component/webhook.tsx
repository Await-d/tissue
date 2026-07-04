import {Form, Input} from "antd";

function Webhook() {
    return (
        <>
            <Form.Item name={'url'} label="URL">
                <Input
                    placeholder="输入 Webhook URL"
                />
            </Form.Item>
        </>
    )
}

export default Webhook
