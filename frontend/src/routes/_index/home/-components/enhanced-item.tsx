import React, { useState } from "react";
import { Badge, Rate, Space, theme, Tooltip, Button } from "antd";
import VideoCover from "../../../../components/VideoCover";
import { SearchOutlined, HeartOutlined, HeartFilled, DownloadOutlined } from "@ant-design/icons";
import { useRouter } from "@tanstack/react-router";
import FavoriteButton from "../../../../components/FavoriteButton";

const { useToken } = theme;

interface VideoItemProps {
    item: any;
    showRank?: boolean;
    rank?: number;
    onFavorite?: (item: any) => void;
    onDownload?: (item: any) => void;
}

/**
 * Enhanced Video Item Card Component
 * Features:
 * - Hover scale effect
 * - Video tags (HD/Chinese/Uncensored)
 * - Quick favorite button
 * - Quick download button
 * - Ranking display
 *
 * @example
 * <EnhancedVideoItem
 *   item={videoData}
 *   showRank={true}
 *   rank={1}
 *   onFavorite={(item) => console.log('Favorited:', item)}
 *   onDownload={(item) => console.log('Download:', item)}
 * />
 */
function EnhancedVideoItem(props: VideoItemProps) {
    const { token } = useToken();
    const { item, showRank = false, rank, onFavorite, onDownload } = props;
    const { navigate } = useRouter();
    const [isHovered, setIsHovered] = useState(false);

    const handleDownload = (event: React.MouseEvent) => {
        event.stopPropagation();
        onDownload?.(item);
    };

    const renderTags = () => {
        const tags = [];

        if (item.isHd) {
            tags.push(
                <span
                    key="hd"
                    className="px-2 py-0.5 text-xs rounded"
                    style={{
                        backgroundColor: "rgba(255, 77, 79, 0.1)",
                        color: "#ff4d4f",
                        border: "1px solid rgba(255, 77, 79, 0.3)"
                    }}
                >
                    HD
                </span>
            );
        }

        if (item.isZh) {
            tags.push(
                <span
                    key="zh"
                    className="px-2 py-0.5 text-xs rounded"
                    style={{
                        backgroundColor: "rgba(82, 196, 26, 0.1)",
                        color: "#52c41a",
                        border: "1px solid rgba(82, 196, 26, 0.3)"
                    }}
                >
                    中文
                </span>
            );
        }

        if (item.isUncensored) {
            tags.push(
                <span
                    key="uncensored"
                    className="px-2 py-0.5 text-xs rounded"
                    style={{
                        backgroundColor: "rgba(250, 173, 20, 0.1)",
                        color: "#faad14",
                        border: "1px solid rgba(250, 173, 20, 0.3)"
                    }}
                >
                    无码
                </span>
            );
        }

        return tags.length > 0 ? (
            <div className="flex gap-1 mb-2 flex-wrap">{tags}</div>
        ) : null;
    };

    const renderRankBadge = () => {
        if (!showRank || rank === undefined) return null;

        let badgeColor = token.colorPrimary;
        if (rank === 1) badgeColor = "#FFD700"; // Gold
        else if (rank === 2) badgeColor = "#C0C0C0"; // Silver
        else if (rank === 3) badgeColor = "#CD7F32"; // Bronze

        return (
            <div
                className="absolute top-2 left-2 z-10 flex items-center justify-center"
                style={{
                    width: 32,
                    height: 32,
                    borderRadius: "50%",
                    backgroundColor: badgeColor,
                    color: "#fff",
                    fontWeight: token.fontWeightStrong,
                    fontSize: token.fontSizeLG,
                    boxShadow: "0 2px 8px rgba(0,0,0,0.15)"
                }}
            >
                {rank}
            </div>
        );
    };

    return (
        <div
            className="overflow-hidden rounded-lg transition-all duration-300 cursor-pointer"
            style={{
                background: token.colorBorderBg,
                border: `1px solid ${token.colorBorderSecondary}`,
                transform: isHovered ? "scale(1.03)" : "scale(1)",
                boxShadow: isHovered
                    ? "0 8px 24px rgba(0,0,0,0.12)"
                    : "0 2px 8px rgba(0,0,0,0.06)"
            }}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            <div className="relative">
                {renderRankBadge()}
                <VideoCover src={item.cover} />

                {/* Action buttons overlay */}
                <div
                    className="absolute top-2 right-2 z-10 transition-opacity duration-300 flex gap-2"
                    style={{ opacity: isHovered ? 1 : 0 }}
                >
                    <FavoriteButton
                        videoNum={item.num}
                        videoTitle={item.title}
                        videoCover={item.cover}
                        shape="circle"
                        type="primary"
                        style={{
                            backgroundColor: "rgba(0,0,0,0.5)",
                            borderColor: "transparent"
                        }}
                        onFavoriteChange={(isFavorited) => {
                            if (isFavorited) {
                                onFavorite?.(item);
                            }
                        }}
                    />
                    {onDownload && (
                        <Button
                            type="primary"
                            shape="circle"
                            icon={<DownloadOutlined />}
                            onClick={handleDownload}
                            style={{
                                backgroundColor: "rgba(0,0,0,0.5)",
                                borderColor: "transparent"
                            }}
                        />
                    )}
                </div>
            </div>

            <div className="p-3">
                {renderTags()}

                <div
                    className="text-nowrap overflow-x-auto mb-2"
                    style={{
                        scrollbarWidth: "none",
                        fontSize: token.fontSizeHeading5,
                        fontWeight: token.fontWeightStrong
                    }}
                >
                    {item.num} {item.title}
                </div>

                <div className="flex items-center my-2">
                    <Rate disabled allowHalf value={item.rank} style={{ fontSize: 14 }} />
                    <div className="mx-1" style={{ fontSize: token.fontSizeSM }}>
                        {item.rank}分
                    </div>
                    <div style={{ fontSize: token.fontSizeSM, color: token.colorTextSecondary }}>
                        ({item.rank_count}人)
                    </div>
                </div>

                <div className="flex items-center justify-between">
                    <div style={{ fontSize: token.fontSizeSM, color: token.colorTextSecondary }}>
                        {item.publish_date}
                    </div>
                    <Tooltip title="搜索">
                        <Button
                            type="text"
                            size="small"
                            icon={<SearchOutlined />}
                            onClick={(event) => {
                                event.stopPropagation();
                                navigate({
                                    to: "/search",
                                    search: { num: item.num }
                                });
                            }}
                        />
                    </Tooltip>
                </div>
            </div>
        </div>
    );
}

export default EnhancedVideoItem;
