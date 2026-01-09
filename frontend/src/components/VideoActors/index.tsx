import {Avatar, Dropdown, message, Tooltip} from "antd";
import type {MenuProps} from "antd";
import * as api from "../../apis/video";
import React, {useState} from "react";
import ModifyModal from "./modifyModal";
import {useNavigate} from "@tanstack/react-router";

interface Actor {
    name: string
    thumb?: string
}

interface Props {
    value?: Actor[]
    onChange?: (value?: Actor[]) => void
    readonly?: boolean
}

function VideoActors(props: Props) {

    const {value, onChange, readonly = false} = props
    const [editMode, setEditMode] = useState<string | undefined>(undefined)
    const [selected, setSelected] = useState<number | undefined>(undefined)
    const navigate = useNavigate()

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

    function handleActorClick(actor: Actor, index: number) {
        if (readonly) {
            // Navigate to actor page
            navigate({
                to: '/actor',
                search: {actorName: actor.name}
            })
        } else {
            // Edit mode
            setEditMode('edit')
            setSelected(index)
        }
    }

    function getContextMenu(actor: Actor): MenuProps {
        return {
            items: [
                {
                    key: 'view',
                    label: '查看演员',
                    onClick: () => {
                        navigate({
                            to: '/actor',
                            search: {actorName: actor.name}
                        })
                    }
                },
                {
                    key: 'search',
                    label: '搜索该演员',
                    onClick: () => {
                        navigate({
                            to: '/search',
                            search: {keyword: actor.name}
                        })
                    }
                }
            ]
        }
    }

    return (
        <>
            <div style={{display: "flex", marginBottom: 5}}>
                <Avatar.Group maxCount={8}>
                    {value?.map((actor: any, index: number) => (
                        <Dropdown
                            key={actor.name}
                            menu={getContextMenu(actor)}
                            trigger={['contextMenu']}
                        >
                            <Tooltip title={actor?.name}>
                                <Avatar style={{cursor: 'pointer'}}
                                        size={"large"}
                                        src={actor?.thumb && api.getVideoCover(actor.thumb)}
                                        onClick={() => handleActorClick(actor, index)}
                                />
                            </Tooltip>
                        </Dropdown>
                    ))}
                    {!readonly && (
                        <Tooltip title={'新增'}>
                            <Avatar style={{cursor: 'pointer'}} size={"large"} onClick={() => {
                                setEditMode('add')
                                setSelected(undefined)
                            }}>+</Avatar>
                        </Tooltip>
                    )}
                </Avatar.Group>
            </div>
            {!readonly && (
                <ModifyModal data={(selected != undefined && value) && value[selected]}
                             open={!!editMode}
                             onOk={onSave}
                             onCancel={() => setEditMode(undefined)}
                             onDelete={onDelete}
                />
            )}
        </>
    )
}

export default VideoActors
