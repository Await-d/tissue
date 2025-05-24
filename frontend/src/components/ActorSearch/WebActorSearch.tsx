import React, { useState, useEffect } from 'react';
import { AutoComplete, Input, Avatar, Spin, Empty, List, Card, Tabs, message, Modal, Radio, Space } from 'antd';
import { SearchOutlined, UserOutlined } from '@ant-design/icons';
import * as api from '../../apis/video';
import { LazyLoadImage } from 'react-lazy-load-image-component';
import 'react-lazy-load-image-component/src/effects/blur.css';
import { useRequest } from 'ahooks';
import VideoCover from "../VideoCover";
import { useNavigate } from "@tanstack/react-router";

interface WebActor {
    name: string;
    thumb?: string;
    url?: string;
    id?: string; // 添加id字段用于唯一标识
}

interface WebVideo {
    title: string;
    num: string;
    url: string;
    cover?: string;
    is_zh: boolean;
    is_uncensored: boolean;
    rank?: number;
    publish_date?: string;
}

interface WebActorSearchProps {
    onVideoSelect?: (video: WebVideo) => void;
}

const WebActorSearch: React.FC<WebActorSearchProps> = ({ onVideoSelect }) => {
    const [searchValue, setSearchValue] = useState('');
    const [selectedActor, setSelectedActor] = useState<WebActor | null>(null);
    const [sourceType, setSourceType] = useState<string>('javdb');
    const [modal, setModal] = useState<{ visible: boolean, video: WebVideo | null }>({
        visible: false,
        video: null
    });
    const navigate = useNavigate();

    // 获取热门演员列表
    const { data: actorsData = [], loading: loadingActors, refresh: refreshActors } = useRequest(
        () => api.getWebActors(sourceType),
        {
            refreshDeps: [sourceType],
            onError: (error) => {
                console.error('Failed to fetch actors from web:', error);
                message.error('获取网站演员列表失败');
            }
        }
    );

    // 处理演员数据，确保每个演员有唯一ID
    const actors = React.useMemo(() => {
        return actorsData.map((actor: WebActor, index: number) => ({
            ...actor,
            id: actor.url ? actor.url.split('/').pop() : `actor-${index}-${actor.name}`,
        }));
    }, [actorsData]);

    useEffect(() => {
        console.log('获取到演员列表数据:', actors);
    }, [actors]);

    // 搜索演员
    const { run: searchActor, data: searchResultsData = [], loading: searching } = useRequest(
        (actorName: string) => api.searchWebActor(actorName, sourceType),
        {
            manual: true,
            onError: (error) => {
                console.error('Failed to search actors:', error);
                message.error('搜索演员失败');
            },
            onSuccess: (data) => {
                console.log('搜索到演员数据:', data);
            }
        }
    );

    // 处理搜索结果，确保唯一ID
    const searchResults = React.useMemo(() => {
        return searchResultsData.map((actor: WebActor, index: number) => ({
            ...actor,
            id: actor.url ? actor.url.split('/').pop() : `search-${index}-${actor.name}`,
        }));
    }, [searchResultsData]);

    // 获取演员视频
    const { run: fetchActorVideos, data: actorVideos = [], loading: loadingVideos } = useRequest(
        (actorName: string) => api.getWebActorVideos(actorName, sourceType),
        {
            manual: true,
            onError: (error) => {
                console.error('Failed to fetch actor videos:', error);
                message.error('获取演员视频失败');
            },
            onSuccess: (data) => {
                console.log('获取到演员视频数据:', data);
                if (data && data.length === 0) {
                    message.info('没有找到该演员的视频');
                }
            }
        }
    );

    const handleSearch = (value: string) => {
        setSearchValue(value);
        if (value.trim().length > 1) {
            searchActor(value);
        } else if (value.trim().length === 0) {
            // 当搜索框清空时，清除搜索结果
            setSelectedActor(null);
        }
    };

    const handleSelect = (value: string) => {
        const actor = [...actors, ...searchResults].find(a => a.name === value);
        if (actor) {
            setSelectedActor(actor);
            fetchActorVideos(actor.name);
        }
    };

    const handleVideoSelect = (video: WebVideo) => {
        if (onVideoSelect) {
            onVideoSelect(video);
        } else {
            // 检查num是否为日期格式
            const isDateFormat = /^\d{4}-\d{2}-\d{2}$/.test(video.num);
            let videoNum = video.num;

            // 如果是日期格式，从URL中提取实际番号
            if (isDateFormat && video.url) {
                const urlParts = video.url.split('/');
                const lastPart = urlParts[urlParts.length - 1];
                if (lastPart && lastPart.length > 0) {
                    videoNum = lastPart;
                }
            }

            navigate({
                to: '/home/detail',
                search: {
                    source: sourceType.charAt(0).toUpperCase() + sourceType.slice(1),
                    num: videoNum,
                    url: video.url
                }
            });
        }
    };

    const handleSourceChange = (e: any) => {
        setSourceType(e.target.value);
        setSelectedActor(null);
        setSearchValue('');
    };

    // 构建下拉选项
    const options = React.useMemo(() => {
        // 去重逻辑：如果有多个相同name的演员，使用额外的信息（如URL或自生成ID）确保唯一性
        const nameCountMap: { [key: string]: number } = {};

        return [...actors, ...searchResults]
            .filter((actor: WebActor) => actor.name && (
                !searchValue.trim() || actor.name.toLowerCase().includes(searchValue.toLowerCase())
            ))
            .map((actor: WebActor) => {
                // 为每个演员的名字计数
                if (!nameCountMap[actor.name]) {
                    nameCountMap[actor.name] = 1;
                } else {
                    nameCountMap[actor.name]++;
                }

                // 为相同名字的演员生成唯一key
                const count = nameCountMap[actor.name];
                const uniqueKey = count > 1
                    ? `${actor.id || actor.name}-${count}`
                    : actor.id || actor.name;

                return {
                    value: actor.name,
                    key: uniqueKey,
                    label: (
                        <div style={{ display: 'flex', alignItems: 'center' }}>
                            <Avatar
                                size="small"
                                icon={<UserOutlined />}
                                src={actor.thumb ? api.getVideoCover(actor.thumb) : undefined}
                                style={{ marginRight: 8 }}
                            />
                            {actor.name}
                        </div>
                    ),
                };
            })
            .slice(0, 10); // 限制下拉框选项数量，但在下方会完整显示所有搜索结果
    }, [actors, searchResults, searchValue]);

    // 生成带有唯一key的演员列表
    const generateActorsWithUniqueKeys = (actorList: WebActor[]) => {
        const nameCountMap: { [key: string]: number } = {};

        return actorList.map((actor: WebActor) => {
            // 为每个演员的名字计数
            if (!nameCountMap[actor.name]) {
                nameCountMap[actor.name] = 1;
            } else {
                nameCountMap[actor.name]++;
            }

            // 为相同名字的演员生成唯一key
            const count = nameCountMap[actor.name];
            const uniqueKey = count > 1
                ? `${actor.id || actor.name}-${count}`
                : actor.id || actor.name;

            return {
                ...actor,
                uniqueKey
            };
        });
    };

    // 预先计算带有唯一key的演员列表
    const actorsWithUniqueKeys = React.useMemo(() => {
        return generateActorsWithUniqueKeys(actors);
    }, [actors]);

    // 预先计算带有唯一key的搜索结果
    const searchResultsWithUniqueKeys = React.useMemo(() => {
        return generateActorsWithUniqueKeys(searchResults);
    }, [searchResults]);

    // 显示热门演员列表
    const renderActorsList = () => {
        if (loadingActors) {
            return (
                <div style={{ textAlign: 'center', margin: '32px 0' }}>
                    <Spin />
                    <div style={{ marginTop: 8 }}>加载中...</div>
                </div>
            );
        }

        if (!actors || actors.length === 0) {
            return <Empty description="没有找到演员列表" />;
        }

        return (
            <div style={{ marginTop: '16px' }}>
                <h3>热门演员</h3>
                <List
                    grid={{ gutter: 16, xs: 2, sm: 3, md: 4, lg: 6, xl: 8, xxl: 10 }}
                    dataSource={actorsWithUniqueKeys}
                    renderItem={(actor: WebActor & { uniqueKey?: string }) => (
                        <List.Item key={actor.uniqueKey || actor.id || `${actor.name}-${Math.random().toString(36).substr(2, 9)}`}>
                            <div
                                style={{ textAlign: 'center', cursor: 'pointer' }}
                                onClick={() => {
                                    setSelectedActor(actor);
                                    setSearchValue(actor.name);
                                    fetchActorVideos(actor.name);
                                }}
                            >
                                <Avatar
                                    size={64}
                                    icon={<UserOutlined />}
                                    src={actor.thumb ? api.getVideoCover(actor.thumb) : undefined}
                                />
                                <div style={{ marginTop: 8 }}>{actor.name}</div>
                            </div>
                        </List.Item>
                    )}
                />
            </div>
        );
    };

    // 显示搜索结果列表
    const renderSearchResults = () => {
        if (searching) {
            return (
                <div style={{ textAlign: 'center', margin: '32px 0' }}>
                    <Spin />
                    <div style={{ marginTop: 8 }}>搜索中...</div>
                </div>
            );
        }

        if (!searchResults || searchResults.length === 0) {
            return <Empty description="没有找到匹配的演员" />;
        }

        return (
            <div style={{ marginTop: '16px' }}>
                <h3>搜索结果 - "{searchValue}" ({searchResults.length})</h3>
                <List
                    grid={{ gutter: 16, xs: 2, sm: 3, md: 4, lg: 6, xl: 8, xxl: 10 }}
                    dataSource={searchResultsWithUniqueKeys}
                    renderItem={(actor: WebActor & { uniqueKey?: string }) => (
                        <List.Item key={actor.uniqueKey || actor.id || `${actor.name}-${Math.random().toString(36).substr(2, 9)}`}>
                            <div
                                style={{ textAlign: 'center', cursor: 'pointer' }}
                                onClick={() => {
                                    setSelectedActor(actor);
                                    setSearchValue(actor.name);
                                    fetchActorVideos(actor.name);
                                }}
                            >
                                <Avatar
                                    size={64}
                                    icon={<UserOutlined />}
                                    src={actor.thumb ? api.getVideoCover(actor.thumb) : undefined}
                                />
                                <div style={{ marginTop: 8 }}>{actor.name}</div>
                            </div>
                        </List.Item>
                    )}
                />
            </div>
        );
    };

    return (
        <div style={{ padding: '16px' }}>
            <Space direction="vertical" style={{ width: '100%', marginBottom: '16px' }}>
                <Radio.Group
                    value={sourceType}
                    onChange={handleSourceChange}
                    optionType="button"
                    buttonStyle="solid"
                    style={{ marginBottom: '16px' }}
                >
                    <Radio.Button value="javdb">JavDB</Radio.Button>
                    <Radio.Button value="javbus">JavBus</Radio.Button>
                </Radio.Group>

                <AutoComplete
                    popupMatchSelectWidth={252}
                    style={{ width: '100%' }}
                    options={options}
                    onSelect={handleSelect}
                    onSearch={handleSearch}
                    value={searchValue}
                    notFoundContent={loadingActors || searching ? <Spin size="small" /> : null}
                >
                    <Input.Search
                        size="large"
                        placeholder={`搜索${sourceType}演员...`}
                        prefix={<SearchOutlined />}
                        onSearch={(value) => {
                            if (value.trim()) {
                                searchActor(value);
                            }
                        }}
                        enterButton
                    />
                </AutoComplete>
            </Space>

            {selectedActor ? (
                // 已选择演员，显示演员详情和视频列表
                <>
                    <div style={{ textAlign: 'center', margin: '16px 0' }}>
                        <Avatar
                            size={64}
                            icon={<UserOutlined />}
                            src={selectedActor.thumb ? api.getVideoCover(selectedActor.thumb) : undefined}
                        />
                        <h2 style={{ marginTop: 8 }}>{selectedActor.name}</h2>
                    </div>

                    {loadingVideos ? (
                        <div style={{ textAlign: 'center', margin: '32px 0' }}>
                            <Spin />
                            <div style={{ marginTop: 8 }}>加载中...</div>
                        </div>
                    ) : actorVideos.length > 0 ? (
                        <List
                            grid={{ gutter: 16, xs: 1, sm: 2, md: 3, lg: 3, xl: 4, xxl: 5 }}
                            dataSource={actorVideos}
                            renderItem={(video: WebVideo, index: number) => (
                                <List.Item key={`${video.num || ''}-${index}-${Math.random().toString(36).substring(2, 7)}`}>
                                    <Card
                                        hoverable
                                        cover={
                                            video.cover ? (
                                                <div style={{ height: 200, overflow: 'hidden' }}>
                                                    <VideoCover src={video.cover} />
                                                </div>
                                            ) : (
                                                <div style={{ height: 200, background: '#f0f0f0', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                                    无封面
                                                </div>
                                            )
                                        }
                                        onClick={() => handleVideoSelect(video)}
                                    >
                                        <Card.Meta
                                            title={
                                                <div style={{
                                                    whiteSpace: 'normal',
                                                    overflow: 'hidden',
                                                    textOverflow: 'ellipsis',
                                                    display: '-webkit-box',
                                                    WebkitLineClamp: 2,
                                                    WebkitBoxOrient: 'vertical',
                                                    lineHeight: '1.3'
                                                }}>
                                                    {video.title || video.num}
                                                </div>
                                            }
                                            description={
                                                <div>
                                                    <div><strong>{video.num}</strong></div>
                                                    <div>
                                                        {video.is_zh && <span style={{ marginRight: 8, color: '#1890ff' }}>中文</span>}
                                                        {video.is_uncensored && <span style={{ color: '#ff4d4f' }}>无码</span>}
                                                        {video.rank && <span style={{ marginLeft: 8 }}>评分: {video.rank}</span>}
                                                    </div>
                                                </div>
                                            }
                                        />
                                    </Card>
                                </List.Item>
                            )}
                        />
                    ) : (
                        <Empty description="没有找到相关视频" />
                    )}
                </>
            ) : searchValue && searchResults.length > 0 ? (
                // 有搜索内容且有搜索结果，显示搜索结果列表
                renderSearchResults()
            ) : (
                // 无搜索内容或无搜索结果，显示热门演员列表
                renderActorsList()
            )}

            <Modal
                title={modal.video?.title || modal.video?.num}
                open={modal.visible}
                footer={null}
                onCancel={() => setModal({ visible: false, video: null })}
                width={800}
            >
                {modal.video && (
                    <div>
                        <div style={{ textAlign: 'center', marginBottom: 20 }}>
                            {modal.video.cover && (
                                <img
                                    src={api.getVideoCover(modal.video.cover)}
                                    alt={modal.video.title || modal.video.num}
                                    style={{ maxWidth: '100%', maxHeight: '400px' }}
                                    onError={(e: any) => {
                                        e.target.onerror = null;
                                        e.target.src = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=';
                                    }}
                                />
                            )}
                        </div>
                        <div>
                            <p><strong>番号:</strong> {modal.video.num}</p>
                            {modal.video.publish_date && <p><strong>发行日期:</strong> {modal.video.publish_date}</p>}
                            {modal.video.rank && <p><strong>评分:</strong> {modal.video.rank}</p>}
                            <p>
                                <strong>特征:</strong>
                                {modal.video.is_zh && <span style={{ marginLeft: 8, color: '#1890ff' }}>中文字幕</span>}
                                {modal.video.is_uncensored && <span style={{ marginLeft: 8, color: '#ff4d4f' }}>无码</span>}
                            </p>
                            <p>
                                <strong>原始链接:</strong>
                                <a href={modal.video.url} target="_blank" rel="noopener noreferrer" style={{ marginLeft: 8 }}>
                                    {modal.video.url}
                                </a>
                            </p>
                        </div>
                    </div>
                )}
            </Modal>
        </div>
    );
};

export default WebActorSearch; 