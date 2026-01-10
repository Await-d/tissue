import {Button, Card, Col, Form, Input, message, Row} from "antd";
import {useDispatch, useSelector} from "react-redux";
import {Dispatch, RootState} from "../../../../models";
import {useEffect} from "react";
import {useRequest} from "ahooks";
import * as api from "../../../../apis/user";


function UserInfo() {

    const [form] = Form.useForm()
    const {userInfo} = useSelector((state: RootState) => state.auth)
    const {getInfo} = useDispatch<Dispatch>().auth


    const {run: onSubmit, loading: onSubmitting} = useRequest(api.modifyUser, {
        manual: true,
        onSuccess: () => {
            getInfo()
            message.success('保存成功')
        }
    })

    useEffect(() => {
        if (userInfo) {
            form.setFieldsValue(userInfo)
        }
    }, [userInfo])

    function onFinish(values: any) {
        if (values.password && values.password !== values.confirmPassword) {
            return message.error("两次输入密码不一致")
        }
        onSubmit({...values, id: userInfo.id})
    }

    return (
        <>
            <style>{`
                .user-info-card .ant-card {
                    background: #1a1a1d;
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                }

                .user-info-card .ant-card-head {
                    background: #222226;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                }

                .user-info-card .ant-card-head-title {
                    color: #f0f0f2;
                    font-weight: 600;
                }

                .user-info-card .ant-form-item-label > label {
                    color: #f0f0f2;
                    font-weight: 500;
                }

                .user-info-card .ant-input,
                .user-info-card .ant-input-password {
                    background: #141416;
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    color: #f0f0f2;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .user-info-card .ant-input:hover,
                .user-info-card .ant-input-password:hover {
                    border-color: rgba(212, 168, 82, 0.4);
                }

                .user-info-card .ant-input:focus,
                .user-info-card .ant-input-password:focus,
                .user-info-card .ant-input-focused {
                    border-color: #d4a852;
                    box-shadow: 0 0 0 2px rgba(212, 168, 82, 0.15);
                }

                .user-info-card .ant-input::placeholder {
                    color: #6a6a72;
                }

                .user-info-card .ant-input-password .ant-input {
                    background: transparent;
                    border: none;
                }

                .user-info-card .ant-input-suffix {
                    color: #a0a0a8;
                }

                .user-info-card .ant-btn-primary {
                    background: #d4a852;
                    border-color: #d4a852;
                    color: #0d0d0f;
                    font-weight: 600;
                    height: 40px;
                    padding: 0 32px;
                    box-shadow: 0 2px 8px rgba(212, 168, 82, 0.3);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .user-info-card .ant-btn-primary:hover {
                    background: #e8c780 !important;
                    border-color: #e8c780 !important;
                    box-shadow: 0 4px 12px rgba(212, 168, 82, 0.4) !important;
                    transform: translateY(-2px);
                }

                .user-info-card .ant-btn-primary:active {
                    transform: translateY(0);
                }

                .user-info-card .ant-form-item-explain-error {
                    color: #ff4d4f;
                }
            `}</style>
            <Card 
                title={'用户信息'}
                className="user-info-card"
                style={{
                    background: '#1a1a1d',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)'
                }}
                styles={{
                    header: {
                        background: '#222226',
                        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
                        color: '#f0f0f2'
                    }
                }}
            >
                <Form form={form} layout={'vertical'} onFinish={onFinish}>
                    <Row gutter={20}>
                        <Col span={24} lg={12}>
                            <Form.Item name={'name'} label={'名称'} rules={[{required: true, message: '请输入名称'}]}>
                                <Input/>
                            </Form.Item>
                        </Col>
                        <Col span={24} lg={12}>
                            <Form.Item name={'username'} label={'用户名'}
                                       rules={[{required: true, message: '请输入用户名'}]}>
                                <Input/>
                            </Form.Item> </Col>
                        <Col span={24} lg={12}>
                            <Form.Item name={'password'} label={'新密码'}>
                                <Input.Password/>
                            </Form.Item> </Col>
                        <Col span={24} lg={12}>
                            <Form.Item name={'confirmPassword'} label={'确认新密码'}>
                                <Input.Password/>
                            </Form.Item>
                        </Col>
                    </Row>
                    <Button type={'primary'} htmlType={'submit'} loading={onSubmitting}>保存</Button>
                </Form>
            </Card>
        </>
    )
}

export default UserInfo
