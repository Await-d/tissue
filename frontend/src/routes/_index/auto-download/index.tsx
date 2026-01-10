import React, { useState } from 'react'
import { Tabs, Card } from 'antd'
import { SettingOutlined, UnorderedListOutlined, BarChartOutlined } from '@ant-design/icons'
import { createFileRoute } from '@tanstack/react-router'
import AutoDownloadRules from './rules'
import AutoDownloadSubscriptions from './subscriptions'
import './style.css'

function AutoDownload() {
  const [activeTab, setActiveTab] = useState('rules')

  const tabItems = [
    {
      key: 'rules',
      label: (
        <span className="tab-label">
          <SettingOutlined />
          规则管理
        </span>
      ),
      children: <AutoDownloadRules />
    },
    {
      key: 'subscriptions',
      label: (
        <span className="tab-label">
          <UnorderedListOutlined />
          订阅记录
        </span>
      ),
      children: <AutoDownloadSubscriptions />
    }
  ]

  return (
    <div className="auto-download-wrapper">
      <Card className="dark-card auto-download-card">
        <div className="page-header">
          <h2 className="page-header-title">
            <BarChartOutlined className="page-header-icon" />
            智能自动下载
          </h2>
          <p className="page-header-description">
            根据评分、评论数等条件自动筛选并订阅符合要求的作品
          </p>
        </div>

        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={tabItems}
          size="large"
          className="dark-tabs"
        />
      </Card>
    </div>
  )
}

export const Route = createFileRoute('/_index/auto-download/')({
  component: AutoDownload
})

export default AutoDownload