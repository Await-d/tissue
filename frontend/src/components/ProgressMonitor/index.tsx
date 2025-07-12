import React, { useState, useEffect } from 'react';
import { Card, Progress, List, Typography, Space, Tag, Button, Drawer, Badge, Statistic, Row, Col } from 'antd';
import { MonitorOutlined, CloseOutlined, ReloadOutlined } from '@ant-design/icons';

const { Text, Title } = Typography;

interface ProgressItem {
    id: string;
    title: string;
    progress: number;
    status: 'active' | 'success' | 'exception' | 'normal';
    description?: string;
    detail?: string;
    type: 'download' | 'search' | 'scrape' | 'subscribe';
}

interface ProgressMonitorProps {
    visible?: boolean;
    onClose?: () => void;
}

const ProgressMonitor: React.FC<ProgressMonitorProps> = ({ visible = false, onClose }) => {
    const [progressItems, setProgressItems] = useState<ProgressItem[]>([]);
    const [isMonitoring, setIsMonitoring] = useState(false);

    // 模拟进度数据 - 在实际应用中，这些数据应该来自后端API或WebSocket
    useEffect(() => {
        if (isMonitoring) {
            const interval = setInterval(() => {
                // 模拟进度更新
                setProgressItems(prev => prev.map(item => {
                    if (item.status === 'active' && item.progress < 100) {
                        const newProgress = Math.min(item.progress + Math.random() * 10, 100);
                        return {
                            ...item,
                            progress: newProgress,
                            status: newProgress >= 100 ? 'success' : 'active'
                        };
                    }
                    return item;
                }));
            }, 1000);

            return () => clearInterval(interval);
        }
    }, [isMonitoring]);

    const addProgressItem = (item: Omit<ProgressItem, 'id'>) => {
        const newItem: ProgressItem = {
            ...item,
            id: Date.now().toString() + Math.random().toString(36).substr(2, 9)
        };
        setProgressItems(prev => [...prev, newItem]);
    };

    const removeProgressItem = (id: string) => {
        setProgressItems(prev => prev.filter(item => item.id !== id));
    };

    const clearCompleted = () => {
        setProgressItems(prev => prev.filter(item => item.status !== 'success'));
    };

    const startMonitoring = () => {
        setIsMonitoring(true);
        // 添加一些示例进度项
        addProgressItem({
            title: '下载演员作品列表',
            progress: 45,
            status: 'active',
            description: '正在获取演员的最新作品...',
            type: 'search'
        });
        addProgressItem({
            title: '下载资源文件',
            progress: 78,
            status: 'active',
            description: 'SSIS-123 - 1.2GB',
            type: 'download'
        });
        addProgressItem({
            title: '刮削视频信息',
            progress: 100,
            status: 'success',
            description: '已完成刮削 SSIS-122',
            type: 'scrape'
        });
    };

    const stopMonitoring = () => {
        setIsMonitoring(false);
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'active': return '#1890ff';
            case 'success': return '#52c41a';
            case 'exception': return '#ff4d4f';
            default: return '#d9d9d9';
        }
    };

    const getTypeIcon = (type: string) => {
        switch (type) {
            case 'download': return '⬇️';
            case 'search': return '🔍';
            case 'scrape': return '📄';
            case 'subscribe': return '📺';
            default: return '⚡';
        }
    };

    const activeItems = progressItems.filter(item => item.status === 'active');
    const completedItems = progressItems.filter(item => item.status === 'success');
    const failedItems = progressItems.filter(item => item.status === 'exception');

    return (
        <Drawer
            title={
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Space>
                        <MonitorOutlined />
                        <span>进度监控</span>
                        {(activeItems.length > 0 || isMonitoring) && (
                            <Badge count={activeItems.length} style={{ backgroundColor: '#1890ff' }} />
                        )}
                    </Space>
                    <Space>
                        {!isMonitoring ? (
                            <Button type="primary" size="small" onClick={startMonitoring}>
                                开始监控
                            </Button>
                        ) : (
                            <Button size="small" onClick={stopMonitoring}>
                                停止监控
                            </Button>
                        )}
                        {completedItems.length > 0 && (
                            <Button size="small" onClick={clearCompleted}>
                                清除已完成
                            </Button>
                        )}
                    </Space>
                </div>
            }
            placement="right"
            width={400}
            open={visible}
            onClose={onClose}
            closable={false}
            extra={
                <Button 
                    type="text" 
                    icon={<CloseOutlined />} 
                    onClick={onClose}
                    size="small"
                />
            }
        >
            {/* 统计信息 */}
            <Row gutter={8} style={{ marginBottom: 16 }}>
                <Col span={8}>
                    <Statistic
                        title="进行中"
                        value={activeItems.length}
                        valueStyle={{ fontSize: 16, color: '#1890ff' }}
                    />
                </Col>
                <Col span={8}>
                    <Statistic
                        title="已完成"
                        value={completedItems.length}
                        valueStyle={{ fontSize: 16, color: '#52c41a' }}
                    />
                </Col>
                <Col span={8}>
                    <Statistic
                        title="失败"
                        value={failedItems.length}
                        valueStyle={{ fontSize: 16, color: '#ff4d4f' }}
                    />
                </Col>
            </Row>

            {progressItems.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
                    <MonitorOutlined style={{ fontSize: 48, marginBottom: 16 }} />
                    <div>暂无进行中的任务</div>
                    <div style={{ fontSize: 12, marginTop: 8 }}>
                        点击"开始监控"查看示例数据
                    </div>
                </div>
            ) : (
                <List
                    dataSource={progressItems}
                    renderItem={item => (
                        <List.Item
                            style={{ 
                                padding: '12px 0',
                                borderBottom: '1px solid #f0f0f0'
                            }}
                            extra={
                                <Button
                                    type="text"
                                    size="small"
                                    icon={<CloseOutlined />}
                                    onClick={() => removeProgressItem(item.id)}
                                    style={{ opacity: 0.6 }}
                                />
                            }
                        >
                            <List.Item.Meta
                                avatar={
                                    <div style={{ fontSize: 20 }}>
                                        {getTypeIcon(item.type)}
                                    </div>
                                }
                                title={
                                    <div style={{ marginBottom: 8 }}>
                                        <Text strong style={{ fontSize: 14 }}>
                                            {item.title}
                                        </Text>
                                        <Tag 
                                            color={getStatusColor(item.status)}
                                            style={{ marginLeft: 8 }}
                                        >
                                            {item.status === 'active' ? '进行中' : 
                                             item.status === 'success' ? '已完成' : '失败'}
                                        </Tag>
                                    </div>
                                }
                                description={
                                    <div>
                                        <Progress
                                            percent={Math.round(item.progress)}
                                            size="small"
                                            status={item.status === 'exception' ? 'exception' : 'normal'}
                                            strokeColor={getStatusColor(item.status)}
                                            style={{ marginBottom: 4 }}
                                        />
                                        {item.description && (
                                            <Text style={{ fontSize: 12, color: '#666' }}>
                                                {item.description}
                                            </Text>
                                        )}
                                    </div>
                                }
                            />
                        </List.Item>
                    )}
                />
            )}
        </Drawer>
    );
};

