import {
    Button,
    Card,
    Col,
    Descriptions,
    Empty,
    Input,
    List,
    App,
    Row, Segmented, Skeleton,
    Space,
    Tag,
    Tooltip,
    Switch,
    Select,
    InputNumber,
    Checkbox,
    Progress,
    Badge,
    Divider
} from "antd";
import React, { useEffect, useState } from "react";
import { CarryOutOutlined, CloudDownloadOutlined, CopyOutlined, HistoryOutlined, RedoOutlined, UserOutlined, ClearOutlined, FilterOutlined, SortAscendingOutlined, SortDescendingOutlined } from "@ant-design/icons";
import * as api from "../../../apis/subscribe";
import * as videoApi from "../../../apis/video";
import { useRequest, useResponsive } from "ahooks";
import { useFormModal } from "../../../utils/useFormModal.ts";
import Websites from "../../../components/Websites";
import VideoCover from "../../../components/VideoCover";
import VideoDetail from "../../../components/VideoDetail";
import SubscribeModifyModal from "../subscribe/-components/modifyModal.tsx";
import {
    createFileRoute,
    useSearch,
    useLoaderData,
    useRouter, useMatch, useNavigate, Link
} from "@tanstack/react-router";
import Await from "../../../components/Await";
import { useDispatch } from "react-redux";
import { Dispatch } from "../../../models";
import Preview from "./-components/preview.tsx";
import DownloadModal from "./-components/downloadModal.tsx";
import DownloadListModal from "./-components/downloadListModal.tsx";
import HistoryModal from "./-components/historyModal.tsx";

const cacheHistoryKey = 'search_video_histories'
const cacheLastSearchKey = 'search_video_last_search'

export const Route = createFileRoute('/_index/search/')({
    component: Search,
    loaderDeps: ({ search }) => search as any,
    loader: ({ deps }) => {
        return {
            data: deps.num ? (
                api.searchVideo(deps).then(data => {
                    const res = { ...data, actors: data.actors.map((i: any) => i.name).join(", ") }
                    const histories: any[] = JSON.parse(localStorage.getItem(cacheHistoryKey) || '[]')
                        .filter((i: any) => i.num.toUpperCase() !== res.num.toUpperCase())
                    const history = { num: res.num, actors: res.actors, title: res.title, cover: res.cover }
                    localStorage.setItem(cacheHistoryKey, JSON.stringify([history, ...histories.slice(0, 9)]))

                    // 保存最后一次搜索的番号
                    localStorage.setItem(cacheLastSearchKey, res.num)

                    return res
                }).catch(() => {

                })
            ) : (
                Promise.resolve()
            )
        }
    },
    staleTime: Infinity
})


