import { HTMLProps, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Empty } from "antd";
import Styles from "./index.module.css";

import * as api from "../../apis/video";
import { useSelector } from "react-redux";
import { RootState } from "../../models";
import { LazyLoadImage } from "react-lazy-load-image-component";


function VideoCover(props: HTMLProps<any>) {
    const { src, ...otherProps } = props
    const { goodBoy } = useSelector((state: RootState) => state.app)
    const [failed, setFailed] = useState(false)
    // 重试计数用于给 URL 加 cache-buster，绕开浏览器对失败响应的缓存
    const [retryToken, setRetryToken] = useState(0)
    const retriedRef = useRef(false)

    const coverSrc = typeof src === 'string' ? src : ''
    const baseUrl = useMemo(() => {
        if (!coverSrc) return ''
        return api.getVideoCover(coverSrc)
    }, [coverSrc])

    const coverUrl = useMemo(() => {
        if (!baseUrl) return ''
        return retryToken > 0 ? `${baseUrl}&_r=${retryToken}` : baseUrl
    }, [baseUrl, retryToken])

    useEffect(() => {
        // 换图时重置状态，允许新图再重试一次
        setFailed(false)
        setRetryToken(0)
        retriedRef.current = false
    }, [baseUrl])

    const handleError = useCallback(() => {
        // 只重试一次。后端已有缓存兜底与负缓存，前端反复重试只会放大源站压力。
        if (!retriedRef.current) {
            retriedRef.current = true
            setRetryToken(Date.now())
            return
        }
        setFailed(true)
    }, [])

    return (
        <div className={Styles.videoCoverContainer} {...otherProps}>
            {(coverSrc && goodBoy && !failed) && <div className={Styles.blur} />}
            {coverSrc ? (
                failed ? (
                    <div className={'flex justify-center items-center'}>
                        <Empty description={'封面加载失败'} />
                    </div>
                ) : (
                    <LazyLoadImage
                        key={coverUrl}
                        className={'object-contain'}
                        src={coverUrl}
                        alt={'视频封面'}
                        onError={handleError}
                    />
                )
            ) : (
                <div className={'flex justify-center items-center'}>
                    <Empty description={'暂无图片'} />
                </div>
            )}
        </div>
    )
}

export default VideoCover
