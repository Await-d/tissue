/*
 * @Author: Await
 * @Date: 2025-05-24 17:05:38
 * @LastEditors: Await
 * @LastEditTime: 2025-05-26 18:01:49
 * @Description: 请填写简介
 */
import { Card, App, Table } from "antd";
import { ColumnsType } from "antd/lib/table";
import React from "react";
import { PlusOutlined } from "@ant-design/icons";
import UserModal from "./userModal.tsx";
import * as api from "../../../../apis/user";
import { useAntdTable } from "ahooks";
import More from "../../../../components/More";
import IconButton from "../../../../components/IconButton";
import { useFormModal } from "../../../../utils/useFormModal.ts";

function UserList() {
    const { message } = App.useApp();
    const { tableProps, refresh } = useAntdTable(api.getUsers)
    const { setOpen, modalProps, form } = useFormModal({
        service: api.modifyUser,
        onOk: () => {
            message.success("保存成功")
            setOpen(false)
            refresh()
        }
    })

    const columns: ColumnsType<any> = [
        {
            title: '名称',
            dataIndex: 'name',
        },
        {
            title: '用户名',
            dataIndex: 'username',
        },
        {
            title: '管理员',
            dataIndex: 'is_admin',
            render: (is_admin) => is_admin ? '是' : '否'
        },
        {
            title: '',
            dataIndex: 'operations',
            width: 20,
            render: (_, record) => (
                !record.is_admin && (
                    <More onClick={(key) => onMoreClick(key, record)} />
                )
            )
        }
    ]

    function onMoreClick(key: string, record: any) {
        if (key === 'edit') {
            setOpen(true, record)
        }
    }

    return (
        <>
            <style>{`
                .user-list-card .ant-card {
                    background: #1a1a1d;
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                }

                .user-list-card .ant-card-head {
                    background: #222226;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                }

                .user-list-card .ant-card-head-title {
                    color: #f0f0f2;
                    font-weight: 600;
                }

                .user-list-card .ant-card-extra {
                    padding: 0;
                }

                .user-list-card .ant-table {
                    background: transparent;
                }

                .user-list-card .ant-table-thead > tr > th {
                    background: #222226;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                    color: #f0f0f2;
                    font-weight: 600;
                    padding: 16px;
                }

                .user-list-card .ant-table-tbody > tr {
                    background: transparent;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .user-list-card .ant-table-tbody > tr > td {
                    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
                    color: #a0a0a8;
                    padding: 16px;
                }

                .user-list-card .ant-table-tbody > tr:hover {
                    background: rgba(212, 168, 82, 0.08) !important;
                }

                .user-list-card .ant-table-tbody > tr:hover > td {
                    color: #f0f0f2;
                    border-bottom-color: rgba(212, 168, 82, 0.15);
                }

                .user-list-card .ant-table-tbody > tr:last-child > td {
                    border-bottom: none;
                }

                .user-list-card .icon-button {
                    width: 32px;
                    height: 32px;
                    border-radius: 6px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: #d4a852;
                    color: #0d0d0f;
                    border: none;
                    cursor: pointer;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    box-shadow: 0 2px 6px rgba(212, 168, 82, 0.3);
                }

                .user-list-card .icon-button:hover {
                    background: #e8c780;
                    box-shadow: 0 4px 12px rgba(212, 168, 82, 0.4);
                    transform: translateY(-2px);
                }

                .user-list-card .icon-button:active {
                    transform: translateY(0);
                }

                .user-list-card .ant-table-placeholder .ant-table-cell {
                    background: transparent;
                    border: none;
                }

                .user-list-card .ant-empty-description {
                    color: #6a6a72;
                }
            `}</style>
            <Card 
                title={'用户管理'} 
                extra={(
                    <IconButton onClick={() => setOpen(true)}>
                        <PlusOutlined />
                    </IconButton>
                )}
                className="user-list-card"
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
                    },
                    body: {
                        padding: 0
                    }
                }}
            >
                <Table rowKey={'id'} columns={columns} {...tableProps} pagination={false} />
                <UserModal form={form} {...modalProps} />
            </Card>
        </>
    )
}

export default UserList
