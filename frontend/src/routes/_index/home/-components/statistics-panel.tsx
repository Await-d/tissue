import React from "react";
import { Card, Col, Row, Statistic, theme } from "antd";
import {
    VideoCameraOutlined,
    RiseOutlined,
    FireOutlined,
    HeartOutlined
} from "@ant-design/icons";

const { useToken } = theme;

interface StatisticsPanelProps {
    totalVideos: number;
    todayNew: number;
    weeklyHot: number;
    favorites: number;
    loading?: boolean;
}

/**
 * Statistics Panel Component
 * Displays overview cards with key metrics
 *
 * @example
 * <StatisticsPanel
 *   totalVideos={1234}
 *   todayNew={12}
 *   weeklyHot={89}
 *   favorites={45}
 * />
 */
function StatisticsPanel(props: StatisticsPanelProps) {
    const { totalVideos, todayNew, weeklyHot, favorites, loading = false } = props;
    const { token } = useToken();

    const statistics = [
        {
            title: "总视频数",
            value: totalVideos,
            icon: <VideoCameraOutlined style={{ fontSize: 24 }} />,
            gradient: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            color: "#667eea"
        },
        {
            title: "今日新增",
            value: todayNew,
            icon: <RiseOutlined style={{ fontSize: 24 }} />,
            gradient: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
            color: "#f5576c"
        },
        {
            title: "本周热门",
            value: weeklyHot,
            icon: <FireOutlined style={{ fontSize: 24 }} />,
            gradient: "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
            color: "#fa709a"
        },
        {
            title: "收藏数量",
            value: favorites,
            icon: <HeartOutlined style={{ fontSize: 24 }} />,
            gradient: "linear-gradient(135deg, #30cfd0 0%, #330867 100%)",
            color: "#30cfd0"
        }
    ];

    return (
        <Row gutter={[16, 16]} className="mb-6">
            {statistics.map((stat, index) => (
                <Col key={index} xs={12} sm={12} md={6} lg={6}>
                    <Card
                        loading={loading}
                        bordered={false}
                        className="transition-all duration-300 hover:shadow-lg hover:-translate-y-1"
                        style={{
                            background: stat.gradient,
                            borderRadius: token.borderRadiusLG,
                            overflow: "hidden"
                        }}
                        bodyStyle={{ padding: "20px" }}
                    >
                        <div className="flex items-center justify-between">
                            <div>
                                <div
                                    className="text-white opacity-90 mb-2"
                                    style={{ fontSize: token.fontSize }}
                                >
                                    {stat.title}
                                </div>
                                <Statistic
                                    value={stat.value}
                                    valueStyle={{
                                        color: "#fff",
                                        fontSize: token.fontSizeHeading3,
                                        fontWeight: token.fontWeightStrong
                                    }}
                                />
                            </div>
                            <div
                                className="flex items-center justify-center"
                                style={{
                                    width: 56,
                                    height: 56,
                                    borderRadius: "50%",
                                    backgroundColor: "rgba(255, 255, 255, 0.2)",
                                    color: "#fff"
                                }}
                            >
                                {stat.icon}
                            </div>
                        </div>
                    </Card>
                </Col>
            ))}
        </Row>
    );
}

export default StatisticsPanel;
