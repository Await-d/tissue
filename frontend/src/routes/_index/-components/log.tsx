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

function Log() {

    const {userToken} = useSelector((state: RootState) => state.auth)
    const [messages, setMessages] = useState<Message[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const container = useRef<HTMLDivElement>(null)

    useEffect(() => {
        const ctrl = new AbortController();
        setLoading(true);
        setError(null);
        
        console.log('开始连接日志，token:', userToken ? '已有token' : '无token');
        
        if (!userToken) {
            setError('用户未登录，请先登录');
            setLoading(false);
            return;
        }
        
        fetchEventSource(`${configs.BASE_API}/home/log`, {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${userToken}`
            },
            signal: ctrl.signal,
            openWhenHidden: true,
            async onopen(response) {
                console.log('日志连接已打开', response.status);
                setLoading(false);
                if (response.status !== 200) {
                    if (response.status === 401) {
                        setError('认证失败，请重新登录');
                    } else {
                        setError(`连接失败: HTTP ${response.status}`);
                    }
                }
            },
            onmessage(msg) {
                console.log('收到日志消息:', msg.data);
                if (msg.data) {
                    const matched = msg.data.match(/【(.+)】(.+) - (.+) - (.+)/)
                    if (matched) {
                        setMessages(data => [{
                            index: data.length + 1,
                            level: matched[1],
                            time: matched[2].split(" ")[1],
                            module: matched[3],
                            content: matched[4],
                        }, ...data])
                    } else {
                        console.warn('日志格式不匹配:', msg.data);
                    }
                }
            },
            onerror(err) {
                console.error('日志连接错误:', err);
                setError('连接日志服务失败，请检查网络连接或重新登录');
                setLoading(false);
            },
            onclose() {
                console.log('日志连接已关闭');
                setLoading(false);
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
