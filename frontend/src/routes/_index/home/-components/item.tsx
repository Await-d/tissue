/*
 * @Author: Await
 * @Date: 2025-05-24 17:05:38
 * @LastEditors: Await
 * @LastEditTime: 2025-05-24 20:23:02
 * @Description: 请填写简介
 */
import React from "react";
import { Badge, Rate, Space, theme } from "antd";
import VideoCover from "../../../../components/VideoCover";

const { useToken } = theme

function JavDBItem(props: { item: any }) {

    const { token } = useToken();
    const { item } = props;

    function render() {
        return (
            <div className="overflow-hidden rounded-lg transition-shadow hover:shadow-lg hover:border-0"
                style={{ background: token.colorBorderBg, border: `1px solid ${token.colorBorderSecondary}` }}>
                <div>
                    <VideoCover src={item.cover} />
                </div>
                <div className={'p-3'}>
                    <div className={'text-nowrap overflow-y-scroll'}
                        style={{ scrollbarWidth: 'none', fontSize: token.fontSizeHeading5, fontWeight: token.fontWeightStrong }}>
                        {item.num} {item.title || ''}
                    </div>
                    <div className={'flex items-center my-2'}>
                        <Rate disabled allowHalf value={item.rank || 0}></Rate>
                        <div className={'mx-1'}>{item.rank || 0}分</div>
                        <div>由{item.rank_count || 0}人评价</div>
                    </div>
                    <div>{item.publish_date || ''}</div>
                </div>
            </div>
        )
    }

    return (
        item.isZh ? (
            <Badge.Ribbon text={'中文'}>
                {render()}
            </Badge.Ribbon>
        ) : (
            render()
        )
    )
}

export default JavDBItem
