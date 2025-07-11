import React, { useState, useEffect, useRef } from 'react';
import { AutoComplete, Input, Avatar, Spin, Empty, List, Card, Tabs, message, Modal, Radio, Space, Button, Tooltip, Tag, App, Rate, Select, Checkbox, Row, Col, InputNumber, Switch } from 'antd';
import { SearchOutlined, UserOutlined, CloudDownloadOutlined, RedoOutlined, StarOutlined, StarFilled, CheckCircleFilled, FilterOutlined } from '@ant-design/icons';
import * as api from '../../apis/video';
import * as subscribeApi from '../../apis/subscribe';
import { LazyLoadImage } from 'react-lazy-load-image-component';
import 'react-lazy-load-image-component/src/effects/blur.css';
import { useRequest } from 'ahooks';
import VideoCover from "../VideoCover";
import { useNavigate, useRouter } from "@tanstack/react-router";
import DownloadModal from "../../routes/_index/search/-components/downloadModal";
import DownloadListModal from "../../routes/_index/search/-components/downloadListModal";
import ActorSubscribeModal from '../../routes/_index/actor-subscribe/-components/ActorSubscribeModal';
import LoadingComponent from '@/components/Loading';

// 本地存储的键名
const STORAGE_KEY = 'web_actor_search_state';

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
    rank_count?: number;
}

interface WebActorSearchProps {
    onVideoSelect?: (video: WebVideo) => void;
    defaultSearchValue?: string;
}

// 定义要保存的状态接口
interface SavedState {
    searchValue: string;
    selectedActor: WebActor | null;
    sourceType: string;
    actorVideos?: any[];
}

