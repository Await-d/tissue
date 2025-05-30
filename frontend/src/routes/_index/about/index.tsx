import Logo from "../../../assets/logo.svg";
import { Card, Space, Tag, Typography, Divider } from "antd";
import { useResponsive } from "ahooks";
import { useSelector } from "react-redux";
import { RootState } from "../../../models";
import { DockerOutlined, GithubOutlined } from "@ant-design/icons";
import { createFileRoute } from "@tanstack/react-router";

const { Paragraph, Link } = Typography;

export const Route = createFileRoute('/_index/about/')({
    component: About
})

function About() {

    const responsive = useResponsive()
    const { versions } = useSelector((state: RootState) => state.auth)


    return (
        <Card>
            <div className="flex flex-col justify-center items-center">
                <img className={'h-20'} src={Logo} alt="" />
                <div>
                    <span>当前版本：{versions?.current}</span>
                    {versions?.hasNew && (
                        <Tag className={'ml-2'} color={'red'}>新版本：{versions?.latest}</Tag>
                    )}
                </div>
                <Space size={"large"} className={'text-4xl mt-4'}>
                    <div className={'cursor-pointer'} onClick={() => window.open('https://github.com/Await-d/tissue')}>
                        <GithubOutlined /></div>
                    <div className={'cursor-pointer'}
                        onClick={() => window.open('https://hub.docker.com/r/chris2s/tissue-plus')}><DockerOutlined /></div>
                </Space>
                {responsive.md ? (
                    <Space align={"center"} wrap={true} className={'mt-4'}>
                        <img src="https://img.shields.io/github/license/Await-d/tissue" alt="" />
                        <img src="https://img.shields.io/docker/v/chris2s/tissue-plus/latest" alt="" />
                        <img src="https://img.shields.io/docker/image-size/chris2s/tissue-plus/latest" alt="" />
                        <img src="https://img.shields.io/github/actions/workflow/status/Await-d/tissue/build.yml"
                            alt="" />
                    </Space>
                ) : (
                    <>
                        <Space align={"center"} wrap={true} className={'mt-4'}>
                            <img src="https://img.shields.io/github/license/Await-d/tissue" alt="" />
                            <img src="https://img.shields.io/docker/v/chris2s/tissue-plus" alt="" />
                        </Space>
                        <Space align={"center"} wrap={true} className={'mt-2'}>
                            <img src="https://img.shields.io/docker/image-size/chris2s/tissue-plus" alt="" />
                            <img src="https://img.shields.io/github/actions/workflow/status/Await-d/tissue/build.yml"
                                alt="" />
                        </Space>
                    </>
                )}
                <div className={'text-center mt-4'}>
                    老师教材刮削工具，提供海报下载、元数据匹配等功能，使教材能够在Jellyfin、Emby、Kodi等工具里装订成册，便于学习。
                </div>
                <Divider />
                <Paragraph className="text-center">
                    本项目基于 <Link href="https://github.com/chris-2s/tissue" target="_blank">chris-2s/tissue</Link> 进行二次开发，感谢原作者的贡献。
                </Paragraph>
                <div className={'text-center mt-4'}>
                    本软件所涉及的数据均通过互联网爬取获取，数据版权归原作者或发布平台所有。
                </div>
                <div className={'text-center mt-4'}>
                    本软件仅作为数据展示与整合的工具，并不提供任何数据的原创或拥有权。
                </div>
            </div>
        </Card>
    )
}

