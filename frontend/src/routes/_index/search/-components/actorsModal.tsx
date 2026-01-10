import {SearchOutlined} from "@ant-design/icons";
import {Modal, ModalProps, Segmented, Space} from "antd";
import {useEffect, useState} from "react";
import { useThemeColors } from '../../../../hooks/useThemeColors';

interface Props extends ModalProps {
    actors: any
}

function ActorsModal(props: Props) {

    const {actors, ...otherProps} = props
    const [selectedSite, setSelectedSite] = useState<string>()
    const colors = useThemeColors()

    const sites = actors.map((item: any) => item.website)

    useEffect(() => {
        if (otherProps.open) setSelectedSite(sites[0])
    }, [otherProps.open])

    const items = actors.find((item: any) => item.website === selectedSite)?.items

    return (
        <Modal
            {...otherProps}
            title={'演员'}
            footer={null}
            centered
            styles={{
                mask: { background: colors.modalOverlay },
                content: {
                    background: colors.modalBg,
                    border: `1px solid ${colors.borderPrimary}`,
                }
            }}
        >
            <div className={'text-center'}>
                <Segmented options={sites}
                           value={selectedSite}
                           onChange={value => {
                               setSelectedSite(value)
                           }}/>
            </div>
            {items && (
                <Space wrap className={'mt-2'}>
                    {items.map((item: any, index: number) => (
                        <span key={item.name || index}>
                            <SearchOutlined/>
                            <a>{item.name}</a>
                        </span>
                    ))}
                </Space>
            )}
        </Modal>
    )
}

export default ActorsModal
