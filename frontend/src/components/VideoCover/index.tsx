import { HTMLProps, useEffect, useMemo, useState } from "react";
import { Empty } from "antd";
import Styles from "./index.module.css";

import * as api from "../../apis/video";
import { useSelector } from "react-redux";
import { RootState } from "../../models";
import { LazyLoadImage } from "react-lazy-load-image-component";


function VideoCover(props: HTMLProps<any>) {
    const { src, ...otherProps } = props
    const { goodBoy } = useSelector((state: RootState) => state.app)
    const [errorMessage, setErrorMessage] = useState<string | null>(null)

    const coverSrc = typeof src === 'string' ? src : ''
    const coverUrl = useMemo(() => {
        if (!coverSrc) return ''
        return api.getVideoCover(coverSrc)
    }, [coverSrc])

    useEffect(() => {
        setErrorMessage(null)
    }, [coverUrl])

    const resolveCoverError = async () => {
        if (!coverUrl) {
            return '封面加载失败'
        }

        try {
            const response = await fetch(coverUrl, { method: 'GET' })
            if (response.status === 422) {
                return '封面地址无效'
            }
            if (response.status === 502) {
                return '封面读取失败（路径无效/源站阻断）'
            }
            if (!response.ok) {
                return `封面加载失败（${response.status}）`
            }

            const contentType = response.headers.get('content-type') || ''
            if (!contentType.startsWith('image/')) {
                return '封面内容无效'
            }
            return '封面加载失败'
        } catch {
            return '封面加载失败（网络异常）'
        }
    }


    return (
        <div className={Styles.videoCoverContainer} {...otherProps}>
            {(coverSrc && goodBoy && !errorMessage) && <div className={Styles.blur} />}
            {coverSrc ? (
                errorMessage ? (
                    <div className={'flex justify-center items-center'}>
                        <Empty description={errorMessage} />
                    </div>
                ) : (
                <LazyLoadImage
                    className={'object-contain'}
                    src={coverUrl}
                    alt={'视频封面'}
                    onError={() => {
                        void resolveCoverError().then(message => {
                            setErrorMessage(message)
                        })
                    }}
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
