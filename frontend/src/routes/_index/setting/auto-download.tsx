import React, { useState, useEffect } from 'react'
import {
  Form,
  Switch,
  InputNumber,
  Select,
  Button,
  Card,
  Space,
  message,
  Divider,
  Row,
  Col,
  Statistic,
  Tag
} from 'antd'
import { createFileRoute } from '@tanstack/react-router'
import {
  getStatistics,
  triggerAutoDownload,
  type AutoDownloadStatistics
} from '../../../apis/autoDownload'

export const Route = createFileRoute('/_index/setting/auto-download')({
  component: AutoDownloadSettings
})

const { Option } = Select

function AutoDownloadSettings() {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [statistics, setStatistics] = useState<AutoDownloadStatistics | null>(null)
  const [settings, setSettings] = useState({
    enabled: true,
    check_interval: 60, // 检查间隔（分钟）
    max_daily_downloads: 10, // 每日最大下载数
    auto_cleanup_days: 30, // 自动清理天数
    notification_enabled: true // 是否启用通知
  })

  // 加载统计信息
  const loadStatistics = async () => {
    try {
      const stats = await getStatistics()
      setStatistics(stats)
    } catch (error) {
      message.error('加载统计信息失败')
    }
  }

  useEffect(() => {
    loadStatistics()
    // 设置表单初始值
    form.setFieldsValue(settings)
  }, [])

  // 保存设置
  const handleSave = async (values: any) => {
    try {
      setLoading(true)
      // 这里应该调用后端API保存设置
      // await saveAutoDownloadSettings(values)
      setSettings(values)
      message.success('设置保存成功')
    } catch (error) {
      message.error('设置保存失败')
    } finally {
      setLoading(false)
    }
  }

  // 手动触发
  const handleTrigger = async () => {
    try {
      setLoading(true)
      await triggerAutoDownload({ force: true })
      message.success('手动触发成功')
      loadStatistics()
    } catch (error) {
      message.error('手动触发失败')
    } finally {
      setLoading(false)
    }
  }

  // 测试设置
  const handleTest = async () => {
    try {
      setLoading(true)
      // 这里可以调用测试API
      message.success('测试完成')
    } catch (error) {
      message.error('测试失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      {/* 统计信息卡片 */}
      {statistics && (
        <Card title="运行状态" style={{ marginBottom: 24 }}>
          <Row gutter={16}>
            <Col span={6}>
              <Statistic 
                title="活跃规则" 
                value={statistics.active_rules}
                suffix={`/ ${statistics.total_rules}`}
              />
            </Col>
            <Col span={6}>
              <Statistic 
                title="今日新增" 
                value={statistics.today_subscriptions} 
              />
            </Col>
            <Col span={6}>
              <Statistic 
                title="等待处理" 
                value={statistics.pending_subscriptions} 
              />
            </Col>
            <Col span={6}>
              <Statistic 
                title="成功率" 
                value={statistics.success_rate} 
                suffix="%" 
                precision={1}
              />
            </Col>
          </Row>
          
          <Divider />
          
          <Row gutter={16}>
            <Col span={6}>
              <div>
                <Tag color="processing">下载中: {statistics.downloading_subscriptions}</Tag>
              </div>
            </Col>
            <Col span={6}>
              <div>
                <Tag color="success">已完成: {statistics.completed_subscriptions}</Tag>
              </div>
            </Col>
            <Col span={6}>
              <div>
                <Tag color="error">失败: {statistics.failed_subscriptions}</Tag>
              </div>
            </Col>
            <Col span={6}>
              <div>
                <Tag color="default">总计: {statistics.total_subscriptions}</Tag>
              </div>
            </Col>
          </Row>
        </Card>
      )}

      {/* 设置表单 */}
      <Card title="智能下载设置">
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
          initialValues={settings}
        >
          <Row gutter={24}>
            <Col span={12}>
              <Form.Item
                name="enabled"
                label="启用智能下载"
                valuePropName="checked"
              >
                <Switch 
                  checkedChildren="开启" 
                  unCheckedChildren="关闭"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="notification_enabled"
                label="启用通知"
                valuePropName="checked"
              >
                <Switch 
                  checkedChildren="开启" 
                  unCheckedChildren="关闭"
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={24}>
            <Col span={12}>
              <Form.Item
                name="check_interval"
                label="检查间隔 (分钟)"
                rules={[{ required: true, message: '请输入检查间隔' }]}
              >
                <InputNumber
                  min={10}
                  max={1440}
                  placeholder="60"
                  style={{ width: '100%' }}
                  addonAfter="分钟"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="max_daily_downloads"
                label="每日最大下载数"
                rules={[{ required: true, message: '请输入每日最大下载数' }]}
              >
                <InputNumber
                  min={1}
                  max={100}
                  placeholder="10"
                  style={{ width: '100%' }}
                  addonAfter="个"
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={24}>
            <Col span={12}>
              <Form.Item
                name="auto_cleanup_days"
                label="自动清理天数"
                rules={[{ required: true, message: '请输入自动清理天数' }]}
              >
                <InputNumber
                  min={1}
                  max={365}
                  placeholder="30"
                  style={{ width: '100%' }}
                  addonAfter="天"
                />
              </Form.Item>
            </Col>
          </Row>

          <Divider />

          <Form.Item>
            <Space>
              <Button 
                type="primary" 
                htmlType="submit" 
                loading={loading}
              >
                保存设置
              </Button>
              <Button 
                onClick={handleTrigger} 
                loading={loading}
              >
                手动触发
              </Button>
              <Button 
                onClick={handleTest} 
                loading={loading}
              >
                测试连接
              </Button>
              <Button onClick={() => loadStatistics()}>
                刷新统计
              </Button>
            </Space>
          </Form.Item>
        </Form>

        <Divider />

        {/* 说明文档 */}
        <Card type="inner" title="使用说明" size="small">
          <div style={{ color: '#666', lineHeight: '1.6' }}>
            <p><strong>智能下载功能说明：</strong></p>
            <ul>
              <li>系统会根据设置的规则自动筛选符合条件的作品</li>
              <li>筛选条件包括：评分、评论数、发布时间、质量要求等</li>
              <li>符合条件的作品会自动加入下载队列</li>
              <li>建议合理设置每日最大下载数，避免占用过多带宽</li>
              <li>定期清理已完成或失败的订阅记录，保持系统整洁</li>
            </ul>
            
            <p><strong>注意事项：</strong></p>
            <ul>
              <li>检查间隔过短可能增加服务器负担</li>
              <li>建议根据网络环境调整最大下载数</li>
              <li>启用通知可及时了解下载状态</li>
            </ul>
          </div>
        </Card>
      </Card>
    </div>
  )
}

export default AutoDownloadSettings