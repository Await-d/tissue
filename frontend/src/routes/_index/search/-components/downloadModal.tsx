import { Input, Modal, ModalProps, Tag, Space, Button } from "antd";
import React, { useEffect, useState } from "react";

interface Props extends ModalProps {
    download?: any
    onDownload: (item: any) => void
}

function DownloadModal(props: Props) {

    const { download, onDownload, ...otherProps } = props;
    const [item, setItem] = useState<any>()

    useEffect(() => {
        setItem(download)
    }, [download])

    function renderDownloadTag(label: string, field: string, color: string) {
        return (
            <Tag className={'cursor-pointer'} color={item?.[field] ? color : 'default'}
                variant={item?.[field] ? "outlined" : "borderless"}
                onClick={() => {
                    setItem({ ...item, [field]: !item[field] })
                }}
            >
                {label}
            </Tag>
        )
    }


    return (
        <Modal 
            title={<span style={{ color: '#e8c780', fontSize: '16px', fontWeight: 600 }}>{'确认下载'}</span>} 
            {...otherProps} 
            onOk={() => onDownload(item)}
            styles={{
                mask: { backdropFilter: 'blur(8px)', background: 'rgba(0, 0, 0, 0.6)' },
                content: { 
                    background: '#141416',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    boxShadow: '0 12px 48px rgba(0, 0, 0, 0.6)'
                }
            }}
            okButtonProps={{
                style: {
                    background: 'linear-gradient(135deg, #d4a852 0%, #e8c780 100%)',
                    border: 'none',
                    color: '#0d0d0f',
                    fontWeight: 600
                }
            }}
        >
            <div style={{ 
                padding: '8px 0',
                color: '#f0f0f2',
                fontSize: '15px',
                marginBottom: '12px',
                fontWeight: 500
            }}>
                {item?.name}
            </div>
            <div className={'mt-4'}>
                <Tag style={{ 
                    background: '#222226', 
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    color: '#a0a0a8'
                }}>{item?.size}</Tag>
                <Tag style={{ 
                    background: '#222226', 
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    color: '#a0a0a8'
                }}>{item?.publish_date}</Tag>
            </div>
            <div className={'mt-4'}>
                {renderDownloadTag('高清', 'is_hd', 'red')}
                {renderDownloadTag('中文', 'is_zh', 'blue')}
                {renderDownloadTag('无码', 'is_uncensored', 'green')}
            </div>
            <div className={'mt-4'}>
                <Space.Compact style={{ width: '100%' }}>
                    <Button 
                        disabled
                        style={{
                            background: '#1a1a1d',
                            border: '1px solid rgba(255, 255, 255, 0.08)',
                            color: '#6a6a72'
                        }}
                    >保存路径</Button>
                    <Input
                        placeholder="请输入保存路径（留空则使用默认路径）"
                        value={item?.savepath}
                        onChange={(e) => setItem({ ...item, savepath: e.target.value })}
                        style={{
                            background: '#0d0d0f',
                            border: '1px solid rgba(255, 255, 255, 0.08)',
                            color: '#f0f0f2'
                        }}
                        onFocus={(e) => {
                            e.currentTarget.style.borderColor = '#d4a852';
                            e.currentTarget.style.boxShadow = '0 0 0 2px rgba(212, 168, 82, 0.1)';
                        }}
                        onBlur={(e) => {
                            e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.08)';
                            e.currentTarget.style.boxShadow = 'none';
                        }}
                    />
                </Space.Compact>
            </div>
        </Modal>
    )
}

export default DownloadModal
