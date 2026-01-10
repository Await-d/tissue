import React, { useState, useEffect } from 'react';
import { AutoComplete, Input, Avatar, Spin, Empty, List, Card, Button, App, FloatButton } from 'antd';
import { SearchOutlined, UserOutlined, ReloadOutlined } from '@ant-design/icons';
import * as api from '../../apis/video';
import { LazyLoadImage } from 'react-lazy-load-image-component';
import 'react-lazy-load-image-component/src/effects/blur.css';
import { useRequest } from 'ahooks';
import { useThemeColors } from '../../hooks/useThemeColors';
import './actorSearchStyles.css';

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
    const { message } = App.useApp();
    const colors = useThemeColors();
    const [searchValue, setSearchValue] = useState('');
    const [searchResults, setSearchResults] = useState<Video[]>([]);
    const [searching, setSearching] = useState(false);
    const [selectedActor, setSelectedActor] = useState<Actor | null>(null);

    // 使用useRequest获取演员列表
    const { data: actors = [], loading, refresh: refreshActors } = useRequest(() => api.getAllActors(true), {
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
        <div className="web-actor-container">
            {/* 搜索栏区域 */}
            <div style={{ display: 'flex', marginBottom: '20px', gap: '12px' }}>
                <AutoComplete
                    popupMatchSelectWidth={400}
                    style={{ width: '100%' }}
                    options={options}
                    onSelect={handleSelect}
                    onSearch={handleSearch}
                    value={searchValue}
                    notFoundContent={loading ? <Spin size="small" /> : null}
                    popupClassName="web-actor-search-dropdown"
                >
                    <Input
                        size="large"
                        placeholder="搜索本地演员..."
                        prefix={<SearchOutlined style={{ color: colors.textSecondary, fontSize: '16px' }} />}
                        onPressEnter={() => performSearch(searchValue)}
                        allowClear
                        suffix={
                            <Button
                                type="primary"
                                size="small"
                                icon={<SearchOutlined />}
                                onClick={() => performSearch(searchValue)}
                                style={{
                                    background: `linear-gradient(135deg, ${colors.gold} 0%, ${colors.goldLight} 100%)`,
                                    borderColor: colors.gold,
                                    transition: 'all 0.3s ease',
                                    height: '32px',
                                    padding: '0 16px',
                                    borderRadius: '6px',
                                    fontWeight: 600,
                                    color: colors.dark
                                }}
                            />
                        }
                        className="web-actor-search-input"
                    />
                </AutoComplete>
                <Button
                    icon={<ReloadOutlined />}
                    onClick={handleReload}
                    size="large"
                    style={{
                        background: colors.bgSecondary,
                        border: `1px solid ${colors.borderColor}`,
                        color: colors.gold,
                        transition: 'all 0.3s ease',
                        borderRadius: '10px',
                        width: '52px'
                    }}
                    className="actor-reload-btn"
                />
            </div>

            {/* 选中演员信息 */}
            {selectedActor && (
                <div className="web-actor-selected-card">
                    <div className="web-actor-avatar-wrapper" style={{ padding: '6px' }}>
                        <Avatar
                            size={80}
                            icon={<UserOutlined />}
                            src={selectedActor.thumb ? api.getVideoCover(selectedActor.thumb) : undefined}
                            style={{
                                border: `4px solid ${colors.bgTertiary}`,
                                background: colors.bgSecondary
                            }}
                        />
                    </div>
                    <h2 style={{
                        marginTop: 16,
                        color: colors.text,
                        fontSize: '24px',
                        fontWeight: 600,
                        letterSpacing: '0.5px'
                    }}>{selectedActor.name}</h2>
                    {searchResults.length > 0 && (
                        <div className="web-actor-stats">
                            <div className="web-actor-stat-item">
                                <div className="web-actor-stat-label">作品数量</div>
                                <div className="web-actor-stat-value">{searchResults.length}</div>
                            </div>
                            <div className="web-actor-stat-item">
                                <div className="web-actor-stat-label">中文字幕</div>
                                <div className="web-actor-stat-value">
                                    {searchResults.filter((v: Video) => v.is_zh).length}
                                </div>
                            </div>
                            <div className="web-actor-stat-item">
                                <div className="web-actor-stat-label">无码作品</div>
                                <div className="web-actor-stat-value">
                                    {searchResults.filter((v: Video) => v.is_uncensored).length}
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* 加载状态 */}
            {searching ? (
                <div className="web-actor-loading">
                    <Spin tip={<span style={{ color: colors.textSecondary, marginTop: '12px', display: 'block' }}>搜索中...</span>} />
                </div>
            ) : searchResults.length > 0 ? (
                <List
                    grid={{ gutter: [20, 20], xs: 1, sm: 2, md: 3, lg: 4, xl: 4, xxl: 5 }}
                    dataSource={searchResults}
                    renderItem={(video: Video) => (
                        <List.Item>
                            <Card
                                hoverable
                                className="web-actor-video-card"
                                cover={
                                    video.cover ? (
                                        <div style={{
                                            height: 200,
                                            overflow: 'hidden',
                                            background: colors.dark,
                                            position: 'relative'
                                        }}>
                                            <LazyLoadImage
                                                alt={video.title}
                                                height={200}
                                                src={api.getVideoCover(video.cover)}
                                                width="100%"
                                                effect="blur"
                                                style={{
                                                    objectFit: 'cover',
                                                    transition: 'transform 0.4s ease'
                                                }}
                                            />
                                        </div>
                                    ) : (
                                        <div style={{
                                            height: 200,
                                            background: colors.dark,
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            color: colors.textTertiary
                                        }}>
                                            无封面
                                        </div>
                                    )
                                }
                                onClick={() => onVideoSelect && onVideoSelect(video)}
                                style={{
                                    background: colors.bgSecondary,
                                    border: `1px solid ${colors.borderColor}`,
                                    borderRadius: '16px',
                                    overflow: 'hidden',
                                    transition: 'all 0.3s ease'
                                }}
                            >
                                <Card.Meta
                                    title={<span style={{ color: colors.text, fontSize: '14px' }}>{video.title}</span>}
                                    description={
                                        <div style={{ marginTop: '8px' }}>
                                            {video.is_zh && (
                                                <span className="web-actor-badge web-actor-badge-zh" style={{ marginRight: 8 }}>
                                                    中文
                                                </span>
                                            )}
                                            {video.is_uncensored && (
                                                <span className="web-actor-badge web-actor-badge-uncensored">
                                                    无码
                                                </span>
                                            )}
                                        </div>
                                    }
                                    style={{
                                        background: colors.bgSecondary
                                    }}
                                />
                            </Card>
                        </List.Item>
                    )}
                />
            ) : selectedActor && (
                <div className="web-actor-empty">
                    <Empty description={<span style={{ color: colors.textSecondary }}>没有找到相关视频</span>} />
                </div>
            )}

            <FloatButton
                icon={<ReloadOutlined />}
                onClick={handleReload}
                className="web-actor-float-btn"
                style={{
                    right: 24,
                    bottom: 24,
                    background: `linear-gradient(135deg, ${colors.gold} 0%, ${colors.goldLight} 100%)`,
                    color: colors.dark
                }}
            />
        </div>
    );
};

export default ActorSearch; 