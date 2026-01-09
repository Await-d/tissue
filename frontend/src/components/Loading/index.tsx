import React from 'react';
import { Spin } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

interface LoadingProps {
  /** 加载状态 */
  loading?: boolean;
  /** 提示文字 */
  tip?: string;
  /** 大小 */
  size?: 'small' | 'default' | 'large';
  /** 是否显示简化版本 */
  simple?: boolean;
  /** 最小高度 */
  minHeight?: number | string;
  /** 子元素 */
  children?: React.ReactNode;
}

const LoadingComponent: React.FC<LoadingProps> = ({
  loading = true,
  tip = '加载中...',
  size = 'default',
  simple = false,
  minHeight = 120,
  children
}) => {
  const antIcon = <LoadingOutlined style={{ fontSize: size === 'large' ? 24 : size === 'small' ? 14 : 18 }} spin />;

  if (simple) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: typeof minHeight === 'number' ? `${minHeight}px` : minHeight,
        padding: '16px'
      }}>
        <Spin indicator={antIcon} spinning={loading} />
        {tip && <span style={{ marginLeft: '8px', color: '#666' }}>{tip}</span>}
      </div>
    );
  }

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: typeof minHeight === 'number' ? `${minHeight}px` : minHeight,
      padding: '24px'
    }}>
      <Spin 
        indicator={antIcon} 
        spinning={loading} 
        tip={tip}
        size={size}
      >
        {children || <div style={{ minHeight: '60px', minWidth: '60px' }} />}
      </Spin>
    </div>
  );
};

export default LoadingComponent;