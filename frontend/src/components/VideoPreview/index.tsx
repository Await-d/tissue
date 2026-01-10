import { Col, Row, Modal } from "antd";
import PreviewImage from "./previewImage.tsx";
import React, { useState } from "react";
import Lightbox from "yet-another-react-lightbox";
import * as api from "../../apis/video.ts";
import "yet-another-react-lightbox/styles.css";
import "yet-another-react-lightbox/plugins/counter.css";
import { Counter, Zoom } from "yet-another-react-lightbox/plugins";
import Video from "yet-another-react-lightbox/plugins/video";

interface PreviewProps {
    data: any[];
    // 是否为网格模式（默认），否则为轻量模式
    gridMode?: boolean;
    // 网格列配置
    colSpan?: { span: number; lg?: number; md?: number };
}

function Preview(props: PreviewProps) {
    const { data, gridMode = true, colSpan = { span: 8, lg: 3, md: 6 } } = props;
    const [openPreview, setOpenPreview] = useState(false);
    const [previewIndex, setPreviewIndex] = useState(0);

    const slides = data.map((item: any) => (
        item.type === "video" ? (
            {
                type: "video" as const,
                poster: api.getVideoCover(item.thumb),
                sources: [
                    {
                        src: api.getVideoTrailer(item.url),
                        type: "video/mp4",
                    },
                ],
            }
        ) : (
            {
                src: api.getVideoCover(item.url)
            }
        )
    ));

    if (!gridMode) {
        // 轻量模式：只显示第一张图片作为预览
        const firstItem = data[0];
        if (!firstItem) return null;
        
        return (
            <>
                <div 
                    className="cursor-pointer" 
                    onClick={() => {
                        setPreviewIndex(0);
                        setOpenPreview(true);
                    }}
                >
                    <PreviewImage src={firstItem.thumb} type={firstItem.type} />
                </div>
                <Lightbox 
                    open={openPreview}
                    index={previewIndex}
                    close={() => setOpenPreview(false)}
                    plugins={[Counter, Video, Zoom]}
                    video={{
                        muted: true,
                        playsInline: false
                    }}
                    controller={{
                        closeOnPullDown: true
                    }}
                    slides={slides}
                />
            </>
        );
    }

    return (
        <Row gutter={[10, 10]}>
            {data.map((i: any, index: number) => (
                <Col 
                    className={'cursor-pointer flex items-center'} 
                    span={colSpan.span} 
                    lg={colSpan.lg} 
                    md={colSpan.md} 
                    key={i.url}
                    onClick={() => {
                        setPreviewIndex(index);
                        setOpenPreview(true);
                    }}
                >
                    <PreviewImage src={i.thumb} type={i.type} />
                </Col>
            ))}
            <Lightbox 
                open={openPreview}
                index={previewIndex}
                close={() => setOpenPreview(false)}
                plugins={[Counter, Video, Zoom]}
                video={{
                    muted: true,
                    playsInline: false
                }}
                controller={{
                    closeOnPullDown: true
                }}
                slides={slides}
            />
        </Row>
    );
}

// 预览模态框组件
interface PreviewModalProps {
    open: boolean;
    onCancel: () => void;
    previews: any[];
    title?: string;
}

export function PreviewModal(props: PreviewModalProps) {
    const { open, onCancel, previews, title = "预览" } = props;
    
    if (!previews || previews.length === 0) {
        return null;
    }

    return (
        <Modal
            title={title}
            open={open}
            onCancel={onCancel}
            footer={null}
            width={800}
            centered
        >
            <Preview data={previews} colSpan={{ span: 8, lg: 6, md: 8 }} />
        </Modal>
    );
}

export default Preview;
