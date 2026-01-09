import {
    Button,
    Card,
    Checkbox,
    Col,
    Descriptions,
    Empty,
    Input,
    message,
    Row,
    Segmented,
    Skeleton,
    Space,
    Table,
    Tag,
    Tooltip,
    Badge,
    Dropdown,
    MenuProps
} from "antd";
import React, {useEffect, useState, useMemo} from "react";
import {
    CarryOutOutlined,
    CloudDownloadOutlined,
    CopyOutlined,
    HistoryOutlined,
    RedoOutlined,
    SearchOutlined,
    ThunderboltOutlined,
    DownloadOutlined,
    StarFilled
} from "@ant-design/icons";
import * as api from "../../../apis/subscribe";
import {useRequest, useResponsive} from "ahooks";
import {useFormModal} from "../../../utils/useFormModal.ts";
import Websites from "../../../components/Websites";
import VideoCover from "../../../components/VideoCover";
import SubscribeModifyModal from "../subscribe/-components/modifyModal.tsx";
import {
    createFileRoute,
    useSearch,
    useLoaderData,
    useRouter, useMatch
} from "@tanstack/react-router";
import Await from "../../../components/Await";
import {useDispatch} from "react-redux";
import {Dispatch} from "../../../models";
import Preview from "./-components/preview.tsx";
import DownloadModal from "./-components/downloadModal.tsx";
import HistoryModal from "./-components/historyModal.tsx";
import Comment from "./-components/comment.tsx";

const cacheHistoryKey = 'search_video_histories'
const filterPreferenceKey = 'search_filter_preference'

// Calculate quality score for a resource
function calculateQualityScore(item: any): number {
    let score = 0;

    // HD quality adds 40 points
    if (item.is_hd) score += 40;

    // Chinese subtitle adds 30 points
    if (item.is_zh) score += 30;

    // Uncensored adds 20 points
    if (item.is_uncensored) score += 20;

    // Size scoring (prefer larger files, usually better quality)
    const sizeMatch = item.size?.match(/(\d+\.?\d*)\s*(GB|MB)/i);
    if (sizeMatch) {
        const size = parseFloat(sizeMatch[1]);
        const unit = sizeMatch[2].toUpperCase();
        const sizeInGB = unit === 'GB' ? size : size / 1024;

        // Add up to 10 points based on size (capped at 5GB)
        score += Math.min(10, (sizeInGB / 5) * 10);
    }

    return score;
}

export const Route = createFileRoute('/_index/search/')({
    component: Search,
    loaderDeps: ({search}) => search as any,
    loader: ({deps}) => {
        return {
            data: deps.num ? (
                api.searchVideo(deps).then(data => {
                    const res = {...data, actors: data.actors.map((i: any) => i.name).join(", ")}
                    const histories: any[] = JSON.parse(localStorage.getItem(cacheHistoryKey) || '[]')
                        .filter((i: any) => i.num.toUpperCase() !== res.num.toUpperCase())
                    const history = {num: res.num, actors: res.actors, title: res.title, cover: res.cover}
                    localStorage.setItem(cacheHistoryKey, JSON.stringify([history, ...histories.slice(0, 19)]))
                    return res
                }).catch((err) => {

                })
            ) : (
                Promise.resolve()
            )
        }
    },
    staleTime: Infinity
})


