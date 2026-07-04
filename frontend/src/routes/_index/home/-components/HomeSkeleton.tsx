import { Col, Row } from "antd";
import { useThemeColors } from "../../../../hooks/useThemeColors";

export default function HomeSkeleton() {
    const colors = useThemeColors();

    return (
        <Row className={'mt-2'} gutter={[16, 16]}>
            {[...Array(8)].map((_, index) => (
                <Col
                    key={index}
                    span={24}
                    md={12}
                    lg={6}
                    className={`tissue-animate-in tissue-stagger-${(index % 8) + 1}`}
                >
                    <div style={{
                        background: colors.bgContainer,
                        borderRadius: '16px',
                        overflow: 'hidden',
                        border: `1px solid ${colors.borderSecondary}`,
                        boxShadow: `0 4px 12px ${colors.rgba('black', 0.15)}`,
                    }}>
                        {/* 封面骨架 */}
                        <div style={{
                            aspectRatio: '16/10',
                            position: 'relative',
                            overflow: 'hidden',
                            background: colors.bgSpotlight,
                        }}>
                            <div style={{
                                position: 'absolute',
                                inset: 0,
                                background: `linear-gradient(90deg, transparent 0%, ${colors.rgba('gold', 0.08)} 50%, transparent 100%)`,
                                backgroundSize: '200% 100%',
                                animation: 'tissue-shimmer 2s ease-in-out infinite',
                            }} />
                            <div style={{
                                position: 'absolute', top: 14, left: 14, width: 60, height: 28,
                                background: colors.rgba('gold', 0.15), borderRadius: 10,
                            }} />
                        </div>

                        {/* 内容骨架 */}
                        <div style={{ padding: '16px 18px' }}>
                            <div style={{
                                width: '40%', height: 20, background: colors.rgba('gold', 0.12),
                                borderRadius: 6, marginBottom: 10, position: 'relative', overflow: 'hidden',
                            }}>
                                <div style={{
                                    position: 'absolute', inset: 0,
                                    background: `linear-gradient(90deg, transparent 0%, ${colors.rgba('white', 0.08)} 50%, transparent 100%)`,
                                    backgroundSize: '200% 100%',
                                    animation: 'tissue-shimmer 2s ease-in-out infinite 0.2s',
                                }} />
                            </div>
                            {[1, 0.75].map((w, i) => (
                                <div key={i} style={{
                                    width: `${w * 100}%`, height: 16, background: colors.bgSpotlight,
                                    borderRadius: 6, marginBottom: 8, position: 'relative', overflow: 'hidden',
                                }}>
                                    <div style={{
                                        position: 'absolute', inset: 0,
                                        background: `linear-gradient(90deg, transparent 0%, ${colors.rgba('white', 0.05)} 50%, transparent 100%)`,
                                        backgroundSize: '200% 100%',
                                        animation: `tissue-shimmer 2s ease-in-out infinite ${0.4 + i * 0.2}s`,
                                    }} />
                                </div>
                            ))}
                            <div style={{
                                display: 'flex', justifyContent: 'space-between', paddingTop: 12,
                                borderTop: `1px solid ${colors.borderSecondary}`,
                            }}>
                                {[0.5, 0.25].map((w, i) => (
                                    <div key={i} style={{
                                        width: `${w * 100}%`, height: 14, background: colors.bgSpotlight,
                                        borderRadius: 6, position: 'relative', overflow: 'hidden',
                                    }}>
                                        <div style={{
                                            position: 'absolute', inset: 0,
                                            background: `linear-gradient(90deg, transparent 0%, ${colors.rgba('white', 0.05)} 50%, transparent 100%)`,
                                            backgroundSize: '200% 100%',
                                            animation: `tissue-shimmer 2s ease-in-out infinite ${0.8 + i * 0.2}s`,
                                        }} />
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </Col>
            ))}
        </Row>
    );
}