// 导出一个全局进度管理器
export class ProgressManager {
    private static instance: ProgressManager;
    private listeners: ((items: ProgressItem[]) => void)[] = [];
    private items: ProgressItem[] = [];

    static getInstance(): ProgressManager {
        if (!ProgressManager.instance) {
            ProgressManager.instance = new ProgressManager();
        }
        return ProgressManager.instance;
    }

    addProgress(item: Omit<ProgressItem, 'id'>): string {
        const newItem: ProgressItem = {
            ...item,
            id: Date.now().toString() + Math.random().toString(36).substr(2, 9)
        };
        this.items.push(newItem);
        this.notifyListeners();
        return newItem.id;
    }

    updateProgress(id: string, updates: Partial<ProgressItem>): void {
        const index = this.items.findIndex(item => item.id === id);
        if (index !== -1) {
            this.items[index] = { ...this.items[index], ...updates };
            this.notifyListeners();
        }
    }

    removeProgress(id: string): void {
        this.items = this.items.filter(item => item.id !== id);
        this.notifyListeners();
    }

    getItems(): ProgressItem[] {
        return [...this.items];
    }

    subscribe(listener: (items: ProgressItem[]) => void): () => void {
        this.listeners.push(listener);
        return () => {
            this.listeners = this.listeners.filter(l => l !== listener);
        };
    }

    private notifyListeners(): void {
        this.listeners.forEach(listener => listener([...this.items]));
    }
}

export default ProgressMonitor;