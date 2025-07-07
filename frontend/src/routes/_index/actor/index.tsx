/*
 * @Author: Await
 * @Date: 2025-05-25 00:03:41
 * @LastEditors: Await
 * @LastEditTime: 2025-05-25 00:11:06
 * @Description: 请填写简介
 */
import React from "react";
import { Button, Card, Col, Row } from "antd";
import { SearchOutlined } from "@ant-design/icons";
import { createFileRoute, useSearch, Link } from "@tanstack/react-router";
import WebActorSearch from '../../../components/ActorSearch/WebActorSearch';

export const Route = createFileRoute('/_index/actor/')({
    component: ActorSearch,
    loaderDeps: ({ search }) => search as any,
})

export function ActorSearch() {
    const search: any = useSearch({ from: '/_index/actor/' });

    return (
        <Row gutter={[15, 15]}>
            <Col span={24}>
                <Card
                    title="演员搜索"
                    extra={
                        <Link to="/search">
                            <Button type="primary" icon={<SearchOutlined />}>
                                番号搜索
                            </Button>
                        </Link>
                    }
                >
                    <WebActorSearch
                        defaultSearchValue={search?.actorName || ""}
                    />
                </Card>
            </Col>
        </Row>
    );
} 