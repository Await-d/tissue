import {Button, Card, Empty, Input, List, Space, Tag, theme, Tooltip} from "antd";
import {useDebounce, useRequest} from "ahooks";
import * as api from "../../../apis/file.ts";
import React, {useMemo, useState} from "react";
import {FolderViewOutlined, SearchOutlined} from "@ant-design/icons";
import IconButton from "../../../components/IconButton";
import {createFileRoute, Link} from "@tanstack/react-router";
import VideoDetail from "../../../components/VideoDetail";
import './style.css';

const {useToken} = theme

export const Route = createFileRoute('/_index/file/')({
    component: File
})

function File() {

    const {token} = useToken()
    const {data = [], loading, refresh} = useRequest(api.getFiles)
    const [selected, setSelected] = useState<string | undefined>()
    const [keyword, setKeyword] = useState<string>()
    const keywordDebounce = useDebounce(keyword, {wait: 1000})

    const realData = useMemo(() => {
        return data.filter((item: any) => {
            return !keywordDebounce ||
                item.name.indexOf(keywordDebounce) != -1 ||
                item.path.indexOf(keywordDebounce) != -1
        })
    }, [data, keywordDebounce])

    return (
        <div className="file-page-wrapper animate-fade-in">
            <Card 
                title={<span style={{ color: '#f0f0f2', fontSize: 18, fontWeight: 500 }}>文件列表</span>}
                loading={loading}
                className="dark-card"
                style={{
                    background: '#141416',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: 8
                }}
                extra={(
                    <Space.Compact>
                        <Input 
                            value={keyword} 
                            onChange={e => setKeyword(e.target.value)} 
                            placeholder={'搜索文件名或路径'}
                            style={{
                                background: '#1a1a1d',
                                border: '1px solid rgba(255, 255, 255, 0.08)',
                                color: '#f0f0f2'
                            }}
                            className="dark-input"
                        />
                        <Button 
                            icon={<SearchOutlined/>}
                            style={{
                                background: '#1a1a1d',
                                border: '1px solid rgba(255, 255, 255, 0.08)',
                                color: '#d4a852'
                            }}
                        />
                    </Space.Compact>
                )}
            >
                {realData.length > 0 ? (
                    <List 
                        itemLayout="horizontal"
                        dataSource={realData}
                        className="dark-file-list"
                        renderItem={(item: any, index) => (
                            <List.Item 
                                className="dark-file-item"
                                actions={[
                                    <Tooltip title={'整理'}>
                                        <IconButton 
                                            onClick={() => setSelected(`${item.path}/${item.name}`)}
                                            style={{
                                                color: '#d4a852',
                                                transition: 'all 0.3s'
                                            }}
                                            className="file-action-btn"
                                        >
                                            <FolderViewOutlined style={{fontSize: token.sizeLG}}/>
                                        </IconButton>
                                    </Tooltip>
                                ]}
                            >
                                <List.Item.Meta
                                    title={(
                                        <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                            <span style={{ color: '#f0f0f2', fontWeight: 500 }}>{item.name}</span>
                                            <Tag 
                                                style={{
                                                    background: 'rgba(212, 168, 82, 0.12)',
                                                    border: '1px solid rgba(212, 168, 82, 0.25)',
                                                    color: '#e8c780',
                                                    margin: 0
                                                }}
                                            >
                                                {item.size}
                                            </Tag>
                                        </span>
                                    )}
                                    description={(
                                        <span style={{ color: '#a0a0a8', fontSize: 13 }}>{item.path}</span>
                                    )}
                                />
                            </List.Item>
                        )}
                    />
                ) : (
                    <Empty 
                        description={(
                            <span style={{ color: '#a0a0a8' }}>
                                无文件，
                                <Link 
                                    to={'/setting/file'}
                                    style={{ color: '#d4a852' }}
                                >
                                    配置文件
                                </Link>
                            </span>
                        )}
                        style={{
                            padding: '40px 0'
                        }}
                    />
                )}
                <VideoDetail 
                    title={'文件整理'}
                    mode={'file'}
                    width={1100}
                    path={selected}
                    open={!!selected}
                    onCancel={() => setSelected(undefined)}
                    onOk={() => {
                        setSelected(undefined)
                        refresh()
                    }}
                />
            </Card>
        </div>
    )
}
