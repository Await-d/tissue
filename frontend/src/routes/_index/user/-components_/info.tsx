import {Button, Card, Col, Form, Input, message, Row} from "antd";
import {useDispatch, useSelector} from "react-redux";
import {Dispatch, RootState} from "../../../../models";
import {useEffect} from "react";
import {useRequest} from "ahooks";
import * as api from "../../../../apis/user";
import { useThemeColors } from '../../../../hooks/useThemeColors';


function UserInfo() {

    const [form] = Form.useForm()
    const {userInfo} = useSelector((state: RootState) => state.auth)
    const {getInfo} = useDispatch<Dispatch>().auth
    const colors = useThemeColors()


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
                    background: ${colors.bgContainer};
                    border: 1px solid ${colors.borderPrimary};
                    box-shadow: ${colors.shadowSm};
                }

                .user-info-card .ant-card-head {
                    background: ${colors.bgSpotlight};
                    border-bottom: 1px solid ${colors.borderPrimary};
                }

                .user-info-card .ant-card-head-title {
                    color: ${colors.textPrimary};
                    font-weight: 600;
                }

                .user-info-card .ant-form-item-label > label {
                    color: ${colors.textPrimary};
                    font-weight: 500;
                }

                .user-info-card .ant-input,
                .user-info-card .ant-input-password {
                    background: ${colors.bgElevated};
                    border: 1px solid ${colors.borderPrimary};
                    color: ${colors.textPrimary};
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .user-info-card .ant-input:hover,
                .user-info-card .ant-input-password:hover {
                    border-color: ${colors.rgba('gold', 0.4)};
                }

                .user-info-card .ant-input:focus,
                .user-info-card .ant-input-password:focus,
                .user-info-card .ant-input-focused {
                    border-color: ${colors.goldPrimary};
                    box-shadow: 0 0 0 2px ${colors.rgba('gold', 0.15)};
                }

                .user-info-card .ant-input::placeholder {
                    color: ${colors.textTertiary};
                }

                .user-info-card .ant-input-password .ant-input {
                    background: transparent;
                    border: none;
                }

                .user-info-card .ant-input-suffix {
                    color: ${colors.textSecondary};
                }

                .user-info-card .ant-btn-primary {
                    background: ${colors.goldPrimary};
                    border-color: ${colors.goldPrimary};
                    color: ${colors.bgBase};
                    font-weight: 600;
                    height: 40px;
                    padding: 0 32px;
                    box-shadow: ${colors.shadowGold};
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .user-info-card .ant-btn-primary:hover {
                    background: ${colors.goldLight} !important;
                    border-color: ${colors.goldLight} !important;
                    box-shadow: 0 4px 12px ${colors.rgba('gold', 0.4)} !important;
                    transform: translateY(-2px);
                }

                .user-info-card .ant-btn-primary:active {
                    transform: translateY(0);
                }

                .user-info-card .ant-form-item-explain-error {
                    color: ${colors.error};
                }
            `}</style>
            <Card
                title={'用户信息'}
                className="user-info-card"
                style={{
                    background: colors.bgContainer,
                    border: `1px solid ${colors.borderPrimary}`,
                    boxShadow: colors.shadowSm
                }}
                styles={{
                    header: {
                        background: colors.bgSpotlight,
                        borderBottom: `1px solid ${colors.borderPrimary}`,
                        color: colors.textPrimary
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