export function Search() {

    const router = useRouter()

    const detailMatch = useMatch({from: '/_index/home/detail', shouldThrow: false})
    const routeId = detailMatch ? '/_index/home/detail' : '/_index/search/'
    const search: any = useSearch({from: routeId})
    const {data: loaderData} = useLoaderData<any>({from: routeId})

    const appDispatch = useDispatch<Dispatch>().app
    const responsive = useResponsive()
    const [searchInput, setSearchInput] = useState(!detailMatch ? search?.num : null)

    // Load filter preference from localStorage
    const savedFilter = useMemo(() => {
        try {
            const saved = localStorage.getItem(filterPreferenceKey);
            return saved ? JSON.parse(saved) : {isHd: false, isZh: false, isUncensored: false};
        } catch {
            return {isHd: false, isZh: false, isUncensored: false};
        }
    }, []);

    const [filter, setFilter] = useState(savedFilter)
    const [previewSelected, setPreviewSelected] = useState<string>()
    const [commentSelected, setCommentSelected] = useState<string>()
    const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])

    const [selectedVideo, setSelectedVideo] = useState<any>()
    const [selectedDownload, setSelectedDownload] = useState<any>()
    const [historyModalOpen, setHistoryModalOpen] = useState(false)

    // Save filter preference to localStorage
    useEffect(() => {
        localStorage.setItem(filterPreferenceKey, JSON.stringify(filter));
    }, [filter]);

    useEffect(() => {
        appDispatch.setCanBack(!!detailMatch)
        return () => {
            appDispatch.setCanBack(false)
        }
    }, [detailMatch])

    const {setOpen: setSubscribeOpen, modalProps: subscribeModalProps} = useFormModal({
        service: api.modifySubscribe,
        onOk: () => {
            setSubscribeOpen(false)
            return message.success("订阅添加成功")
        }
    })

    const {run: onDownload, loading: onDownloading} = useRequest(api.downloadVideos, {
        manual: true,
        onSuccess: () => {
            setSelectedVideo(undefined)
            setSelectedDownload(undefined)
            setSelectedRowKeys([])
            return message.success("下载任务创建成功")
        }
    })

    function renderItems(video: any) {
        return [
            {
                key: 'actors',
                label: '演员',
                span: 24,
                children: video.actors,
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
                key: 'outline-solid',
                label: '大纲',
                span: 24,
                children: (
                    <span className={'whitespace-pre-wrap'}>{video.outline}</span>
                ),
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
                    <Websites value={video.website} readonly/>
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

    // Quick download without confirmation
    function onQuickDownload(video: any, item: any) {
        onDownload(video, item);
    }

    // Smart download - automatically select best resource
    function onSmartDownload(video: any, downloads: any[]) {
        if (!downloads || downloads.length === 0) {
            return message.warning("没有可用的资源");
        }

        // Calculate scores and find best resource
        const scoredDownloads = downloads.map(item => ({
            ...item,
            score: calculateQualityScore(item)
        }));

        const bestResource = scoredDownloads.reduce((best, current) =>
            current.score > best.score ? current : best
        );

        message.info(`智能选择最优资源: ${bestResource.name}`);
        onDownload(video, bestResource);
    }

    // Batch download selected resources
    function onBatchDownload(video: any, downloads: any[]) {
        const selectedDownloads = downloads.filter((_, index) =>
            selectedRowKeys.includes(index)
        );

        if (selectedDownloads.length === 0) {
            return message.warning("请先选择要下载的资源");
        }

        // Download each selected resource
        selectedDownloads.forEach(item => {
            onDownload(video, item);
        });

        message.success(`已添加 ${selectedDownloads.length} 个下载任务`);
    }

    // Filter preset handlers
    function applyFilterPreset(preset: 'all' | 'hd' | 'zh' | 'hd-zh' | 'uncensored') {
        switch (preset) {
            case 'all':
                setFilter({isHd: false, isZh: false, isUncensored: false});
                break;
            case 'hd':
                setFilter({isHd: true, isZh: false, isUncensored: false});
                break;
            case 'zh':
                setFilter({isHd: false, isZh: true, isUncensored: false});
                break;
            case 'hd-zh':
                setFilter({isHd: true, isZh: true, isUncensored: false});
                break;
            case 'uncensored':
                setFilter({isHd: false, isZh: false, isUncensored: true});
                break;
        }
    }

    const filterPresetMenu: MenuProps = {
        items: [
            {key: 'all', label: '全部资源'},
            {key: 'hd', label: '仅高清'},
            {key: 'zh', label: '仅中文'},
            {key: 'hd-zh', label: '高清中文'},
            {key: 'uncensored', label: '仅无码'},
        ],
        onClick: ({key}) => applyFilterPreset(key as any)
    };

    // Render resource table for desktop
    function renderResourceTable(video: any, downloads: any[]) {
        const scoredDownloads = downloads.map((item, index) => ({
            ...item,
            key: index,
            score: calculateQualityScore(item)
        }));

        const maxScore = Math.max(...scoredDownloads.map(d => d.score));

        const columns = [
            {
                title: '资源名称',
                dataIndex: 'name',
                key: 'name',
                ellipsis: true,
                render: (text: string, record: any) => (
                    <div className="flex items-center gap-2">
                        {record.score === maxScore && maxScore > 0 && (
                            <Tooltip title="推荐资源">
                                <StarFilled className="text-yellow-500" />
                            </Tooltip>
                        )}
                        <Tooltip title={text}>
                            <span className="truncate">{text}</span>
                        </Tooltip>
                    </div>
                ),
            },
            {
                title: '大小',
                dataIndex: 'size',
                key: 'size',
                width: 100,
            },
            {
                title: '标签',
                key: 'tags',
                width: 180,
                render: (_: any, record: any) => (
                    <Space size={4}>
                        {record.is_hd && <Tag color="red" bordered={false}>高清</Tag>}
                        {record.is_zh && <Tag color="blue" bordered={false}>中文</Tag>}
                        {record.is_uncensored && <Tag color="green" bordered={false}>无码</Tag>}
                    </Space>
                ),
            },
            {
                title: '质量',
                key: 'quality',
                width: 80,
                render: (_: any, record: any) => {
                    const percentage = maxScore > 0 ? Math.round((record.score / maxScore) * 100) : 0;
                    let color = 'default';
                    if (percentage >= 80) color = 'success';
                    else if (percentage >= 60) color = 'processing';
                    else if (percentage >= 40) color = 'warning';

                    return (
                        <Tooltip title={`质量评分: ${record.score.toFixed(1)}`}>
                            <Badge status={color as any} text={`${percentage}%`} />
                        </Tooltip>
                    );
                },
            },
            {
                title: '来源',
                dataIndex: 'website',
                key: 'website',
                width: 100,
                render: (text: string, record: any) => (
                    <a href={record.url} target="_blank" rel="noopener noreferrer">
                        <Tag>{text}</Tag>
                    </a>
                ),
            },
            {
                title: '日期',
                dataIndex: 'publish_date',
                key: 'publish_date',
                width: 110,
            },
            {
                title: '操作',
                key: 'action',
                width: 120,
                fixed: 'right' as const,
                render: (_: any, record: any) => (
                    <Space size="small">
                        <Tooltip title="快速下载">
                            <Button
                                type="primary"
                                size="small"
                                icon={<DownloadOutlined />}
                                onClick={() => onQuickDownload(video, record)}
                                loading={onDownloading}
                            />
                        </Tooltip>
                        <Tooltip title="复制磁力">
                            <Button
                                size="small"
                                icon={<CopyOutlined />}
                                onClick={() => onCopyClick(record)}
                            />
                        </Tooltip>
                    </Space>
                ),
            },
        ];

        const rowSelection = {
            selectedRowKeys,
            onChange: (keys: React.Key[]) => setSelectedRowKeys(keys),
        };

        return (
            <Table
                columns={columns}
                dataSource={scoredDownloads}
                rowSelection={rowSelection}
                pagination={false}
                size="small"
                scroll={{x: 1000}}
                rowClassName="hover:bg-gray-50 transition-colors cursor-pointer"
            />
        );
    }

    // Render resource cards for mobile
    function renderResourceCards(video: any, downloads: any[]) {
        const scoredDownloads = downloads.map((item, index) => ({
            ...item,
            key: index,
            score: calculateQualityScore(item)
        }));

        const maxScore = Math.max(...scoredDownloads.map(d => d.score));

        return (
            <Space direction="vertical" size="middle" className="w-full">
                {scoredDownloads.map((item) => {
                    const percentage = maxScore > 0 ? Math.round((item.score / maxScore) * 100) : 0;
                    const isRecommended = item.score === maxScore && maxScore > 0;

                    return (
                        <Card
                            key={item.key}
                            size="small"
                            className="hover:shadow-md transition-shadow"
                            style={{
                                borderLeft: isRecommended ? '3px solid #faad14' : undefined
                            }}
                        >
                            <div className="flex items-start justify-between mb-2">
                                <div className="flex-1 mr-2">
                                    <div className="flex items-center gap-2 mb-1">
                                        {isRecommended && (
                                            <StarFilled className="text-yellow-500 text-xs" />
                                        )}
                                        <span className="font-medium text-sm">{item.name}</span>
                                    </div>
                                    <Space size={4} wrap>
                                        <Tag>{item.size}</Tag>
                                        <a href={item.url} target="_blank" rel="noopener noreferrer">
                                            <Tag>{item.website}</Tag>
                                        </a>
                                        <Tag>{item.publish_date}</Tag>
                                    </Space>
                                </div>
                                <Checkbox
                                    checked={selectedRowKeys.includes(item.key)}
                                    onChange={(e) => {
                                        if (e.target.checked) {
                                            setSelectedRowKeys([...selectedRowKeys, item.key]);
                                        } else {
                                            setSelectedRowKeys(selectedRowKeys.filter(k => k !== item.key));
                                        }
                                    }}
                                />
                            </div>
                            <div className="flex items-center justify-between">
                                <Space size={4}>
                                    {item.is_hd && <Tag color="red" bordered={false}>高清</Tag>}
                                    {item.is_zh && <Tag color="blue" bordered={false}>中文</Tag>}
                                    {item.is_uncensored && <Tag color="green" bordered={false}>无码</Tag>}
                                    <Badge
                                        status={percentage >= 80 ? 'success' : percentage >= 60 ? 'processing' : 'warning'}
                                        text={`${percentage}%`}
                                    />
                                </Space>
                                <Space size="small">
                                    <Button
                                        type="primary"
                                        size="small"
                                        icon={<DownloadOutlined />}
                                        onClick={() => onQuickDownload(video, item)}
                                        loading={onDownloading}
                                    >
                                        下载
                                    </Button>
                                    <Button
                                        size="small"
                                        icon={<CopyOutlined />}
                                        onClick={() => onCopyClick(item)}
                                    />
                                </Space>
                            </div>
                        </Card>
                    );
                })}
            </Space>
        );
    }

    return (
        <Row gutter={[15, 15]}>
            <Col span={24} lg={8} md={12}>
                <Card className="shadow-sm">
                    {!detailMatch && (
                        <div className={'flex'}>
                            <Input.Search placeholder={'请输入番号'} enterButton
                                          value={searchInput} allowClear
                                          onChange={e => setSearchInput(e.target.value)}
                                          onSearch={(num) => {
                                              if (num) {
                                                  return router.navigate({search: {num: num} as any, replace: true})
                                              }
                                          }}/>
                            <div className={'ml-2'}>
                                <Button type={"primary"} icon={<HistoryOutlined/>}
                                        onClick={() => setHistoryModalOpen(true)}/>
                            </div>
                        </div>
                    )}
                    <Await promise={loaderData}>
                        {(video, loading) => (
                            video ? (
                                <>
                                    <div className={'my-4 rounded-xl overflow-hidden shadow-lg'}
                                         style={{
                                             background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                             padding: '4px'
                                         }}>
                                        <div className="rounded-lg overflow-hidden">
                                            <VideoCover src={video.cover}/>
                                        </div>
                                    </div>
                                    <div className={'text-center'}>
                                        <Tooltip title={'添加订阅'}>
                                            <Button type={'primary'} icon={<CarryOutOutlined/>} shape={'circle'}
                                                    onClick={() => {
                                                        setSubscribeOpen(true, video)
                                                    }}/>
                                        </Tooltip>
                                        <Tooltip title={'刷新'}>
                                            <Button type={'primary'} icon={<RedoOutlined/>} shape={'circle'}
                                                    className={'ml-4'}
                                                    onClick={() => {
                                                        router.invalidate({filter: d => d.routeId === routeId})
                                                        return router.navigate({
                                                            replace: true,
                                                            search: {...search, num: video.num}
                                                        })
                                                    }}/>
                                        </Tooltip>
                                        {detailMatch && (
                                            <Tooltip title={'搜索'}>
                                                <Button type={'primary'} icon={<SearchOutlined/>} shape={'circle'}
                                                        className={'ml-4'}
                                                        onClick={() => {
                                                            setSearchInput(video.num)
                                                            return router.navigate({
                                                                to: '/search',
                                                                search: {num: video.num}
                                                            })
                                                        }}/>
                                            </Tooltip>
                                        )}
                                    </div>
                                    <Descriptions className={'mt-4'}
                                                  layout={'vertical'}
                                                  items={renderItems(video)}
                                                  column={24}
                                                  size={'small'}/>
                                </>
                            ) : (
                                <div className={'py-11'}>
                                    {loading ? (
                                        <Skeleton active/>
                                    ) : (
                                        <Empty/>
                                    )}
                                </div>
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
                                <Card title={'预览'} className={'mb-4 shadow-sm'} extra={(
                                    <Segmented onChange={(value: string) => setPreviewSelected(value)}
                                               options={video.previews.map((i: any) => i.website)}/>
                                )}>
                                    <Preview data={previews.items}/>
                                </Card>
                            )
                        } else {
                            return <div></div>
                        }
                    }}
                </Await>
                <Card
                    title={'资源列表'}
                    className="shadow-sm"
                    extra={
                        <Space wrap>
                            <Dropdown menu={filterPresetMenu} placement="bottomRight">
                                <Button size="small">筛选预设</Button>
                            </Dropdown>
                            <Segmented
                                options={[
                                    {
                                        label: '高清',
                                        value: 'hd',
                                    },
                                    {
                                        label: '中文',
                                        value: 'zh',
                                    },
                                    {
                                        label: '无码',
                                        value: 'uncensored',
                                    },
                                ]}
                                value={
                                    filter.isHd ? 'hd' :
                                    filter.isZh ? 'zh' :
                                    filter.isUncensored ? 'uncensored' :
                                    undefined
                                }
                                onChange={(value) => {
                                    if (value === 'hd') {
                                        setFilter({...filter, isHd: !filter.isHd});
                                    } else if (value === 'zh') {
                                        setFilter({...filter, isZh: !filter.isZh});
                                    } else if (value === 'uncensored') {
                                        setFilter({...filter, isUncensored: !filter.isUncensored});
                                    }
                                }}
                            />
                        </Space>
                    }
                >
                    <Await promise={loaderData}>
                        {(video: any, loading) => {
                            const downloads = video?.downloads?.filter((item: any) => (
                                (!filter.isHd || item.is_hd) &&
                                (!filter.isZh || item.is_zh) &&
                                (!filter.isUncensored || item.is_uncensored)
                            ))

                            return downloads ? (
                                <>
                                    <div className="mb-3 flex flex-wrap gap-2">
                                        <Button
                                            type="primary"
                                            icon={<ThunderboltOutlined />}
                                            onClick={() => onSmartDownload(video, downloads)}
                                            loading={onDownloading}
                                        >
                                            智能下载
                                        </Button>
                                        <Button
                                            icon={<CloudDownloadOutlined />}
                                            onClick={() => onBatchDownload(video, downloads)}
                                            disabled={selectedRowKeys.length === 0}
                                            loading={onDownloading}
                                        >
                                            批量下载 {selectedRowKeys.length > 0 && `(${selectedRowKeys.length})`}
                                        </Button>
                                        {selectedRowKeys.length > 0 && (
                                            <Button
                                                size="small"
                                                onClick={() => setSelectedRowKeys([])}
                                            >
                                                取消选择
                                            </Button>
                                        )}
                                    </div>
                                    {responsive.md ?
                                        renderResourceTable(video, downloads) :
                                        renderResourceCards(video, downloads)
                                    }
                                </>
                            ) : (
                                <div className={'py-8'}>
                                    {loading ? (
                                        <Skeleton active/>
                                    ) : (
                                        <Empty/>
                                    )}
                                </div>
                            )
                        }}
                    </Await>
                </Card>
                <Await promise={loaderData}>
                    {(video) => {
                        if (video?.comments && video.comments.length > 0) {
                            const comments = video.comments.find((i: any) => i.website === commentSelected) || video.comments[0]
                            return (
                                <Card title={'评论'} className={'mt-4 shadow-sm'} extra={(
                                    <Segmented onChange={(value: string) => setCommentSelected(value)}
                                               options={video.comments.map((i: any) => i.website)}/>
                                )}>
                                    <Comment data={comments.items}/>
                                </Card>
                            )
                        } else {
                            return <div></div>
                        }
                    }}
                </Await>
            </Col>
            <SubscribeModifyModal width={1100}
                                  {...subscribeModalProps} />
            <DownloadModal open={!!selectedDownload}
                           download={selectedDownload}
                           onCancel={() => setSelectedDownload(undefined)}
                           onDownload={item => onDownload(selectedVideo, item)}
                           confirmLoading={onDownloading}
            />
            <HistoryModal open={historyModalOpen}
                          onCancel={() => setHistoryModalOpen(false)}
                          onClick={history => {
                              setHistoryModalOpen(false)
                              setSearchInput(history.num)
                              return router.navigate({search: {num: history.num} as any, replace: true})
                          }}
            />
        </Row>
    )
}

