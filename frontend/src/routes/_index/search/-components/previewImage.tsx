import React from "react";
import * as api from "../../../../apis/video.ts";
import Styles from "./previewImage.module.css";
import {useSelector} from "react-redux";
import {RootState} from "../../../../models";
import {PlayCircleTwoTone} from "@ant-design/icons";
import {theme} from "antd";
import {LazyLoadImage} from "react-lazy-load-image-component";

const {useToken} = theme

const PREVIEW_IMAGE_MAX_HEIGHT = 80

interface Props extends React.ComponentProps<any> {
    src: string,
    type: string
}

function PreviewImage(props: Props) {
    const {src, type} = props;
    const {goodBoy} = useSelector((state: RootState) => state.app)
    const {token} = useToken()

    return (
        <div className={Styles.container}>
            {goodBoy && <div className={Styles.blur}/>}
            {type === 'video' && (
                <div className={'absolute z-50 top-0 bottom-0 left-0 right-0 flex justify-center items-center'}>
                    <PlayCircleTwoTone style={{color: token.colorPrimary}} className={'text-4xl'}/>
                </div>
            )}
            <LazyLoadImage className={'w-full h-auto align-bottom object-contain'} style={{maxHeight: PREVIEW_IMAGE_MAX_HEIGHT}} src={api.getVideoCover(src)}
                 alt=""/>
        </div>
    )
}

export default PreviewImage;
