import React, { useState } from 'react'
import { Tabs, Card } from 'antd'
import { SettingOutlined, UnorderedListOutlined, BarChartOutlined } from '@ant-design/icons'
import AutoDownloadRules from './rules'
import AutoDownloadSubscriptions from './subscriptions'

const AutoDownload: React.FC = () => {
  const [activeTab, setActiveTab] = useState('rules')

  const tabItems = [
    {
      key: 'rules',
      label: (
        <span>
          <SettingOutlined />
          规则管理
        </span>
      ),
      children: <AutoDownloadRules />
    },
    {
      key: 'subscriptions',
      label: (
        <span>
          <UnorderedListOutlined />
          订阅记录
        </span>
      ),
      children: <AutoDownloadSubscriptions />
    }
  ]

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <div style={{ marginBottom: '16px' }}>
          <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 'bold' }}>
            <BarChartOutlined style={{ marginRight: '8px' }} />
            智能自动下载
          </h2>
          <p style={{ margin: '8px 0 0 0', color: '#666' }}>
            根据评分、评论数等条件自动筛选并订阅符合要求的作品
          </p>
        </div>
        
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={tabItems}
          size="large"
        />
      </Card>
    </div>
  )
}

export default AutoDownload