/*
 * @Author: Await
 * @Date: 2025-05-23 20:29:27
 * @LastEditors: Await
 * @LastEditTime: 2025-05-23 21:39:26
 * @Description: 请填写简介
 */
import { Space } from "antd";
import UserInfo from "./-components_/info.tsx";
import UserList from "./-components_/user.tsx";
import { useSelector } from "react-redux";
import { RootState } from "../../../models";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute('/_index/user/')({
    component: User
})

function User() {

    const { userInfo } = useSelector((state: RootState) => state.auth)

    return (
        <Space direction={'vertical'} style={{ width: '100%' }}>
            <UserInfo />
            {userInfo?.is_admin && (
                <UserList />
            )}
        </Space>
    )
}

