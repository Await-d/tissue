/*
 * @Author: Await
 * @Date: 2025-05-24 17:05:38
 * @LastEditors: Await
 * @LastEditTime: 2025-01-09 20:30:00
 * @Description: User Management with Enhanced UI
 */
import { Card, App, Table, Input, Select, Space, Row, Col, Statistic, Avatar, Tag, Popconfirm, Empty, Tooltip } from "antd";
import { ColumnsType } from "antd/lib/table";
import React, { useMemo, useState } from "react";
import {
    PlusOutlined,
    SearchOutlined,
    UserOutlined,
    CrownOutlined,
    TeamOutlined,
    ClockCircleOutlined,
    EditOutlined,
    DeleteOutlined,
    KeyOutlined
} from "@ant-design/icons";
import UserModal from "./userModal.tsx";
import * as api from "../../../../apis/user";
import { useAntdTable } from "ahooks";
import IconButton from "../../../../components/IconButton";
import { useFormModal } from "../../../../utils/useFormModal.ts";

const { Search } = Input;

interface UserRecord {
    id: number;
    name: string;
    username: string;
    is_admin: boolean;
    created_at?: string;
    last_login?: string;
}

function UserList() {
    const { message, modal } = App.useApp();
    const [searchText, setSearchText] = useState('');
    const [roleFilter, setRoleFilter] = useState<string>('all');

    const { tableProps, refresh, data } = useAntdTable(api.getUsers);
    const { setOpen, modalProps } = useFormModal({
        service: api.modifyUser,
        onOk: () => {
            message.success("保存成功");
            setOpen(false);
            refresh();
        }
    });

    // Filter users based on search and role
    const filteredData = useMemo(() => {
        if (!data?.list) return [];

        return data.list.filter((user: UserRecord) => {
            const matchSearch = !searchText ||
                user.name?.toLowerCase().includes(searchText.toLowerCase()) ||
                user.username?.toLowerCase().includes(searchText.toLowerCase());

            const matchRole = roleFilter === 'all' ||
                (roleFilter === 'admin' && user.is_admin) ||
                (roleFilter === 'user' && !user.is_admin);

            return matchSearch && matchRole;
        });
    }, [data?.list, searchText, roleFilter]);

    // Calculate statistics
    const statistics = useMemo(() => {
        const users = data?.list || [];
        const totalUsers = users.length;
        const adminCount = users.filter((u: UserRecord) => u.is_admin).length;
        const regularCount = totalUsers - adminCount;

        return {
            total: totalUsers,
            admin: adminCount,
            regular: regularCount
        };
    }, [data?.list]);

    const handleDelete = (record: UserRecord) => {
        modal.confirm({
            title: '确认删除',
            content: `确定要删除用户 "${record.name}" 吗？此操作不可恢复。`,
            okText: '删除',
            okType: 'danger',
            cancelText: '取消',
            onOk: async () => {
                try {
                    // TODO: Implement delete API
                    message.success('删除成功');
                    refresh();
                } catch (error) {
                    message.error('删除失败');
                }
            }
        });
    };

    const handleResetPassword = (record: UserRecord) => {
        modal.confirm({
            title: '重置密码',
            content: `确定要重置用户 "${record.name}" 的密码吗？`,
            okText: '重置',
            cancelText: '取消',
            onOk: async () => {
                try {
                    // TODO: Implement reset password API
                    message.success('密码已重置');
                } catch (error) {
                    message.error('重置失败');
                }
            }
        });
    };

    const columns: ColumnsType<UserRecord> = [
        {
            title: '用户',
            dataIndex: 'name',
            key: 'name',
            width: 250,
            render: (name, record) => (
                <Space>
                    <Avatar
                        size={40}
                        icon={<UserOutlined />}
                        style={{
                            backgroundColor: record.is_admin ? '#1890ff' : '#87d068',
                            flexShrink: 0
                        }}
                    >
                        {name?.charAt(0)?.toUpperCase()}
                    </Avatar>
                    <div style={{ minWidth: 0 }}>
                        <div style={{
                            fontWeight: 500,
                            fontSize: 14,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                        }}>
                            {name}
                        </div>
                        <div style={{
                            fontSize: 12,
                            color: '#8c8c8c',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                        }}>
                            @{record.username}
                        </div>
                    </div>
                </Space>
            )
        },
        {
            title: '角色',
            dataIndex: 'is_admin',
            key: 'role',
            width: 120,
            render: (is_admin) => (
                <Tag
                    icon={is_admin ? <CrownOutlined /> : <UserOutlined />}
                    color={is_admin ? 'gold' : 'blue'}
                >
                    {is_admin ? '管理员' : '普通用户'}
                </Tag>
            )
        },
        {
            title: '最后登录',
            dataIndex: 'last_login',
            key: 'last_login',
            width: 180,
            render: (last_login) => (
                last_login ? (
                    <Space size={4}>
                        <ClockCircleOutlined style={{ color: '#8c8c8c' }} />
                        <span style={{ fontSize: 13, color: '#595959' }}>
                            {new Date(last_login).toLocaleString('zh-CN')}
                        </span>
                    </Space>
                ) : (
                    <span style={{ color: '#bfbfbf' }}>从未登录</span>
                )
            )
        },
        {
            title: '操作',
            key: 'operations',
            width: 150,
            fixed: 'right',
            render: (_, record) => (
                !record.is_admin && (
                    <Space size={8}>
                        <Tooltip title="编辑">
                            <IconButton onClick={() => setOpen(true, record)}>
                                <EditOutlined style={{ fontSize: 16, color: '#1890ff' }} />
                            </IconButton>
                        </Tooltip>
                        <Tooltip title="重置密码">
                            <IconButton onClick={() => handleResetPassword(record)}>
                                <KeyOutlined style={{ fontSize: 16, color: '#faad14' }} />
                            </IconButton>
                        </Tooltip>
                        <Tooltip title="删除">
                            <Popconfirm
                                title="确认删除此用户？"
                                onConfirm={() => handleDelete(record)}
                                okText="删除"
                                cancelText="取消"
                                okButtonProps={{ danger: true }}
                            >
                                <IconButton>
                                    <DeleteOutlined style={{ fontSize: 16, color: '#ff4d4f' }} />
                                </IconButton>
                            </Popconfirm>
                        </Tooltip>
                    </Space>
                )
            )
        }
    ];

    return (
        <Card
            title={
                <Space>
                    <TeamOutlined />
                    <span>用户管理</span>
                </Space>
            }
            extra={(
                <IconButton onClick={() => setOpen(true)}>
                    <PlusOutlined style={{ fontSize: 16 }} />
                </IconButton>
            )}
        >
            {/* Statistics Panel */}
            <Row gutter={16} style={{ marginBottom: 24 }}>
                <Col xs={24} sm={8}>
                    <Card bordered={false} style={{ background: '#f0f5ff' }}>
                        <Statistic
                            title="总用户数"
                            value={statistics.total}
                            prefix={<TeamOutlined />}
                            valueStyle={{ color: '#1890ff' }}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={8}>
                    <Card bordered={false} style={{ background: '#fffbe6' }}>
                        <Statistic
                            title="管理员"
                            value={statistics.admin}
                            prefix={<CrownOutlined />}
                            valueStyle={{ color: '#faad14' }}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={8}>
                    <Card bordered={false} style={{ background: '#f6ffed' }}>
                        <Statistic
                            title="普通用户"
                            value={statistics.regular}
                            prefix={<UserOutlined />}
                            valueStyle={{ color: '#52c41a' }}
                        />
                    </Card>
                </Col>
            </Row>

            {/* Search and Filter */}
            <Space style={{ marginBottom: 16, width: '100%' }} direction="vertical" size={12}>
                <Row gutter={12}>
                    <Col xs={24} sm={16} md={18}>
                        <Search
                            placeholder="搜索用户名或姓名"
                            allowClear
                            enterButton={<SearchOutlined />}
                            size="large"
                            value={searchText}
                            onChange={(e) => setSearchText(e.target.value)}
                            onSearch={setSearchText}
                        />
                    </Col>
                    <Col xs={24} sm={8} md={6}>
                        <Select
                            size="large"
                            style={{ width: '100%' }}
                            value={roleFilter}
                            onChange={setRoleFilter}
                            options={[
                                { label: '全部角色', value: 'all' },
                                { label: '管理员', value: 'admin' },
                                { label: '普通用户', value: 'user' }
                            ]}
                        />
                    </Col>
                </Row>
            </Space>

            {/* User Table */}
            <Table
                rowKey="id"
                columns={columns}
                {...tableProps}
                dataSource={filteredData}
                pagination={{
                    ...tableProps.pagination,
                    showSizeChanger: true,
                    showTotal: (total) => `共 ${total} 个用户`,
                    pageSizeOptions: ['10', '20', '50', '100']
                }}
                locale={{
                    emptyText: (
                        <Empty
                            image={Empty.PRESENTED_IMAGE_SIMPLE}
                            description={
                                searchText || roleFilter !== 'all'
                                    ? '没有找到匹配的用户'
                                    : '暂无用户数据'
                            }
                        />
                    )
                }}
                scroll={{ x: 800 }}
            />

            <UserModal {...modalProps} />
        </Card>
    );
}

export default UserList;
