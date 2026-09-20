import {useEffect, useRef, useState} from "react";
import {useSelector} from "react-redux";
import {RootState} from "../../../models";
import configs from "../../../configs";
import {fetchEventSource} from "@microsoft/fetch-event-source";
import {Table, Tag, Alert, Spin} from "antd";
import {ColumnsType} from "antd/lib/table";

interface Message {
    index: number
    level: string,
    module: string,
    time: string
    content: string
}

const tagColorMap: { [key: string]: string } = {
    'INFO': 'default',
    'WARN': 'warning',
    'ERROR': 'error',
}

// 日志缓冲区上限，避免长时间连接导致内存无限增长
const MAX_LOG_MESSAGES = 500
// 断线重连策略：最多重试次数与指数退避上限
const MAX_RETRY_ATTEMPTS = 5
const BASE_RETRY_DELAY = 1000
const MAX_RETRY_DELAY = 30000

function Log() {

    const {userToken} = useSelector((state: RootState) => state.auth)
    const [messages, setMessages] = useState<Message[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const container = useRef<HTMLDivElement>(null)
    const messageIndex = useRef(0)
    const retryAttempt = useRef(0)

    useEffect(() => {
        const ctrl = new AbortController();
        retryAttempt.current = 0;
        setLoading(true);
        setError(null);

        fetchEventSource(`${configs.BASE_API}/home/log`, {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${userToken}`
            },
            signal: ctrl.signal,
            openWhenHidden: true,
            async onopen(response) {
                if (import.meta.env.DEV) {
                    console.log('日志连接已打开', response.status);
                }
                setLoading(false);
                if (response.status === 200) {
                    // 连接成功，重置重试计数
                    retryAttempt.current = 0;
                } else {
                    setError(`连接失败: HTTP ${response.status}`);
                }
            },
            onmessage(msg) {
                if (import.meta.env.DEV) {
                    console.log('收到日志消息:', msg.data);
                }
                if (msg.data) {
                    const matched = msg.data.match(/【(.+)】(.+) - (.+) - (.+)/)
                    if (matched) {
                        messageIndex.current += 1
                        const nextMessage = {
                            index: messageIndex.current,
                            level: matched[1],
                            time: matched[2].split(" ")[1],
                            module: matched[3],
                            content: matched[4],
                        }
                        setMessages(data => [nextMessage, ...data].slice(0, MAX_LOG_MESSAGES))
                    } else if (import.meta.env.DEV) {
                        console.warn('日志格式不匹配:', msg.data);
                    }
                }
            },
            onerror(err) {
                console.error('日志连接错误:', err);
                setLoading(false);
                if (ctrl.signal.aborted) {
                    throw err;
                }
                retryAttempt.current += 1;
                if (retryAttempt.current > MAX_RETRY_ATTEMPTS) {
                    setError('连接日志服务失败，请检查网络连接');
                    // 抛出异常以终止 fetchEventSource 的无限重连循环
                    throw err;
                }
                // 指数退避：1s、2s、4s、8s、16s，避免紧凑的无限重连
                return Math.min(BASE_RETRY_DELAY * 2 ** (retryAttempt.current - 1), MAX_RETRY_DELAY);
            },
            onclose() {
                if (import.meta.env.DEV) {
                    console.log('日志连接已关闭');
                }
                setLoading(false);
            }
        }).catch((err) => {
            if (import.meta.env.DEV) {
                console.warn('日志连接已终止:', err);
            }
        });
        return () => {
            ctrl.abort()
        }
    }, [userToken])

    useEffect(() => {
        container.current?.scrollTo({
            top: 0,
            behavior: "smooth"
        })
    }, [messages]);

    const columns: ColumnsType<any> = [
        {
            dataIndex: 'level',
            width: 80,
            render: (value) => (<Tag color={tagColorMap[value]}>{value}</Tag>)
        },
        {
            dataIndex: 'time',
            width: 100
        },
        {
            dataIndex: 'module',
            width: 80
        },
        {
            dataIndex: 'content',
            width: 600
        }
    ]

    if (error) {
        return (
            <Alert 
                message="日志加载失败" 
                description={error} 
                type="error" 
                showIcon 
                style={{ margin: '20px 0' }}
            />
        );
    }

    return (
        <div ref={container} style={{height: '80vh', overflowY: 'auto'}}>
            {loading && (
                <div style={{ textAlign: 'center', padding: '20px' }}>
                    <Spin size="large" />
                    <div style={{ marginTop: '10px' }}>正在连接日志服务...</div>
                </div>
            )}
            <Table 
                rowKey={'index'} 
                showHeader={false} 
                columns={columns} 
                dataSource={messages} 
                pagination={false}
                scroll={{x: 'max-content'}}
                loading={loading}
            />
        </div>
    )
}

export default Log
