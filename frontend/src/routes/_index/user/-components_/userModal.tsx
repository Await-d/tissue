import React from "react";
import {Form, Input, Modal} from "antd";
import {FormModalProps} from "../../../../utils/useFormModal.ts";

function UserModal(props: FormModalProps) {

    const {form, initValues, ...otherProps} = props

    const id = initValues?.id

    return (
        <Modal
            title={id ? '编辑用户' : '新建用户'}
            {...otherProps}
        >
            <Form layout={'vertical'} form={form}>
                <Form.Item name={'name'} label={'名称'} rules={[{required: true, message: '请输入名称'}]}>
                    <Input/>
                </Form.Item>
                <Form.Item name={'username'} label={'用户名'} rules={[{required: true, message: '请输入用户名'}]}>
                    <Input/>
                </Form.Item>
                <Form.Item name={'password'} label={'新密码'} rules={[{required: !id, message: '请输入密码'}]}>
                    <Input.Password/>
                </Form.Item>
                <Form.Item name={'confirmPassword'} label={'确认新密码'} dependencies={['password']} rules={[
                    {required: !id, message: '请再次输入密码'},
                    ({getFieldValue}) => ({
                        validator(_, value) {
                            if (!value || getFieldValue('password') === value) {
                                return Promise.resolve()
                            }
                            return Promise.reject(new Error('两次输入的密码不一致'))
                        }
                    })
                ]}>
                    <Input.Password/>
                </Form.Item>
            </Form>
        </Modal>
    )
}

export default UserModal
