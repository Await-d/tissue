import React, { useState, useEffect } from 'react';
import { FloatButton, Badge, ConfigProvider } from 'antd';
import { MonitorOutlined } from '@ant-design/icons';
import ProgressMonitor, { ProgressManager } from '../ProgressMonitor';
import { useThemeColors } from '../../hooks/useThemeColors';

interface ProgressFloatButtonProps {
    style?: React.CSSProperties;
}

const ProgressFloatButton: React.FC<ProgressFloatButtonProps> = ({ style }) => {
    const [visible, setVisible] = useState(false);
    const [activeCount, setActiveCount] = useState(0);
    const colors = useThemeColors();

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
                        colorPrimary: colors.goldPrimary,
                        colorPrimaryHover: colors.goldLight,
                        colorBgElevated: colors.bgContainer,
                        colorText: colors.textPrimary,
                        colorBorder: colors.borderPrimary,
                    },
                    Badge: {
                        colorError: colors.goldPrimary,
                        colorBgContainer: colors.bgBase,
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
                        background: activeCount > 0 ? colors.goldPrimary : colors.bgContainer,
                        color: activeCount > 0 ? colors.bgBase : colors.textPrimary,
                        border: `1px solid ${activeCount > 0 ? colors.goldPrimary : colors.borderPrimary}`,
                        boxShadow: activeCount > 0 ? `0 0 20px ${colors.rgba('gold', 0.4)}` : colors.shadowMd,
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