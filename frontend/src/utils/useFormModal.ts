import { useState } from "react";
import { Form, FormInstance, ModalProps } from "antd";

interface Params {
    service: ((...args: any[]) => Promise<any>)
    onOk: (data: any) => void
    transform?: (values: any) => any
}

export interface FormModalProps extends ModalProps {
    form?: FormInstance
    initValues?: any
}

export function useFormModal(params: Params) {

    const [open, setModalOpen] = useState(false)
    const [values, setValues] = useState<any>({})
    const [formInstance] = Form.useForm()
    const [confirmLoading, setConfirmLoading] = useState(false)

    function setOpen(isOpen: boolean, records?: any) {
        setValues(records)
        if (isOpen) {
            formInstance.resetFields()
        }
        if (records) {
            formInstance.setFieldsValue(records)
        }
        setModalOpen(isOpen)
    }

    async function onOk() {
        try {
            setConfirmLoading(true)
            const formData = await formInstance.validateFields()
            const data = { ...values, ...formData }
            const payload = params.transform ? params.transform(data) : data

            const service = params.service(payload)
            const response = await service
            params.onOk(response.data)
            setValues({})
            formInstance.resetFields()
        } catch (_e) {

        } finally {
            setConfirmLoading(false)
        }
    }

    function onCancel() {
        setModalOpen(false)
        setValues({})
        formInstance.resetFields()
    }

    return {
        modalProps: {
            open,
            onOk,
            onCancel,
            confirmLoading,
            initValues: values,
            form: formInstance,
        },
        form: formInstance,
        open,
        setOpen,
    }
}
