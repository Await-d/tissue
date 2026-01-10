/*
 * @Author: Await
 * @Date: 2025-05-25 00:03:41
 * @LastEditors: Await
 * @LastEditTime: 2025-05-25 00:11:06
 * @Description: 请填写简介
 */
import React from "react";
import { Button } from "antd";
import { SearchOutlined } from "@ant-design/icons";
import { createFileRoute, useSearch, Link } from "@tanstack/react-router";
import WebActorSearch from '../../../components/ActorSearch/WebActorSearch';
import './styles.css';

export const Route = createFileRoute('/_index/actor/')({
    component: ActorSearch,
    loaderDeps: ({ search }) => search as any,
})

export function ActorSearch() {
    const search: any = useSearch({ from: '/_index/actor/' });

    return (
        <div className="actor-page-container">
            <div className="actor-main-card">
                <div className="actor-card-header">
                    <h1 className="actor-card-title">
                        演员搜索
                    </h1>
                    <Link to="/search">
                        <button className="actor-search-button">
                            <SearchOutlined />
                            <span>番号搜索</span>
                        </button>
                    </Link>
                </div>
                <div className="actor-card-body">
                    <WebActorSearch
                        defaultSearchValue={search?.actorName || ""}
                    />
                </div>
            </div>
        </div>
    );
}