const WebActorSearch: React.FC<WebActorSearchProps> = ({ onVideoSelect, defaultSearchValue }) => {
    const { message } = App.useApp();
    // 尝试从localStorage获取保存的状态
    const getSavedState = (): SavedState | null => {
        try {
            const savedStateString = localStorage.getItem(STORAGE_KEY);
            if (savedStateString) {
                return JSON.parse(savedStateString);
            }
        } catch (error) {
            console.error('Failed to parse saved state:', error);
        }
        return null;
    };

    const savedState = getSavedState();

    // 使用保存的状态或默认值初始化状态
    const [searchValue, setSearchValue] = useState(defaultSearchValue || savedState?.searchValue || '');
    const [selectedActor, setSelectedActor] = useState<WebActor | null>(savedState?.selectedActor || null);
    const [sourceType, setSourceType] = useState<string>(savedState?.sourceType || 'javdb');
    const [modal, setModal] = useState<{ visible: boolean, video: WebVideo | null }>({
        visible: false,
        video: null
    });
    const [selectedVideo, setSelectedVideo] = useState<any>(null);
    const [selectedDownload, setSelectedDownload] = useState<any>(null);
    const [showDownloadList, setShowDownloadList] = useState(false);
    const [downloadOptions, setDownloadOptions] = useState<any[]>([]);
    const [loadingVideoId, setLoadingVideoId] = useState<string | null>(null);
    const navigate = useNavigate();
    const router = useRouter(); // 添加路由钩子
    const isFirstRender = useRef(true); // 添加首次渲染标记
    const [subscribeModalVisible, setSubscribeModalVisible] = useState(false);
    const [isSubscribed, setIsSubscribed] = useState(false);
    const [checkingSubscription, setCheckingSubscription] = useState(false);
    const [showFilters, setShowFilters] = useState(false);
    const [filters, setFilters] = useState({
        rating: { min: 0, max: 10 },
        year: { min: 1990, max: new Date().getFullYear() },
        showOnlyZh: false,
        showOnlyUncensored: false,
        sortBy: 'date',
        sortOrder: 'desc'
    });
    const [progress, setProgress] = useState({
        total: 0,
        loaded: 0,
        isLoading: false
    });

    // 保存状态到localStorage
    const saveState = () => {
        try {
            const stateToSave: SavedState = {
                searchValue,
                selectedActor,
                sourceType
            };
            localStorage.setItem(STORAGE_KEY, JSON.stringify(stateToSave));
        } catch (error) {
            console.error('Failed to save state:', error);
        }
    };

    // 当关键状态变化时保存状态
    useEffect(() => {
        saveState();
    }, [searchValue, selectedActor, sourceType]);

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
                // 当获取到演员视频数据后，检查该演员是否已被订阅
                if (selectedActor && selectedActor.name) {
                    checkActorSubscription(selectedActor.name);
                }
            }
        }
    );

    // 添加检查演员是否已被订阅的函数
    const checkActorSubscription = async (actorName: string) => {
        if (!actorName) return;

        setCheckingSubscription(true);
        try {
            const subscriptions = await subscribeApi.getActorSubscriptions();
            const isAlreadySubscribed = subscriptions.some(
                (sub: any) => sub.actor_name.toLowerCase() === actorName.toLowerCase()
            );
            setIsSubscribed(isAlreadySubscribed);
            console.log(`演员 ${actorName} 订阅状态:`, isAlreadySubscribed ? '已订阅' : '未订阅');
        } catch (error) {
            console.error('检查演员订阅状态失败:', error);
        } finally {
            setCheckingSubscription(false);
        }
    };

    // 当选中的演员变化时，检查订阅状态
    useEffect(() => {
        if (selectedActor && selectedActor.name) {
            checkActorSubscription(selectedActor.name);
        } else {
            setIsSubscribed(false);
        }
    }, [selectedActor]);

    // 添加下载功能
    const { run: onDownload, loading: onDownloading } = useRequest(subscribeApi.downloadVideos, {
        manual: true,
        onSuccess: () => {
            setSelectedVideo(null);
            setSelectedDownload(null);
            setShowDownloadList(false);
            setDownloadOptions([]);
            return message.success("下载任务创建成功");
        },
        onError: (error) => {
            console.error('下载失败:', error);
            message.error('创建下载任务失败');
        }
    });

    // 初始化时处理默认搜索值或恢复保存的状态
    useEffect(() => {
        if (defaultSearchValue && defaultSearchValue.trim()) {
            // 如果有默认搜索值，优先使用默认搜索值
            setSearchValue(defaultSearchValue);
            searchActor(defaultSearchValue);
        } else if (savedState?.selectedActor && savedState.searchValue) {
            // 如果有保存的演员，恢复之前的状态
            if (savedState.selectedActor.name) {
                fetchActorVideos(savedState.selectedActor.name);
            }
        }
    }, [defaultSearchValue, searchActor, fetchActorVideos]);

    // 当演员列表或搜索结果更新时，尝试匹配默认演员
    useEffect(() => {
        if (defaultSearchValue && defaultSearchValue.trim() && (actors.length > 0 || searchResults.length > 0)) {
            // 如果能在演员列表或搜索结果中找到匹配的演员，自动选中并获取其作品
            const matchedActor =
                [...actors, ...searchResults].find(actor =>
                    actor.name.toLowerCase() === defaultSearchValue.toLowerCase());

            if (matchedActor) {
                setSelectedActor(matchedActor);
                fetchActorVideos(matchedActor.name);
            }
        }
    }, [defaultSearchValue, actors, searchResults, fetchActorVideos]);

    useEffect(() => {
        console.log('获取到演员列表数据:', actors);
    }, [actors]);

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
            // 从URL中提取实际番号作为备用
            let videoNum = video.num;
            if (sourceType.toLowerCase() === 'javbus' && videoNum.match(/^\d{4}-\d{2}-\d{2}$/)) {
                // 如果是JavBus源并且num是日期格式，尝试从URL中提取番号
                const urlMatch = video.url.match(/\/([A-Za-z]+-\d+)$/);
                if (urlMatch && urlMatch[1]) {
                    console.log('从URL中提取番号:', urlMatch[1], '替代日期格式:', video.num);
                    videoNum = urlMatch[1];
                }
            }

            // 根据URL确定正确的source（优先判断URL中的域名）
            let source = 'JavDB'; // 默认为JavDB

            // 如果URL包含javbus，则source一定是JavBus
            if (video.url.includes('javbus')) {
                source = 'JavBus';
                console.log('根据URL设置source为JavBus');
            }
            // 如果URL包含javdb，则source一定是JavDB
            else if (video.url.includes('javdb')) {
                source = 'JavDB';
                console.log('根据URL设置source为JavDB');
            }
            // 如果URL不包含明确域名，则使用当前选择的sourceType
            else {
                source = sourceType.charAt(0).toUpperCase() + sourceType.slice(1);
            }

            navigate({
                to: '/home/detail',
                search: {
                    source: source,
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
            return <LoadingComponent tip="正在加载热门演员..." minHeight={200} />;
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
            return <LoadingComponent tip="正在搜索演员..." minHeight={200} simple />;
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

    // 添加新的函数处理视频下载
    const handleVideoDownload = (video: WebVideo) => {
        // 设置当前视频为加载状态
        const videoId = `${video.num}-${Math.random().toString(36).substring(2, 7)}`;
        setLoadingVideoId(videoId);

        // 显示加载消息
        message.loading({ content: '正在获取下载资源...', key: 'download' });

        // 获取视频的详细信息（包括下载资源）
        api.getVideoDownloads(video.num, sourceType, video.url)
            .then(detailData => {
                // 清除加载状态
                setLoadingVideoId(null);

                if (detailData && detailData.downloads && detailData.downloads.length > 0) {
                    // 如果有多个下载选项，显示下载列表模态框
                    setSelectedVideo(detailData);
                    setDownloadOptions(detailData.downloads);
                    setShowDownloadList(true);
                    message.destroy('download');
                } else {
                    // 如果没有下载选项，只显示提示信息，不显示模态框
                    message.warning({ content: '没有找到可用的下载资源', key: 'download' });
                    // 不再设置selectedVideo和selectedDownload，避免显示空模态框
                }
            })
            .catch(error => {
                // 清除加载状态
                setLoadingVideoId(null);

                console.error('获取下载资源失败:', error);
                message.error({ content: '获取下载资源失败', key: 'download' });
                // 出错时不显示模态框，只显示错误提示
            });
    };

    // 添加新的useEffect，监听路由变化
    useEffect(() => {
        // 如果是首次渲染，标记为已渲染并返回
        if (isFirstRender.current) {
            isFirstRender.current = false;
            return;
        }

        // 如果有选中的演员，自动刷新作品列表
        if (selectedActor && selectedActor.name) {
            console.log('检测到路由变化，自动刷新演员作品列表:', selectedActor.name);
            fetchActorVideos(selectedActor.name);
        }
    }, [router.state.location.pathname, selectedActor, fetchActorVideos]);

    // 处理订阅成功后的回调
    const handleSubscribeSuccess = () => {
        setSubscribeModalVisible(false);
        setIsSubscribed(true);
        message.success(`已成功订阅演员 ${selectedActor?.name}`);
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
                        allowClear
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
                        <h2 style={{ marginTop: 8 }}>
                            {selectedActor.name}
                            {checkingSubscription ? (
                                <Spin size="small" style={{ marginLeft: 8 }} />
                            ) : isSubscribed ? (
                                <Tag color="green" icon={<CheckCircleFilled />} style={{ marginLeft: 8 }}>
                                    已订阅
                                </Tag>
                            ) : null}
                        </h2>

                        {/* 订阅按钮根据订阅状态显示不同样式 */}
                        <Button
                            type={isSubscribed ? "default" : "primary"}
                            icon={isSubscribed ? <StarFilled /> : <StarOutlined />}
                            style={{ marginTop: 8 }}
                            onClick={() => setSubscribeModalVisible(true)}
                        >
                            {isSubscribed ? "修改订阅" : "订阅演员"}
                        </Button>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                        <div>
                            <Button
                                icon={<FilterOutlined />}
                                onClick={() => setShowFilters(!showFilters)}
                                style={{ marginRight: 8 }}
                            >
                                筛选 {showFilters ? '▼' : '▶'}
                            </Button>
                            {actorVideos.length > 0 && (
                                <span style={{ color: '#666', fontSize: '12px' }}>
                                    共找到 {actorVideos.length} 个作品
                                </span>
                            )}
                        </div>
                        <Tooltip title="刷新作品列表">
                            <Button
                                type="primary"
                                icon={<RedoOutlined />}
                                loading={loadingVideos}
                                onClick={() => {
                                    if (selectedActor && selectedActor.name) {
                                        fetchActorVideos(selectedActor.name);
                                        message.info('正在刷新作品列表...');
                                    }
                                }}
                            >
                                刷新
                            </Button>
                        </Tooltip>
                    </div>

                    {showFilters && (
                        <Card size="small" style={{ marginBottom: 16 }}>
                            <Row gutter={[16, 16]}>
                                <Col span={12}>
                                    <div style={{ marginBottom: 8 }}>评分范围</div>
                                    <Row gutter={8}>
                                        <Col span={12}>
                                            <InputNumber
                                                min={0}
                                                max={10}
                                                step={0.1}
                                                value={filters.rating.min}
                                                onChange={(value) => setFilters({
                                                    ...filters,
                                                    rating: { ...filters.rating, min: value || 0 }
                                                })}
                                                placeholder="最低评分"
                                                style={{ width: '100%' }}
                                            />
                                        </Col>
                                        <Col span={12}>
                                            <InputNumber
                                                min={0}
                                                max={10}
                                                step={0.1}
                                                value={filters.rating.max}
                                                onChange={(value) => setFilters({
                                                    ...filters,
                                                    rating: { ...filters.rating, max: value || 10 }
                                                })}
                                                placeholder="最高评分"
                                                style={{ width: '100%' }}
                                            />
                                        </Col>
                                    </Row>
                                </Col>
                                <Col span={12}>
                                    <div style={{ marginBottom: 8 }}>年份范围</div>
                                    <Row gutter={8}>
                                        <Col span={12}>
                                            <InputNumber
                                                min={1990}
                                                max={new Date().getFullYear()}
                                                value={filters.year.min}
                                                onChange={(value) => setFilters({
                                                    ...filters,
                                                    year: { ...filters.year, min: value || 1990 }
                                                })}
                                                placeholder="最早年份"
                                                style={{ width: '100%' }}
                                            />
                                        </Col>
                                        <Col span={12}>
                                            <InputNumber
                                                min={1990}
                                                max={new Date().getFullYear()}
                                                value={filters.year.max}
                                                onChange={(value) => setFilters({
                                                    ...filters,
                                                    year: { ...filters.year, max: value || new Date().getFullYear() }
                                                })}
                                                placeholder="最晚年份"
                                                style={{ width: '100%' }}
                                            />
                                        </Col>
                                    </Row>
                                </Col>
                                <Col span={8}>
                                    <Checkbox
                                        checked={filters.showOnlyZh}
                                        onChange={(e) => setFilters({
                                            ...filters,
                                            showOnlyZh: e.target.checked
                                        })}
                                    >
                                        仅中文字幕
                                    </Checkbox>
                                </Col>
                                <Col span={8}>
                                    <Checkbox
                                        checked={filters.showOnlyUncensored}
                                        onChange={(e) => setFilters({
                                            ...filters,
                                            showOnlyUncensored: e.target.checked
                                        })}
                                    >
                                        仅无码
                                    </Checkbox>
                                </Col>
                                <Col span={8}>
                                    <Select
                                        value={`${filters.sortBy}-${filters.sortOrder}`}
                                        onChange={(value) => {
                                            const [sortBy, sortOrder] = value.split('-');
                                            setFilters({
                                                ...filters,
                                                sortBy,
                                                sortOrder
                                            });
                                        }}
                                        style={{ width: '100%' }}
                                    >
                                        <Select.Option value="date-desc">发布日期 (新→旧)</Select.Option>
                                        <Select.Option value="date-asc">发布日期 (旧→新)</Select.Option>
                                        <Select.Option value="rating-desc">评分 (高→低)</Select.Option>
                                        <Select.Option value="rating-asc">评分 (低→高)</Select.Option>
                                        <Select.Option value="comments-desc">评论数 (多→少)</Select.Option>
                                        <Select.Option value="comments-asc">评论数 (少→多)</Select.Option>
                                    </Select>
                                </Col>
                            </Row>
                        </Card>
                    )}

                    {(() => {
                        // 过滤和排序逻辑
                        const filteredVideos = actorVideos.filter((video: WebVideo) => {
                            // 评分过滤
                            if (video.rank) {
                                if (video.rank < filters.rating.min || video.rank > filters.rating.max) {
                                    return false;
                                }
                            }
                            
                            // 年份过滤
                            if (video.publish_date) {
                                const videoYear = new Date(video.publish_date).getFullYear();
                                if (videoYear < filters.year.min || videoYear > filters.year.max) {
                                    return false;
                                }
                            }
                            
                            // 中文字幕过滤
                            if (filters.showOnlyZh && !video.is_zh) {
                                return false;
                            }
                            
                            // 无码过滤
                            if (filters.showOnlyUncensored && !video.is_uncensored) {
                                return false;
                            }
                            
                            return true;
                        }).sort((a: WebVideo, b: WebVideo) => {
                            // 排序逻辑
                            const { sortBy, sortOrder } = filters;
                            let compareValue = 0;
                            
                            if (sortBy === 'date') {
                                const dateA = new Date(a.publish_date || '1900-01-01');
                                const dateB = new Date(b.publish_date || '1900-01-01');
                                compareValue = dateA.getTime() - dateB.getTime();
                            } else if (sortBy === 'rating') {
                                compareValue = (a.rank || 0) - (b.rank || 0);
                            } else if (sortBy === 'comments') {
                                compareValue = (a.rank_count || 0) - (b.rank_count || 0);
                            }
                            
                            return sortOrder === 'desc' ? -compareValue : compareValue;
                        });

                        return loadingVideos ? (
                            <LoadingComponent tip="正在加载作品列表..." minHeight={300} />
                        ) : filteredVideos.length > 0 ? (
                            <>
                                {filteredVideos.length !== actorVideos.length && (
                                    <div style={{ marginBottom: 16, color: '#666', fontSize: '12px' }}>
                                        筛选结果：{filteredVideos.length} / {actorVideos.length} 个作品
                                    </div>
                                )}
                                <List
                                    grid={{ gutter: 16, xs: 1, sm: 2, md: 3, lg: 3, xl: 4, xxl: 5 }}
                                    dataSource={filteredVideos}
                                    renderItem={(video: WebVideo, index: number) => {
                                // 为每个视频生成一个唯一的ID用于加载状态跟踪
                                const videoId = `${video.num}-${index}-${Math.random().toString(36).substring(2, 7)}`;
                                return (
                                    <List.Item key={videoId}>
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
                                            actions={[
                                                <Tooltip title="推送到下载器">
                                                    <Button
                                                        type="primary"
                                                        shape="circle"
                                                        icon={<CloudDownloadOutlined />}
                                                        size="small"
                                                        loading={loadingVideoId === videoId}
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            // 使用新的处理函数
                                                            handleVideoDownload(video);
                                                        }}
                                                    />
                                                </Tooltip>
                                            ]}
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
                                                        {video.rank && (
                                                            <div className={'flex items-center my-2'}>
                                                                <Rate disabled allowHalf value={video.rank} style={{ fontSize: 12 }} />
                                                                <div className={'mx-1'}>{video.rank}分</div>
                                                                {video.rank_count && <div>由{video.rank_count}人评价</div>}
                                                            </div>
                                                        )}
                                                        <div>
                                                            {video.is_zh && <span style={{ marginRight: 8, color: '#1890ff' }}>中文</span>}
                                                            {video.is_uncensored && <span style={{ color: '#ff4d4f' }}>无码</span>}
                                                        </div>
                                                        {video.publish_date && <div style={{ marginTop: 4, color: '#8c8c8c', fontSize: '12px' }}>发行日期: {video.publish_date}</div>}
                                                    </div>
                                                }
                                            />
                                        </Card>
                                    </List.Item>
                                );
                            }}
                                />
                            </>
                        ) : actorVideos.length > 0 ? (
                            <Empty description="没有符合筛选条件的视频" />
                        ) : (
                            <Empty description="没有找到相关视频" />
                        );
                    })()}
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

            {/* 单个下载对话框 */}
            <DownloadModal
                open={!!selectedDownload}
                download={selectedDownload}
                onCancel={() => setSelectedDownload(null)}
                onDownload={item => onDownload(selectedVideo, item)}
                confirmLoading={onDownloading}
            />

            {/* 添加下载列表模态框 */}
            <DownloadListModal
                open={showDownloadList}
                video={selectedVideo}
                downloads={downloadOptions}
                onCancel={() => setShowDownloadList(false)}
                onDownload={(video, item) => onDownload(video, item)}
                confirmLoading={onDownloading}
            />

            {/* 修改演员订阅对话框，添加onOk回调 */}
            {selectedActor && (
                <ActorSubscribeModal
                    open={subscribeModalVisible}
                    actor={selectedActor}
                    onCancel={() => setSubscribeModalVisible(false)}
                    onOk={handleSubscribeSuccess}
                />
            )}
        </div>
    );
};

export default WebActorSearch; 