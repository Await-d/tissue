import { Button, Col, message, Row, Space, theme, ConfigProvider } from "antd";
import Logo from "../../assets/logo.svg";
import PinPad from "./pad.tsx";
import React, { useState } from "react";
import { useResponsive } from "ahooks";
import { CloseOutlined, EyeInvisibleOutlined, EyeOutlined } from "@ant-design/icons";
import { sha256 } from "js-sha256";
import { createPortal } from "react-dom";
import { useDispatch, useSelector } from "react-redux";
import { Dispatch, RootState } from "../../models";
import { useThemeColors } from "../../hooks/useThemeColors";

const { useToken } = theme

export enum PinMode {
    verify,
    setting
}

interface Props {
    pin: string | null
    onClose: () => void;
    mode: PinMode
}

function PinView(props: Props) {

    const { pin, mode, onClose } = props;
    const { token } = useToken()
    const colors = useThemeColors()
    const [numbers, setNumbers] = useState<string[]>([])
    const [repeatNumbers, setRepeatNumbers] = useState<string[]>([])
    const [errorMessage, setErrorMessage] = useState<string>()
    const responsive = useResponsive()

    const goodBoy = useSelector((state: RootState) => state.app?.goodBoy)
    const dispatch = useDispatch<Dispatch>().app

    function onEnter(num: string) {
        const newNumbers = [...numbers, num]
        setNumbers(newNumbers)
        setErrorMessage(undefined)

        if (newNumbers.length === 4) {
            if (mode === PinMode.verify) {
                const hash = sha256.create()
                hash.update(newNumbers.join(''))
                if (pin === hash.hex()) {
                    onClose()
                } else {
                    setNumbers([])
                    setErrorMessage('密码错误')
                }
            } else if (mode === PinMode.setting) {
                if (repeatNumbers.length === 0) {
                    setRepeatNumbers(newNumbers)
                    setNumbers([])
                } else {
                    if (repeatNumbers.join('') !== newNumbers.join('')) {
                        setErrorMessage('两次输入密码不匹配')
                        setRepeatNumbers([])
                        setNumbers([])
                    } else {
                        const hash = sha256.create()
                        hash.update(newNumbers.join(''))
                        dispatch.setPin(hash.hex())
                        message.success('密码设置成功')
                        onClose()
                    }
                }
            }
        }
    }

    function onDelete() {
        if (numbers.length >= 1) {
            numbers.pop()
            setNumbers([...numbers])
        }
    }

    function renderRemark() {
        return (mode === PinMode.setting) && (
            <div className={'flex flex-col items-center mt-8 font-light text-xs'} style={{ color: colors.textTertiary }}>
                <div style={{ marginBottom: '8px' }}>
                    密码仅当前设备有效，退出登录即可清空密码
                </div>
                <div>
                    由于系统及兼容性限制，可靠性无法保证
                </div>
            </div>
        )
    }

    return createPortal(
        <ConfigProvider
            theme={{
                components: {
                    Button: {
                        colorPrimary: colors.goldPrimary,
                        colorPrimaryHover: colors.goldLight,
                        colorPrimaryActive: colors.goldDark,
                        colorBgContainer: colors.bgContainer,
                        colorBorder: colors.borderPrimary,
                        colorText: colors.textPrimary,
                        defaultBg: colors.bgContainer,
                        defaultBorderColor: colors.borderPrimary,
                        defaultColor: colors.textSecondary,
                    }
                }
            }}
        >
            <div
                className={'fixed top-0 right-0 bottom-0 left-0 z-[1000]'}
                style={{
                    background: colors.bgBase,
                    backdropFilter: 'blur(8px)'
                }}
            >
                <div className={'h-full w-full flex justify-center items-center'}>
                    <Row gutter={[80, 0]}>
                        <Col span={24} md={12}>
                            <div className={'h-full flex flex-col items-center justify-center'}>
                                <img className={'h-20'} src={Logo} alt="" style={{ filter: 'drop-shadow(0 0 20px rgba(212, 168, 82, 0.3))' }} />
                                <div style={{ color: colors.textPrimary, fontSize: '16px', marginTop: '24px', fontWeight: 500 }}>
                                    {repeatNumbers.length > 0 ? (
                                        '请再次输入密码 '
                                    ) : (
                                        '请输入密码'
                                    )}
                                </div>
                                <Space className={'flex justify-center mt-8'}>
                                    {new Array(4).fill(0).map((_, i) => (
                                        <Button
                                            shape={"circle"}
                                            size={"small"}
                                            key={i}
                                            type={numbers.length > i ? 'primary' : 'default'}
                                            style={{
                                                background: numbers.length > i ? colors.goldPrimary : colors.bgContainer,
                                                borderColor: numbers.length > i ? colors.goldPrimary : colors.borderPrimary,
                                                boxShadow: numbers.length > i ? `0 0 12px ${colors.rgba('gold', 0.4)}` : 'none',
                                                transition: 'all 0.3s ease'
                                            }}
                                        />
                                    ))}
                                </Space>
                                <div
                                    className={'h-14 flex items-center'}
                                    style={{
                                        color: colors.error,
                                        fontWeight: 500,
                                        textShadow: `0 0 8px ${colors.rgba('black', 0.3)}`
                                    }}
                                >
                                    {errorMessage}
                                </div>
                                {responsive.md && (
                                    renderRemark()
                                )}
                            </div>
                        </Col>
                        <Col span={24} md={12}>
                            <div className={'flex flex-col items-center justify-center'}>
                                <PinPad numbers={numbers} onEnter={onEnter} onDelete={onDelete} />
                            </div>
                            {!responsive.md && (
                                renderRemark()
                            )}
                        </Col>
                    </Row>
                </div>
                <div className={'fixed'} style={{
                    top: 'calc(10px + env(safe-area-inset-top, 0))',
                    right: 'calc(20px + env(safe-area-inset-right, 0))'
                }}>
                    {mode === PinMode.setting ? (
                        <Button
                            shape={'circle'}
                            icon={<CloseOutlined />}
                            onClick={() => onClose()}
                            style={{
                                background: colors.bgContainer,
                                borderColor: colors.borderPrimary,
                                color: colors.textPrimary
                            }}
                        />
                    ) : (
                        <div
                            className={'mr-2'}
                            style={{
                                fontSize: token.sizeLG,
                                color: colors.goldPrimary,
                                cursor: 'pointer',
                                transition: 'all 0.3s ease'
                            }}
                            onClick={() => dispatch.setGoodBoy(!goodBoy)}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.color = colors.goldLight
                                e.currentTarget.style.transform = 'scale(1.1)'
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.color = colors.goldPrimary
                                e.currentTarget.style.transform = 'scale(1)'
                            }}
                        >
                            {goodBoy ? (<EyeInvisibleOutlined />) : (<EyeOutlined />)}
                        </div>
                    )}
                </div>
            </div>
        </ConfigProvider>, document.body
    )
}


export default PinView;
