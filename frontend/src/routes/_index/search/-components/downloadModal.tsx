import { Input, Modal, ModalProps, Tag, Space, Button } from "antd";
import React, { useEffect, useState } from "react";
import { useThemeColors } from '../../../../hooks/useThemeColors';

interface Props extends ModalProps {
    download?: any
    onDownload: (item: any) => void
}

function DownloadModal(props: Props) {

    const { download, onDownload, ...otherProps } = props;
    const [item, setItem] = useState<any>()
    const colors = useThemeColors()

    useEffect(() => {
        setItem(download)
    }, [download])

    function renderDownloadTag(label: string, field: string, color: string) {
        return (
            <Tag className={'cursor-pointer'} color={item?.[field] ? color : 'default'}
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
            title={<span style={{ color: colors.goldLight, fontSize: '16px', fontWeight: 600 }}>{'确认下载'}</span>}
            {...otherProps}
            onOk={() => onDownload(item)}
            styles={{
                mask: { backdropFilter: 'blur(8px)', background: colors.modalOverlay },
                content: {
                    background: colors.modalBg,
                    border: `1px solid ${colors.borderPrimary}`,
                    boxShadow: '0 12px 48px rgba(0, 0, 0, 0.6)'
                }
            }}
            okButtonProps={{
                style: {
                    background: colors.goldGradientHover,
                    border: 'none',
                    color: colors.bgBase,
                    fontWeight: 600
                }
            }}
        >
            <div style={{
                padding: '8px 0',
                color: colors.textPrimary,
                fontSize: '15px',
                marginBottom: '12px',
                fontWeight: 500
            }}>
                {item?.name}
            </div>
            <div className={'mt-4'}>
                <Tag style={{
                    background: colors.bgSpotlight,
                    border: `1px solid ${colors.borderPrimary}`,
                    color: colors.textSecondary
                }}>{item?.size}</Tag>
                <Tag style={{
                    background: colors.bgSpotlight,
                    border: `1px solid ${colors.borderPrimary}`,
                    color: colors.textSecondary
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
                            background: colors.bgContainer,
                            border: `1px solid ${colors.borderPrimary}`,
                            color: colors.textTertiary
                        }}
                    >保存路径</Button>
                    <Input
                        placeholder="请输入保存路径（留空则使用默认路径）"
                        value={item?.savepath}
                        onChange={(e) => setItem({ ...item, savepath: e.target.value })}
                        style={{
                            background: colors.bgBase,
                            border: `1px solid ${colors.borderPrimary}`,
                            color: colors.textPrimary
                        }}
                        onFocus={(e) => {
                            e.currentTarget.style.borderColor = colors.goldPrimary;
                            e.currentTarget.style.boxShadow = colors.rgba('gold', 0.1);
                        }}
                        onBlur={(e) => {
                            e.currentTarget.style.borderColor = colors.borderPrimary;
                            e.currentTarget.style.boxShadow = 'none';
                        }}
                    />
                </Space.Compact>
            </div>
        </Modal>
    )
}

export default DownloadModal
