import React from 'react';
import { Space, Button, Typography, Card } from 'antd';
import {
    DeleteOutlined,
    TagOutlined,
    DownloadOutlined,
    StarOutlined,
    CloseOutlined,
    PauseOutlined,
    PlaySquareOutlined
} from '@ant-design/icons';

const { Text } = Typography;

export interface BatchOperationsProps {
    selectedCount: number;
    onDelete?: () => void;
    onEditTags?: () => void;
    onDownload?: () => void;
    onFavorite?: () => void;
    onPause?: () => void;
    onResume?: () => void;
    onCancel: () => void;
    position?: 'top' | 'bottom';
}

/**
 * BatchOperations Component
 *
 * A fixed bar that displays batch operation controls when items are selected.
 *
 * @example
 * ```tsx
 * <BatchOperations
 *   selectedCount={5}
 *   onDelete={() => handleBatchDelete()}
 *   onEditTags={() => setTagModalOpen(true)}
 *   onCancel={() => setSelectedItems([])}
 * />
 * ```
 */
const BatchOperations: React.FC<BatchOperationsProps> = ({
    selectedCount,
    onDelete,
    onEditTags,
    onDownload,
    onFavorite,
    onPause,
    onResume,
    onCancel,
    position = 'bottom'
}) => {
    if (selectedCount === 0) return null;

    return (
        <div
            style={{
                position: 'fixed',
                [position]: 0,
                left: 0,
                right: 0,
                zIndex: 1000,
                padding: '16px',
                display: 'flex',
                justifyContent: 'center',
                pointerEvents: 'none'
            }}
        >
            <Card
                style={{
                    boxShadow: '0 4px 16px rgba(0, 0, 0, 0.15)',
                    borderRadius: '8px',
                    pointerEvents: 'auto',
                    minWidth: '400px'
                }}
                bodyStyle={{
                    padding: '12px 24px'
                }}
            >
                <Space size="large" style={{ width: '100%', justifyContent: 'space-between' }}>
                    <Text strong style={{ fontSize: '16px' }}>
                        已选择 <span style={{ color: '#1890ff' }}>{selectedCount}</span> 项
                    </Text>

                    <Space>
                        {onEditTags && (
                            <Button
                                icon={<TagOutlined />}
                                onClick={onEditTags}
                            >
                                编辑标签
                            </Button>
                        )}

                        {onFavorite && (
                            <Button
                                icon={<StarOutlined />}
                                onClick={onFavorite}
                            >
                                收藏
                            </Button>
                        )}

                        {onDownload && (
                            <Button
                                icon={<DownloadOutlined />}
                                onClick={onDownload}
                            >
                                下载
                            </Button>
                        )}

                        {onPause && (
                            <Button
                                icon={<PauseOutlined />}
                                onClick={onPause}
                            >
                                暂停
                            </Button>
                        )}

                        {onResume && (
                            <Button
                                icon={<PlaySquareOutlined />}
                                onClick={onResume}
                            >
                                恢复
                            </Button>
                        )}

                        {onDelete && (
                            <Button
                                danger
                                icon={<DeleteOutlined />}
                                onClick={onDelete}
                            >
                                删除
                            </Button>
                        )}

                        <Button
                            icon={<CloseOutlined />}
                            onClick={onCancel}
                        >
                            取消
                        </Button>
                    </Space>
                </Space>
            </Card>
        </div>
    );
};

export default BatchOperations;
