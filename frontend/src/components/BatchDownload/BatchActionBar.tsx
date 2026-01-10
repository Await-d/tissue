/**
 * @Author: Await
 * @Date: 2025-01-10
 * @Description: 批量操作工具栏组件
 */
import React from 'react';
import { Button, Space, Checkbox } from 'antd';
import {
    CloudDownloadOutlined,
    CloseOutlined,
    CheckSquareOutlined,
    BorderOutlined
} from '@ant-design/icons';
import type { BatchSelectVideo } from '@/hooks/useBatchSelect';
import './BatchActionBar.css';

interface BatchActionBarProps {
    /** 是否显示 */
    visible: boolean;
    /** 选中数量 */
    selectedCount: number;
    /** 总数量 */
    totalCount: number;
    /** 全选回调 */
    onSelectAll: () => void;
    /** 取消全选回调 */
    onUnselectAll: () => void;
    /** 批量下载回调 */
    onBatchDownload: () => void;
    /** 退出批量模式回调 */
    onExit: () => void;
    /** 下载中状态 */
    loading?: boolean;
}

const BatchActionBar: React.FC<BatchActionBarProps> = ({
    visible,
    selectedCount,
    totalCount,
    onSelectAll,
    onUnselectAll,
    onBatchDownload,
    onExit,
    loading = false,
}) => {
    if (!visible) return null;

    const isAllSelected = selectedCount > 0 && selectedCount === totalCount;
    const isPartialSelected = selectedCount > 0 && selectedCount < totalCount;

    return (
        <div className="batch-action-bar">
            <div className="batch-action-bar-content">
                <div className="batch-action-left">
                    <Checkbox
                        checked={isAllSelected}
                        indeterminate={isPartialSelected}
                        onChange={(e) => {
                            if (e.target.checked) {
                                onSelectAll();
                            } else {
                                onUnselectAll();
                            }
                        }}
                    >
                        <span className="batch-select-text">
                            {isAllSelected ? '取消全选' : '全选'}
                        </span>
                    </Checkbox>
                    <span className="batch-count-text">
                        已选择 <span className="batch-count-number">{selectedCount}</span> 个视频
                    </span>
                </div>

                <div className="batch-action-right">
                    <Space size="middle">
                        <Button
                            type="primary"
                            icon={<CloudDownloadOutlined />}
                            onClick={onBatchDownload}
                            disabled={selectedCount === 0}
                            loading={loading}
                            className="batch-download-btn"
                        >
                            批量下载
                        </Button>
                        <Button
                            icon={<CloseOutlined />}
                            onClick={onExit}
                            className="batch-exit-btn"
                        >
                            退出
                        </Button>
                    </Space>
                </div>
            </div>
        </div>
    );
};

export default BatchActionBar;
