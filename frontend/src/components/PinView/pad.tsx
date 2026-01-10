import {Col, Row, theme} from "antd";

const {useToken} = theme

function PinPadButton(props: any) {

    const {token} = useToken()

    return (
        <div className={'flex justify-center items-center '}>
            <button
                className={'size-16 rounded-full text-2xl transition-all duration-300'}
                onClick={() => props.onClick(props.children)}
                style={{
                    border: `solid 2px rgba(212, 168, 82, 0.3)`,
                    background: "#1a1a1d",
                    color: '#f0f0f2',
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)'
                }}
                onMouseEnter={(e) => {
                    e.currentTarget.style.border = 'solid 2px #d4a852'
                    e.currentTarget.style.background = '#222226'
                    e.currentTarget.style.boxShadow = '0 0 16px rgba(212, 168, 82, 0.3)'
                    e.currentTarget.style.transform = 'translateY(-2px)'
                }}
                onMouseLeave={(e) => {
                    e.currentTarget.style.border = 'solid 2px rgba(212, 168, 82, 0.3)'
                    e.currentTarget.style.background = '#1a1a1d'
                    e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.3)'
                    e.currentTarget.style.transform = 'translateY(0)'
                }}
                onMouseDown={(e) => {
                    e.currentTarget.style.transform = 'translateY(0) scale(0.95)'
                    e.currentTarget.style.background = '#d4a852'
                    e.currentTarget.style.color = '#0d0d0f'
                }}
                onMouseUp={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px) scale(1)'
                    e.currentTarget.style.background = '#222226'
                    e.currentTarget.style.color = '#f0f0f2'
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
                            color: '#d4a852',
                            fontWeight: 500
                        }}
                        onClick={onDelete}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.color = '#e8c780'
                            e.currentTarget.style.transform = 'scale(1.1)'
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.color = '#d4a852'
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
