import { Avatar, message, Tooltip, Button, Typography, Space } from "antd";
import * as api from "../../apis/video";
import React, { useState } from "react";
import ModifyModal from "./modifyModal";
import { PlusOutlined, EditOutlined } from "@ant-design/icons";

interface Actor {
    name: string
    thumb?: string
}

interface Props {
    value?: Actor[]
    onChange?: (value?: Actor[]) => void
}

function VideoActors(props: Props) {
    const { value, onChange } = props
    const [editMode, setEditMode] = useState<string | undefined>(undefined)
    const [selected, setSelected] = useState<number | undefined>(undefined)

    function onSave(data: any) {
        if (editMode === 'add') {
            if (value?.some((i) => i.name === data.name)) {
                return message.error("该演员已存在")
            }
            onChange?.([...(value || []), data])
        } else if (editMode == 'edit') {
            value!![selected!!] = data
            onChange?.(value && [...value])
        }
        setEditMode(undefined)
        setSelected(undefined)
    }

    function onDelete() {
        onChange?.(value?.filter((_, index) => index != selected))
        setEditMode(undefined)
        setSelected(undefined)
    }

    return (
        <>
            <div style={{ marginBottom: 16 }}>
                <Typography.Title level={5} style={{ marginBottom: 12 }}>
                    演员信息
                </Typography.Title>
                {value && value.length > 0 ? (
                    <Space direction="vertical" style={{ width: '100%' }}>
                        <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
                            {value.map((actor: any, index: number) => (
                                <div
                                    key={actor.name}
                                    style={{
                                        display: 'flex',
                                        flexDirection: 'column',
                                        alignItems: 'center',
                                        position: 'relative'
                                    }}
                                >
                                    <Avatar
                                        style={{
                                            cursor: 'pointer',
                                            border: '2px solid #f0f0f0',
                                            transition: 'all 0.3s'
                                        }}
                                        size={64}
                                        src={actor?.thumb && api.getVideoCover(actor.thumb)}
                                        onClick={() => {
                                            setEditMode('edit')
                                            setSelected(index)
                                        }}
                                    />
                                    <Typography.Text
                                        style={{
                                            marginTop: 4,
                                            maxWidth: 64,
                                            textAlign: 'center',
                                            fontSize: 12
                                        }}
                                        ellipsis={{ tooltip: actor?.name }}
                                    >
                                        {actor?.name}
                                    </Typography.Text>
                                    <Button
                                        size="small"
                                        type="text"
                                        icon={<EditOutlined />}
                                        style={{
                                            position: 'absolute',
                                            top: -8,
                                            right: -8,
                                            background: '#fff',
                                            borderRadius: '50%',
                                            border: '1px solid #f0f0f0',
                                            padding: 0,
                                            height: 24,
                                            width: 24,
                                            display: 'flex',
                                            justifyContent: 'center',
                                            alignItems: 'center'
                                        }}
                                        onClick={() => {
                                            setEditMode('edit')
                                            setSelected(index)
                                        }}
                                    />
                                </div>
                            ))}
                            <div style={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center'
                            }}>
                                <Avatar
                                    style={{
                                        cursor: 'pointer',
                                        backgroundColor: '#fafafa',
                                        border: '1px dashed #d9d9d9',
                                        display: 'flex',
                                        justifyContent: 'center',
                                        alignItems: 'center',
                                        transition: 'all 0.3s',
                                        color: '#999'
                                    }}
                                    size={64}
                                    icon={<PlusOutlined />}
                                    onClick={() => {
                                        setEditMode('add')
                                        setSelected(undefined)
                                    }}
                                />
                                <Typography.Text style={{ marginTop: 4, fontSize: 12 }}>
                                    添加演员
                                </Typography.Text>
                            </div>
                        </div>
                    </Space>
                ) : (
                    <Button
                        icon={<PlusOutlined />}
                        onClick={() => {
                            setEditMode('add')
                            setSelected(undefined)
                        }}
                    >
                        添加演员
                    </Button>
                )}
            </div>
            <ModifyModal
                data={(selected != undefined && value) && value[selected]}
                open={!!editMode}
                onOk={onSave}
                onCancel={() => setEditMode(undefined)}
                onDelete={onDelete}
            />
        </>
    )
}

export default VideoActors
