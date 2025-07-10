import React, { useState, useEffect } from 'react';
import { FloatButton, Badge } from 'antd';
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
        <>
            <Badge count={activeCount} offset={[-8, 8]}>
                <FloatButton
                    icon={<MonitorOutlined />}
                    tooltip="进度监控"
                    type={activeCount > 0 ? 'primary' : 'default'}
                    onClick={() => setVisible(true)}
                    style={{
                        bottom: 120,
                        right: 24,
                        ...style
                    }}
                />
            </Badge>
            
            <ProgressMonitor
                visible={visible}
                onClose={() => setVisible(false)}
            />
        </>
    );
};

export default ProgressFloatButton;