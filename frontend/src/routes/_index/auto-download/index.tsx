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
    <div className="auto-download-wrapper animate-fade-in" style={{ padding: '24px' }}>
      <Card
        className="dark-card auto-download-card"
        style={{
          background: '#141416',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: 8
        }}
      >
        <div className="page-header" style={{ marginBottom: '24px' }}>
          <h2 style={{ 
            margin: 0, 
            fontSize: '20px', 
            fontWeight: 600,
            color: '#f0f0f2',
            display: 'flex',
            alignItems: 'center',
            gap: 10
          }}>
            <BarChartOutlined style={{ color: '#d4a852' }} />
            智能自动下载
          </h2>
          <p style={{ 
            margin: '8px 0 0 0', 
            color: '#a0a0a8',
            fontSize: 14
          }}>
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