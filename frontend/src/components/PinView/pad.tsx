import {Col, Row, theme} from "antd";
import { useThemeColors } from "../../hooks/useThemeColors";

const {useToken} = theme

function PinPadButton(props: any) {

    const {token} = useToken()
    const colors = useThemeColors()

    return (
        <div className={'flex justify-center items-center '}>
            <button
                className={'size-16 rounded-full text-2xl transition-all duration-300'}
                onClick={() => props.onClick(props.children)}
                style={{
                    border: `solid 2px ${colors.borderGold}`,
                    background: colors.bgContainer,
                    color: colors.textPrimary,
                    boxShadow: colors.shadowSm
                }}
                onMouseEnter={(e) => {
                    e.currentTarget.style.border = `solid 2px ${colors.goldPrimary}`
                    e.currentTarget.style.background = colors.bgSpotlight
                    e.currentTarget.style.boxShadow = `0 0 16px ${colors.rgba('gold', 0.3)}`
                    e.currentTarget.style.transform = 'translateY(-2px)'
                }}
                onMouseLeave={(e) => {
                    e.currentTarget.style.border = `solid 2px ${colors.borderGold}`
                    e.currentTarget.style.background = colors.bgContainer
                    e.currentTarget.style.boxShadow = colors.shadowSm
                    e.currentTarget.style.transform = 'translateY(0)'
                }}
                onMouseDown={(e) => {
                    e.currentTarget.style.transform = 'translateY(0) scale(0.95)'
                    e.currentTarget.style.background = colors.goldPrimary
                    e.currentTarget.style.color = colors.bgBase
                }}
                onMouseUp={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px) scale(1)'
                    e.currentTarget.style.background = colors.bgSpotlight
                    e.currentTarget.style.color = colors.textPrimary
                }}
            >
                {props.children}
            </button>
        </div>
    )
}

interface Props {
    numbers: string[];
    onEnter: (num: string) => void
    onDelete: () => void
}

function PinPad(props: Props) {

    const {numbers, onEnter, onDelete} = props
    const colors = useThemeColors()

    return (
        <Row className={'w-64'} gutter={[20, 20]}>
            {new Array(10).fill(0).map((_, i) => (
                <Col span={8}
                     key={i}
                     offset={((i + 1) % 10) === 0 ? 8 : 0}>
                    <PinPadButton onClick={onEnter}>{(i + 1) % 10}</PinPadButton>
                </Col>
            ))}
            {numbers.length > 0 && (
                <Col span={8}>
                    <button
                        className={'w-full h-full border-none rounded-full transition-all duration-300'}
                        style={{
                            background: 'none',
                            fontSize: 16,
                            color: colors.goldPrimary,
                            fontWeight: 500
                        }}
                        onClick={onDelete}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.color = colors.goldLight
                            e.currentTarget.style.transform = 'scale(1.1)'
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.color = colors.goldPrimary
                            e.currentTarget.style.transform = 'scale(1)'
                        }}
                    >
                        删除
                    </button>
                </Col>
            )}
        </Row>
    )
}


export default PinPad
