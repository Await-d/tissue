import React, { useState, useEffect } from 'react';
import { FloatButton, Badge, ConfigProvider } from 'antd';
import { MonitorOutlined } from '@ant-design/icons';
import ProgressMonitor, { ProgressManager } from '../ProgressMonitor';

interface ProgressFloatButtonProps {
    style?: React.CSSProperties;
}

const ProgressFloatButton: React.FC<ProgressFloatButtonProps> = ({ style }) => {
    const [visible, setVisible] = useState(false);
    const [activeCount, setActiveCount] = useState(0);

    useEffect(() => {
        const progressManager = ProgressManager.getInstance();
        
        const unsubscribe = progressManager.subscribe((items) => {
            const active = items.filter(item => item.status === 'active').length;
            setActiveCount(active);
        });

        return unsubscribe;
    }, []);

    return (
        <ConfigProvider
            theme={{
                components: {
                    FloatButton: {
                        colorPrimary: '#d4a852',
                        colorPrimaryHover: '#e8c780',
                        colorBgElevated: '#1a1a1d',
                        colorText: '#f0f0f2',
                        colorBorder: 'rgba(255, 255, 255, 0.08)',
                    },
                    Badge: {
                        colorError: '#d4a852',
                        colorBgContainer: '#0d0d0f',
                    }
                }
            }}
        >
            <Badge count={activeCount} offset={[-8, 8]}>
                <FloatButton
                    icon={<MonitorOutlined />}
                    tooltip="进度监控"
                    type={activeCount > 0 ? 'primary' : 'default'}
                    onClick={() => setVisible(true)}
                    style={{
                        bottom: 120,
                        right: 24,
                        background: activeCount > 0 ? '#d4a852' : '#1a1a1d',
                        color: activeCount > 0 ? '#0d0d0f' : '#f0f0f2',
                        border: `1px solid ${activeCount > 0 ? '#d4a852' : 'rgba(255, 255, 255, 0.08)'}`,
                        boxShadow: activeCount > 0 ? '0 0 20px rgba(212, 168, 82, 0.4)' : '0 4px 12px rgba(0, 0, 0, 0.3)',
                        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                        ...style
                    }}
                />
            </Badge>
            
            <ProgressMonitor
                visible={visible}
                onClose={() => setVisible(false)}
            />
        </ConfigProvider>
    );
};

export default ProgressFloatButton;