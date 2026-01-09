import React, { useState, useEffect } from 'react';
import { Modal, Tag, Space, Input, Button, message } from 'antd';
import { PlusOutlined, CloseOutlined } from '@ant-design/icons';

export interface TagEditModalProps {
    open: boolean;
    selectedItems: any[];
    onCancel: () => void;
    onOk: (tags: string[]) => void;
}

/**
 * TagEditModal Component
 *
 * Modal for batch editing tags on selected items.
 * Allows adding and removing tags that will be applied to all selected items.
 *
 * @example
 * ```tsx
 * <TagEditModal
 *   open={tagModalOpen}
 *   selectedItems={selectedVideos}
 *   onCancel={() => setTagModalOpen(false)}
 *   onOk={(tags) => handleBatchUpdateTags(tags)}
 * />
 * ```
 */
const TagEditModal: React.FC<TagEditModalProps> = ({
    open,
    selectedItems,
    onCancel,
    onOk
}) => {
    const [tags, setTags] = useState<string[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [inputVisible, setInputVisible] = useState(false);

    // Extract existing tags from selected items
    useEffect(() => {
        if (open && selectedItems.length > 0) {
            const allTags = new Set<string>();
            selectedItems.forEach(item => {
                if (item.tags && Array.isArray(item.tags)) {
                    item.tags.forEach((tag: string) => allTags.add(tag));
                }
            });
            setTags(Array.from(allTags));
        }
    }, [open, selectedItems]);

    const handleAddTag = () => {
        if (inputValue && !tags.includes(inputValue)) {
            setTags([...tags, inputValue]);
            setInputValue('');
            setInputVisible(false);
        } else if (tags.includes(inputValue)) {
            message.warning('标签已存在');
        }
    };

    const handleRemoveTag = (tagToRemove: string) => {
        setTags(tags.filter(tag => tag !== tagToRemove));
    };

    const handleOk = () => {
        onOk(tags);
        setInputValue('');
        setInputVisible(false);
    };

    const handleCancel = () => {
        onCancel();
        setInputValue('');
        setInputVisible(false);
    };

    return (
        <Modal
            title="批量编辑标签"
            open={open}
            onCancel={handleCancel}
            onOk={handleOk}
            width={600}
            okText="确定"
            cancelText="取消"
        >
            <div style={{ marginBottom: 16 }}>
                <div style={{ marginBottom: 8, color: '#666' }}>
                    已选择 {selectedItems.length} 项
                </div>
                <div style={{ marginBottom: 16, color: '#999', fontSize: '12px' }}>
                    添加或删除标签将应用到所有选中的项目
                </div>
            </div>

            <div
                style={{
                    border: '1px solid #d9d9d9',
                    borderRadius: '4px',
                    padding: '16px',
                    minHeight: '120px',
                    backgroundColor: '#fafafa'
                }}
            >
                <Space size={[8, 8]} wrap>
                    {tags.map(tag => (
                        <Tag
                            key={tag}
                            closable
                            onClose={() => handleRemoveTag(tag)}
                            style={{ fontSize: '14px', padding: '4px 8px' }}
                        >
                            {tag}
                        </Tag>
                    ))}

                    {inputVisible ? (
                        <Input
                            type="text"
                            size="small"
                            style={{ width: 120 }}
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onBlur={handleAddTag}
                            onPressEnter={handleAddTag}
                            autoFocus
                        />
                    ) : (
                        <Tag
                            onClick={() => setInputVisible(true)}
                            style={{
                                background: '#fff',
                                borderStyle: 'dashed',
                                cursor: 'pointer',
                                fontSize: '14px',
                                padding: '4px 8px'
                            }}
                        >
                            <PlusOutlined /> 添加标签
                        </Tag>
                    )}
                </Space>
            </div>

            <div style={{ marginTop: 16, color: '#999', fontSize: '12px' }}>
                提示: 点击标签右侧的 × 可以删除标签
            </div>
        </Modal>
    );
};

export default TagEditModal;
