import React from "react";
import { Skeleton, Card } from "antd";

/**
 * Video Card Skeleton Loading Component
 * Provides a placeholder while video cards are loading
 *
 * @example
 * <VideoCardSkeleton count={8} />
 */
function VideoCardSkeleton({ count = 8 }: { count?: number }) {
    return (
        <>
            {Array.from({ length: count }).map((_, index) => (
                <div key={index} className="col-span-1">
                    <Card bordered={false}>
                        <Skeleton.Image
                            active
                            style={{ width: "100%", height: 200 }}
                        />
                        <Skeleton
                            active
                            paragraph={{ rows: 3 }}
                            className="mt-3"
                        />
                    </Card>
                </div>
            ))}
        </>
    );
}

export default VideoCardSkeleton;