export function Search() {
    const { message } = App.useApp();
    const router = useRouter()
    const navigate = useNavigate()

    const detailMatch = useMatch({ from: '/_index/home/detail', shouldThrow: false })
    const routeId = detailMatch ? '/_index/home/detail' : '/_index/search/'
    const search: any = useSearch({ from: routeId })
    const { data: loaderData } = useLoaderData<any>({ from: routeId })

    const appDispatch = useDispatch<Dispatch>().app
    const responsive = useResponsive()
    const [searchInput, setSearchInput] = useState(search?.num)
    const [filter, setFilter] = useState({ isHd: false, isZh: false, isUncensored: false })
    const [previewSelected, setPreviewSelected] = useState<string>()
    const [showAdvancedFilters, setShowAdvancedFilters] = useState(false)
    const [advancedFilters, setAdvancedFilters] = useState({
        minSize: 0,
        maxSize: 10000,
        sortBy: 'date',
        sortOrder: 'desc',
        showOnlyWithPreviews: false,
        website: 'all'
    })
    const [searchProgress, setSearchProgress] = useState({
        current: 0,
        total: 0,
        isSearching: false
    })

    const [selectedVideo, setSelectedVideo] = useState<any>()
    const [selectedDownload, setSelectedDownload] = useState<any>()
    const [showDownloadList, setShowDownloadList] = useState(false)
    const [historyModalOpen, setHistoryModalOpen] = useState(false)
    const [loadingDownloadId, setLoadingDownloadId] = useState<string | null>(null)

    // 组件加载时，检查是否有上一次搜索的番号，如果有且当前没有搜索参数，则自动搜索
    useEffect(() => {
        if (!search?.num) {
            const lastSearch = localStorage.getItem(cacheLastSearchKey);
            if (lastSearch) {
                setSearchInput(lastSearch);
                // 如果需要自动搜索，取消注释下面这行
                // router.navigate({ search: { num: lastSearch } as any, replace: true });
            }
        }
    }, []);

    useEffect(() => {
        if (detailMatch) {
            appDispatch.setCanBack(true)
        }
        return () => {
            appDispatch.setCanBack(false)
        }
    }, [detailMatch, appDispatch])

    const { setOpen: setSubscribeOpen, modalProps: subscribeModalProps, form: subscribeForm } = useFormModal({
        service: api.modifySubscribe,
        onOk: () => {
            setSubscribeOpen(false)
            return message.success("订阅添加成功")
        }
    })

    const { run: onDownload, loading: onDownloading } = useRequest(api.downloadVideos, {
        manual: true,
        onSuccess: () => {
            setSelectedVideo(undefined)
            setSelectedDownload(undefined)
            setShowDownloadList(false)
            return message.success("下载任务创建成功")
        },
        onError: (err) => {
            console.error(err)
            message.error("下载任务创建失败")
        }
    })

    // 清除搜索结果
    const handleClearSearch = () => {
        setSearchInput('');
        localStorage.removeItem(cacheLastSearchKey);
        router.navigate({ search: {} as any, replace: true });
    };

    function renderItems(video: any) {
        return [
            {
                key: 'actors',
                label: '演员',
                span: 24,
                children: typeof video.actors === 'string' ? (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                        {video.actors.split(',').map((actor: string) => {
                            const actorName = actor.trim();
                            return actorName ? (
                                <Tag
                                    key={actorName}
                                    color="blue"
                                    style={{ cursor: 'pointer' }}
                                    onClick={() => handleActorClick(actorName)}
                                >
                                    {actorName}
                                </Tag>
                            ) : null;
                        })}
                    </div>
                ) : video.actors,
            },
            {
                key: 'num',
                label: '番号',
                span: 8,
                children: video.num,
            },
            {
                key: 'premiered',
                label: '发布日期',
                span: 8,
                children: video.premiered,
            },
            {
                key: 'rating',
                label: '评分',
                span: 8,
                children: video.rating,
            },
            {
                key: 'title',
                label: '标题',
                span: 24,
                children: video.title,
            },
            {
                key: 'outline',
                label: '大纲',
                span: 24,
                children: video.outline,
            },
            {
                key: 'studio',
                label: '制造商',
                span: 8,
                children: video.studio,
            },
            {
                key: 'publisher',
                label: '发行商',
                span: 8,
                children: video.publisher,
            },
            {
                key: 'director',
                label: '导演',
                span: 8,
                children: video.director,
            },
            {
                key: 'tags',
                label: '类别',
                span: 24,
                children: (
                    <div className={'leading-7'}>
                        {video.tags.map((i: any) => (
                            <Tag key={i}>{i}</Tag>
                        ))}
                    </div>
                ),
            },
            {
                key: 'series',
                label: '系列',
                span: 16,
                children: video.series,
            },
            {
                key: 'runtime',
                label: '时长',
                span: 8,
                children: video.runtime,
            },
            {
                key: 'websites',
                label: '网站',
                span: 24,
                children: (
                    <Websites value={video.website} readonly />
                ),
            },
        ]
    }

    function onCopyClick(item: any) {
        const textarea = document.createElement('textarea');
        textarea.value = item.magnet;
        textarea.style.position = 'fixed';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        return message.success("磁力链接已复制")
    }

    const handleActorClick = (actorName: string) => {
        navigate({
            to: '/actor',
            search: { actorName: actorName } as any,
            replace: true
        });
    };

    const handleWebVideoSelect = (video: any) => {
        if (video && video.url) {
            let source = 'JavDB';

            if (video.url.includes('javbus')) {
                source = 'JavBus';
                console.log('根据URL设置source为JavBus');
            }
            else if (video.url.includes('javdb')) {
                source = 'JavDB';
                console.log('根据URL设置source为JavDB');
            }

            navigate({
                to: '/home/detail',
                search: { source: source, num: video.num, url: video.url }
            });
        }
    };

    const handleHistorySelect = (num: string) => {
        setHistoryModalOpen(false)
        navigate({
            search: { num } as any
        })
    };

    const handleDownloadClick = (video: any, downloadItem?: any) => {
        setLoadingDownloadId(video.num)

        setSelectedVideo(video)

        if (downloadItem) {
            setSelectedDownload(downloadItem)
            setLoadingDownloadId(null)
            return
        }

        const downloads = video?.downloads
        if (downloads && downloads.length > 0) {
            setShowDownloadList(true)
            setLoadingDownloadId(null)
        } else {
            message.warning("没有可用的下载资源")
            setLoadingDownloadId(null)
        }
    }

    return (
        <Row gutter={[15, 15]}>
            <Col span={24}>
                <Card
                    title="番号搜索"
                    extra={
                        <Space>
                            <Button
                                icon={<HistoryOutlined />}
                                onClick={() => setHistoryModalOpen(true)}
                            >
                                历史记录
                            </Button>
                            <Link to="/actor">
                                <Button type="primary" icon={<UserOutlined />}>
                                    演员搜索
                                </Button>
                            </Link>
                            <Button
                                icon={<ClearOutlined />}
                                onClick={handleClearSearch}
                            >
                                清除
                            </Button>
                        </Space>
                    }
                >
                    <Row gutter={[15, 15]}>
                        <Col span={24} lg={8} md={12}>
                            <Card>
                                {!detailMatch && (
                                    <div className={'flex'}>
                                        <Input.Search
                                            placeholder={'请输入番号'}
                                            enterButton
                                            value={searchInput}
                                            allowClear
                                            onChange={e => setSearchInput(e.target.value)}
                                            onSearch={(num) => {
                                                return router.navigate({ search: { num: num } as any, replace: true })
                                            }}
                                        />
                                    </div>
                                )}
                                <Await promise={loaderData}>
                                    {(video, loading) => (
                                        video ? (
                                            <>
                                                <div className={'my-4 rounded-lg overflow-hidden'}>
                                                    <VideoCover src={video.cover} />
                                                </div>
                                                <div className={'text-center'}>
                                                    <Tooltip title={'添加订阅'}>
                                                        <Button
                                                            type={'primary'}
                                                            icon={<CarryOutOutlined />}
                                                            shape={'circle'}
                                                            onClick={() => {
                                                                setSubscribeOpen(true, video)
                                                            }}
                                                        />
                                                    </Tooltip>
                                                    <Tooltip title={'刷新'}>
                                                        <Button
                                                            type={'primary'}
                                                            icon={<RedoOutlined />}
                                                            shape={'circle'}
                                                            className={'ml-4'}
                                                            onClick={() => {
                                                                router.invalidate({ filter: d => d.routeId === routeId })
                                                                return router.navigate({
                                                                    replace: true,
                                                                    search: { ...search, num: video.num }
                                                                })
                                                            }}
                                                        />
                                                    </Tooltip>
                                                </div>
                                                <Descriptions
                                                    className={'mt-4'}
                                                    layout={'vertical'}
                                                    items={renderItems(video)}
                                                    column={24}
                                                    size={'small'}
                                                />
                                            </>
                                        ) : (
                                            loading ? (
                                                <Skeleton active />
                                            ) : (
                                                <div className={'py-11'}>
                                                    <Empty />
                                                </div>
                                            )
                                        )
                                    )}
                                </Await>
                            </Card>
                        </Col>
                        <Col span={24} lg={16} md={12}>
                            <Await promise={loaderData}>
                                {(video) => {
                                    if (video?.previews) {
                                        const previews = video.previews.find((i: any) => i.website === previewSelected) || video.previews[0]
                                        return (
                                            <Card
                                                title={'预览'}
                                                className={'mb-4'}
                                                extra={(
                                                    <Segmented
                                                        onChange={(value: string) => setPreviewSelected(value)}
                                                        options={video.previews.map((i: any) => i.website)}
                                                    />
                                                )}>
                                                <Preview data={previews.items} />
                                            </Card>
                                        )
                                    } else {
                                        return <div></div>
                                    }
                                }}
                            </Await>
                            <Card
                                title={
                                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                        <span>资源列表</span>
                                        <Button
                                            icon={<FilterOutlined />}
                                            size="small"
                                            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                                        >
                                            高级筛选 {showAdvancedFilters ? '▼' : '▶'}
                                        </Button>
                                    </div>
                                }
                                extra={
                                    <Space wrap>
                                        <Tag
                                            color={filter.isHd ? 'red' : 'default'}
                                            className={'cursor-pointer'}
                                            onClick={() => setFilter({ ...filter, isHd: !filter.isHd })}
                                        >
                                            高清
                                        </Tag>
                                        <Tag
                                            color={filter.isZh ? 'blue' : 'default'}
                                            className={'cursor-pointer'}
                                            onClick={() => setFilter({ ...filter, isZh: !filter.isZh })}
                                        >
                                            中文
                                        </Tag>
                                        <Tag
                                            color={filter.isUncensored ? 'green' : 'default'}
                                            className={'cursor-pointer'}
                                            onClick={() => setFilter({
                                                ...filter,
                                                isUncensored: !filter.isUncensored
                                            })}
                                        >
                                            无码
                                        </Tag>
                                    </Space>
                                }>
                                {showAdvancedFilters && (
                                    <Card size="small" style={{ marginBottom: 16 }}>
                                        <Row gutter={[16, 8]}>
                                            <Col span={12}>
                                                <div style={{ marginBottom: 8 }}>文件大小范围 (MB)</div>
                                                <Row gutter={8}>
                                                    <Col span={12}>
                                                        <InputNumber
                                                            min={0}
                                                            value={advancedFilters.minSize}
                                                            onChange={(value) => setAdvancedFilters({
                                                                ...advancedFilters,
                                                                minSize: value || 0
                                                            })}
                                                            placeholder="最小"
                                                            style={{ width: '100%' }}
                                                        />
                                                    </Col>
                                                    <Col span={12}>
                                                        <InputNumber
                                                            min={0}
                                                            value={advancedFilters.maxSize}
                                                            onChange={(value) => setAdvancedFilters({
                                                                ...advancedFilters,
                                                                maxSize: value || 10000
                                                            })}
                                                            placeholder="最大"
                                                            style={{ width: '100%' }}
                                                        />
                                                    </Col>
                                                </Row>
                                            </Col>
                                            <Col span={8}>
                                                <div style={{ marginBottom: 8 }}>排序方式</div>
                                                <Select
                                                    value={`${advancedFilters.sortBy}-${advancedFilters.sortOrder}`}
                                                    onChange={(value) => {
                                                        const [sortBy, sortOrder] = value.split('-');
                                                        setAdvancedFilters({
                                                            ...advancedFilters,
                                                            sortBy,
                                                            sortOrder
                                                        });
                                                    }}
                                                    style={{ width: '100%' }}
                                                >
                                                    <Select.Option value="date-desc">日期 (新→旧)</Select.Option>
                                                    <Select.Option value="date-asc">日期 (旧→新)</Select.Option>
                                                    <Select.Option value="size-desc">大小 (大→小)</Select.Option>
                                                    <Select.Option value="size-asc">大小 (小→大)</Select.Option>
                                                </Select>
                                            </Col>
                                            <Col span={4}>
                                                <div style={{ marginBottom: 8 }}>数据源</div>
                                                <Select
                                                    value={advancedFilters.website}
                                                    onChange={(value) => setAdvancedFilters({
                                                        ...advancedFilters,
                                                        website: value
                                                    })}
                                                    style={{ width: '100%' }}
                                                >
                                                    <Select.Option value="all">全部</Select.Option>
                                                    <Select.Option value="javbus">JavBus</Select.Option>
                                                    <Select.Option value="javdb">JavDB</Select.Option>
                                                </Select>
                                            </Col>
                                        </Row>
                                    </Card>
                                )}
                                
                                <Await promise={loaderData}>
                                    {(video: any, loading) => {
                                        if (!video?.downloads) {
                                            return loading ? <Skeleton active /> : <Empty description="没有找到下载资源" />;
                                        }

                                        // 基础过滤
                                        let downloads = video.downloads.filter((item: any) => (
                                            (!filter.isHd || item.is_hd) &&
                                            (!filter.isZh || item.is_zh) &&
                                            ((!filter.isUncensored || item.is_uncensored))
                                        ));

                                        // 高级过滤
                                        if (showAdvancedFilters) {
                                            downloads = downloads.filter((item: any) => {
                                                // 大小过滤
                                                const sizeMatch = item.size?.match(/([0-9.]+)/);
                                                const sizeInMB = sizeMatch ? parseFloat(sizeMatch[1]) : 0;
                                                if (sizeInMB < advancedFilters.minSize || sizeInMB > advancedFilters.maxSize) {
                                                    return false;
                                                }
                                                
                                                // 数据源过滤
                                                if (advancedFilters.website !== 'all' && 
                                                    item.website?.toLowerCase() !== advancedFilters.website) {
                                                    return false;
                                                }
                                                
                                                return true;
                                            });

                                            // 排序
                                            downloads = downloads.sort((a: any, b: any) => {
                                                const { sortBy, sortOrder } = advancedFilters;
                                                let compareValue = 0;
                                                
                                                if (sortBy === 'date') {
                                                    const dateA = new Date(a.publish_date || '1900-01-01');
                                                    const dateB = new Date(b.publish_date || '1900-01-01');
                                                    compareValue = dateA.getTime() - dateB.getTime();
                                                } else if (sortBy === 'size') {
                                                    const sizeMatchA = a.size?.match(/([0-9.]+)/);
                                                    const sizeMatchB = b.size?.match(/([0-9.]+)/);
                                                    const sizeA = sizeMatchA ? parseFloat(sizeMatchA[1]) : 0;
                                                    const sizeB = sizeMatchB ? parseFloat(sizeMatchB[1]) : 0;
                                                    compareValue = sizeA - sizeB;
                                                }
                                                
                                                return sortOrder === 'desc' ? -compareValue : compareValue;
                                            });
                                        }

                                        const filteredCount = downloads.length;
                                        const totalCount = video.downloads.length
                                        return downloads ? (
                                            <>
                                                {filteredCount !== totalCount && (
                                                    <div style={{ marginBottom: 16, padding: '8px 12px', background: '#f0f2f5', borderRadius: 4 }}>
                                                        <Space>
                                                            <Badge count={filteredCount} style={{ backgroundColor: '#1890ff' }} />
                                                            <span>筛选结果：{filteredCount} / {totalCount} 个资源</span>
                                                            {showAdvancedFilters && (
                                                                <Button 
                                                                    size="small" 
                                                                    onClick={() => {
                                                                        setFilter({ isHd: false, isZh: false, isUncensored: false });
                                                                        setAdvancedFilters({
                                                                            minSize: 0,
                                                                            maxSize: 10000,
                                                                            sortBy: 'date',
                                                                            sortOrder: 'desc',
                                                                            showOnlyWithPreviews: false,
                                                                            website: 'all'
                                                                        });
                                                                    }}
                                                                >
                                                                    重置筛选
                                                                </Button>
                                                            )}
                                                        </Space>
                                                    </div>
                                                )}
                                                
                                                <List
                                                dataSource={downloads}
                                                renderItem={(item: any) => (
                                                    <List.Item
                                                        actions={[
                                                            <Tooltip title={'发送到下载器'}>
                                                                <Button
                                                                    type={'primary'}
                                                                    icon={<CloudDownloadOutlined />}
                                                                    shape={'circle'}
                                                                    loading={loadingDownloadId === video.num}
                                                                    onClick={() => {
                                                                        setLoadingDownloadId(video.num);
                                                                        onDownload(video, item);
                                                                    }}
                                                                />
                                                            </Tooltip>,
                                                            <Tooltip title={'复制磁力链接'}>
                                                                <Button
                                                                    type={'primary'}
                                                                    icon={<CopyOutlined />}
                                                                    shape={'circle'}
                                                                    onClick={() => onCopyClick(item)}
                                                                />
                                                            </Tooltip>
                                                        ]}>
                                                        <List.Item.Meta
                                                            title={item.name}
                                                            description={(
                                                                <Space
                                                                    direction={responsive.lg ? 'horizontal' : 'vertical'}
                                                                    size={responsive.lg ? 0 : 'small'}>
                                                                    <div>
                                                                        <a href={item.url}>
                                                                            <Tag>{item.website}</Tag>
                                                                        </a>
                                                                        <Tag>{item.size}</Tag>
                                                                    </div>
                                                                    <div>
                                                                        {item.is_hd &&
                                                                            <Tag color={'red'} bordered={false}>高清</Tag>}
                                                                        {item.is_zh &&
                                                                            <Tag color={'blue'} bordered={false}>中文</Tag>}
                                                                        {item.is_uncensored &&
                                                                            <Tag color={'green'} bordered={false}>无码</Tag>}
                                                                    </div>
                                                                    <div>{item.publish_date}</div>
                                                                </Space>
                                                            )}
                                                        />
                                                    </List.Item>
                                                )}
                                                />
                                            </>
                                        ) : (
                                            loading ? (
                                                <Skeleton active />
                                            ) : (
                                                <div className={'py-8'}>
                                                    <Empty />
                                                </div>
                                            )
                                        )
                                    }}
                                </Await>
                            </Card>
                        </Col>
                    </Row>
                </Card>
            </Col>

            <SubscribeModifyModal width={1100}
                form={subscribeForm}
                {...subscribeModalProps} />
            <DownloadModal open={!!selectedDownload}
                download={selectedDownload}
                onCancel={() => setSelectedDownload(undefined)}
                onDownload={item => onDownload(selectedVideo, item)}
                confirmLoading={onDownloading}
            />
            <DownloadListModal
                open={showDownloadList}
                video={selectedVideo}
                downloads={selectedVideo?.downloads}
                onCancel={() => setShowDownloadList(false)}
                onDownload={onDownload}
                confirmLoading={onDownloading}
            />
            <HistoryModal
                open={historyModalOpen}
                onCancel={() => setHistoryModalOpen(false)}
                onSelect={handleHistorySelect}
            />
        </Row>
    )
}

