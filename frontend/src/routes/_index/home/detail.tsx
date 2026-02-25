import { createFileRoute } from "@tanstack/react-router";
import { Search } from "../search";
import * as api from "../../../apis/home";
import { message } from "antd";


export const Route = createFileRoute('/_index/home/detail')({
    component: Search,
    loaderDeps: ({ search }) => search,
    loader: async ({ deps }) => ({
        data: api.getRankingDetail(deps).then(data => ({
            ...data,
            actors: Array.isArray(data?.actors)
                ? data.actors
                    .map((i: any) => (typeof i === 'string' ? i : i?.name))
                    .filter((name: any) => typeof name === 'string' && name)
                    .join(", ")
                : (typeof data?.actors === 'string' ? data.actors : '')
        })).catch((error) => {
            console.error('获取排行榜详情失败:', error)
            message.error("数据加载失败")
            return undefined
        })
    })
})
