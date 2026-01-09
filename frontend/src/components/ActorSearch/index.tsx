import React, { useState, useEffect } from 'react';
import { AutoComplete, Input, Avatar, Spin, Empty, List, Card, Button, message, FloatButton } from 'antd';
import { SearchOutlined, UserOutlined, ReloadOutlined } from '@ant-design/icons';
import * as api from '../../apis/video';
import { LazyLoadImage } from 'react-lazy-load-image-component';
import 'react-lazy-load-image-component/src/effects/blur.css';
import { useRequest } from 'ahooks';

interface Actor {
    name: string;
    thumb?: string;
}

interface Video {
    title: string;
    path: string;
    cover?: string;
    is_zh: boolean;
    is_uncensored: boolean;
    actors: Actor[];
}

interface ActorSearchProps {
    onVideoSelect?: (video: Video) => void;
}

const ActorSearch: React.FC<ActorSearchProps> = ({ onVideoSelect }) => {
    const [searchValue, setSearchValue] = useState('');
    const [searchResults, setSearchResults] = useState<Video[]>([]);
    const [searching, setSearching] = useState(false);
    const [selectedActor, setSelectedActor] = useState<Actor | null>(null);

    // 使用useRequest获取演员列表
    const { data: actors = [], loading, refresh: refreshActors } = useRequest<Actor[], []>(() => api.getAllActors(true), {
        onError: (error) => {
            console.error('Failed to fetch actors:', error);
            message.error('获取演员列表失败');
        }
    });

    // 搜索函数，始终使用force=true获取实时数据
    const performSearch = async (value: string) => {
        if (!value.trim()) {
            setSearchResults([]);
            setSelectedActor(null);
            return;
        }

        setSearching(true);
        try {
            // 查找匹配的演员
            const matchedActor = actors.find((a: Actor) =>
                a.name.toLowerCase().includes(value.toLowerCase())
            );

            if (matchedActor) {
                setSelectedActor(matchedActor);
                const results = await api.searchVideosByActor(matchedActor.name, true);
                setSearchResults(results);
                if (results.length === 0) {
                    message.info(`未找到演员"${matchedActor.name}"的相关视频`);
                }
            } else {
                // 直接通过输入的文本搜索
                const results = await api.searchVideosByActor(value, true);
                setSearchResults(results);
                setSelectedActor(null);
                if (results.length === 0) {
                    message.info(`未找到与"${value}"相关的视频`);
                }
            }
        } catch (error) {
            console.error('Failed to search videos:', error);
            message.error('搜索视频失败');
        } finally {
            setSearching(false);
        }
    };

    const handleSearch = (value: string) => {
        setSearchValue(value);
        if (!value) {
            setSearchResults([]);
            setSelectedActor(null);
        }
    };

    const handleSelect = async (value: string, option: any) => {
        setSearchValue(value);
        setSearching(true);
        try {
            const actor = actors.find((a: Actor) => a.name === value);
            setSelectedActor(actor || null);
            // 使用force=true获取实时数据
            const results = await api.searchVideosByActor(value, true);
            setSearchResults(results);
        } catch (error) {
            console.error('Failed to search videos:', error);
            message.error('搜索视频失败');
        } finally {
            setSearching(false);
        }
    };

    const options = actors
        .filter((actor: Actor) => actor.name && actor.name.toLowerCase().includes(searchValue.toLowerCase()))
        .map((actor: Actor) => ({
            value: actor.name,
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
        }));

    const handleReload = () => {
        refreshActors();
        if (searchValue) {
            performSearch(searchValue);
        }
        message.success('数据已刷新');
    };

    return (
        <div style={{ padding: '16px', position: 'relative' }}>
            <div style={{ display: 'flex', marginBottom: '16px' }}>
                <AutoComplete
                    dropdownMatchSelectWidth={252}
                    style={{ width: '100%' }}
                    options={options}
                    onSelect={handleSelect}
                    onSearch={handleSearch}
                    value={searchValue}
                    notFoundContent={loading ? <Spin size="small" /> : null}
                >
                    <Input.Search
                        size="large"
                        placeholder="搜索演员..."
                        prefix={<SearchOutlined />}
                        onPressEnter={() => performSearch(searchValue)}
                        onSearch={() => performSearch(searchValue)}
                        enterButton
                    />
                </AutoComplete>
                <Button
                    icon={<ReloadOutlined />}
                    onClick={handleReload}
                    style={{ marginLeft: '8px' }}
                    size="large"
                />
            </div>

            {selectedActor && (
                <div style={{ textAlign: 'center', margin: '16px 0' }}>
                    <Avatar
                        size={64}
                        icon={<UserOutlined />}
                        src={selectedActor.thumb ? api.getVideoCover(selectedActor.thumb) : undefined}
                    />
                    <h2 style={{ marginTop: 8 }}>{selectedActor.name}</h2>
                </div>
            )}

            {searching ? (
                <div style={{ textAlign: 'center', margin: '32px 0' }}>
                    <Spin tip="搜索中..." />
                </div>
            ) : searchResults.length > 0 ? (
                <List
                    grid={{ gutter: 16, xs: 1, sm: 2, md: 3, lg: 3, xl: 4, xxl: 5 }}
                    dataSource={searchResults}
                    renderItem={(video: Video) => (
                        <List.Item>
                            <Card
                                hoverable
                                cover={
                                    video.cover ? (
                                        <LazyLoadImage
                                            alt={video.title}
                                            height={200}
                                            src={api.getVideoCover(video.cover)}
                                            width="100%"
                                            effect="blur"
                                            style={{ objectFit: 'cover' }}
                                        />
                                    ) : (
                                        <div style={{ height: 200, background: '#f0f0f0', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                            无封面
                                        </div>
                                    )
                                }
                                onClick={() => onVideoSelect && onVideoSelect(video)}
                            >
                                <Card.Meta
                                    title={video.title}
                                    description={
                                        <div>
                                            {video.is_zh && <span style={{ marginRight: 8 }}>中文</span>}
                                            {video.is_uncensored && <span>无码</span>}
                                        </div>
                                    }
                                />
                            </Card>
                        </List.Item>
                    )}
                />
            ) : selectedActor && (
                <Empty description="没有找到相关视频" />
            )}

            <FloatButton
                icon={<ReloadOutlined />}
                onClick={handleReload}
                style={{ right: 24, bottom: 24 }}
            />
        </div>
    );
};

export default ActorSearch; 