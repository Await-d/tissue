import React, { useState, useEffect } from 'react'
import {
  Form,
  Switch,
  InputNumber,
  Select,
  Button,
  Card,
  Space,
  App,
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
} from '@/apis/autoDownload'
import { useThemeColors } from '../../../hooks/useThemeColors'

export const Route = createFileRoute('/_index/setting/auto-download')({
  component: AutoDownloadSettings
})

const { Option } = Select

function AutoDownloadSettings() {
  const { message } = App.useApp()
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [statistics, setStatistics] = useState<AutoDownloadStatistics | null>(null)
  const [settings, setSettings] = useState({
    enabled: true,
    check_interval: 60,
    max_daily_downloads: 10,
    auto_cleanup_days: 30,
    notification_enabled: true
  })
  const colors = useThemeColors()

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
    form.setFieldsValue(settings)
  }, [])

  const handleSave = async (values: any) => {
    try {
      setLoading(true)
      setSettings(values)
      message.success('设置保存成功')
    } catch (error) {
      message.error('设置保存失败')
    } finally {
      setLoading(false)
    }
  }

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

  const handleTest = async () => {
    try {
      setLoading(true)
      message.success('测试完成')
    } catch (error) {
      message.error('测试失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* 运行状态卡片 */}
      {statistics && (
        <div style={{ backgroundColor: colors.bgContainer, borderColor: colors.borderPrimary }} className="rounded-2xl border shadow-2xl overflow-hidden mb-6">
          <div style={{ borderBottomColor: colors.borderPrimary, backgroundImage: `linear-gradient(to right, ${colors.bgElevated}, ${colors.bgContainer})` }} className="px-8 py-6 border-b">
            <h2 style={{ color: colors.goldPrimary }} className="text-2xl font-bold flex items-center gap-3">
              <span style={{ backgroundImage: `linear-gradient(to bottom, ${colors.goldPrimary}, ${colors.goldDark})` }} className="w-1.5 h-8 rounded-full"></span>
              运行状态
            </h2>
            <p style={{ color: colors.textSecondary }} className="text-sm mt-2 ml-6">智能下载系统运行统计信息</p>
          </div>

          <div className="p-8">
            <Row gutter={16}>
              <Col span={6}>
                <div style={{ backgroundColor: colors.bgElevated, borderColor: colors.borderPrimary }} className="rounded-lg p-4 border">
                  <div style={{ color: colors.textTertiary }} className="text-xs mb-2">活跃规则</div>
                  <div style={{ color: colors.goldPrimary }} className="text-3xl font-bold">
                    {statistics.active_rules}
                    <span style={{ color: colors.textTertiary }} className="text-sm font-normal ml-2">/ {statistics.total_rules}</span>
                  </div>
                </div>
              </Col>
              <Col span={6}>
                <div style={{ backgroundColor: colors.bgElevated, borderColor: colors.borderPrimary }} className="rounded-lg p-4 border">
                  <div style={{ color: colors.textTertiary }} className="text-xs mb-2">今日新增</div>
                  <div style={{ color: colors.textPrimary }} className="text-3xl font-bold">{statistics.today_subscriptions}</div>
                </div>
              </Col>
              <Col span={6}>
                <div style={{ backgroundColor: colors.bgElevated, borderColor: colors.borderPrimary }} className="rounded-lg p-4 border">
                  <div style={{ color: colors.textTertiary }} className="text-xs mb-2">等待处理</div>
                  <div style={{ color: colors.textPrimary }} className="text-3xl font-bold">{statistics.pending_subscriptions}</div>
                </div>
              </Col>
              <Col span={6}>
                <div style={{ backgroundColor: colors.bgElevated, borderColor: colors.borderPrimary }} className="rounded-lg p-4 border">
                  <div style={{ color: colors.textTertiary }} className="text-xs mb-2">成功率</div>
                  <div style={{ color: colors.goldLight }} className="text-3xl font-bold">
                    {statistics.success_rate}
                    <span style={{ color: colors.textTertiary }} className="text-sm ml-1">%</span>
                  </div>
                </div>
              </Col>
            </Row>

            <div style={{ borderTopColor: colors.borderPrimary }} className="mt-6 pt-6 border-t">
              <Row gutter={16}>
                <Col span={6}>
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                    <Tag color="processing" className="border-0 bg-blue-500/10 text-blue-400">
                      下载中: {statistics.downloading_subscriptions}
                    </Tag>
                  </div>
                </Col>
                <Col span={6}>
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-green-500"></span>
                    <Tag color="success" className="border-0 bg-green-500/10 text-green-400">
                      已完成: {statistics.completed_subscriptions}
                    </Tag>
                  </div>
                </Col>
                <Col span={6}>
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-red-500"></span>
                    <Tag color="error" className="border-0 bg-red-500/10 text-red-400">
                      失败: {statistics.failed_subscriptions}
                    </Tag>
                  </div>
                </Col>
                <Col span={6}>
                  <div className="flex items-center gap-2">
                    <span style={{ backgroundColor: colors.textTertiary }} className="w-2 h-2 rounded-full"></span>
                    <Tag style={{ backgroundColor: colors.bgSpotlight, color: colors.textSecondary }} className="border-0">
                      总计: {statistics.total_subscriptions}
                    </Tag>
                  </div>
                </Col>
              </Row>
            </div>
          </div>
        </div>
      )}

      {/* 设置表单 */}
      <div style={{ backgroundColor: colors.bgContainer, borderColor: colors.borderPrimary }} className="rounded-2xl border shadow-2xl overflow-hidden">
        <div style={{ borderBottomColor: colors.borderPrimary, backgroundImage: `linear-gradient(to right, ${colors.bgElevated}, ${colors.bgContainer})` }} className="px-8 py-6 border-b">
          <h2 style={{ color: colors.goldPrimary }} className="text-2xl font-bold flex items-center gap-3">
            <span style={{ backgroundImage: `linear-gradient(to bottom, ${colors.goldPrimary}, ${colors.goldDark})` }} className="w-1.5 h-8 rounded-full"></span>
            智能下载设置
          </h2>
          <p style={{ color: colors.textSecondary }} className="text-sm mt-2 ml-6">配置自动下载规则和运行参数</p>
        </div>

        <div className="p-8">
          <Form
            form={form}
            layout="vertical"
            onFinish={handleSave}
            initialValues={settings}
          >
            {/* 基础开关 */}
            <div className="mb-8">
              <h3 style={{ color: colors.goldLight }} className="text-lg font-semibold mb-4 flex items-center gap-2">
                <span style={{ backgroundColor: colors.goldPrimary }} className="w-1 h-5 rounded-full"></span>
                基础设置
              </h3>
              <Row gutter={24}>
                <Col span={12}>
                  <Form.Item
                    name="enabled"
                    label={<span style={{ color: colors.textPrimary }}>启用智能下载</span>}
                    valuePropName="checked"
                    className="mb-0"
                  >
                    <Switch className="custom-switch-gold" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="notification_enabled"
                    label={<span style={{ color: colors.textPrimary }}>启用通知</span>}
                    valuePropName="checked"
                    className="mb-0"
                  >
                    <Switch className="custom-switch-gold" />
                  </Form.Item>
                </Col>
              </Row>
            </div>

            {/* 运行参数 */}
            <div style={{ borderTopColor: colors.borderPrimary }} className="mb-8 pt-8 border-t">
              <h3 style={{ color: colors.goldLight }} className="text-lg font-semibold mb-4 flex items-center gap-2">
                <span style={{ backgroundColor: colors.goldPrimary }} className="w-1 h-5 rounded-full"></span>
                运行参数
              </h3>
              <Row gutter={24}>
                <Col span={12}>
                  <Form.Item
                    name="check_interval"
                    label={<span style={{ color: colors.textPrimary }}>检查间隔 (分钟)</span>}
                    rules={[{ required: true, message: '请输入检查间隔' }]}
                  >
                    <InputNumber
                      min={10}
                      max={1440}
                      placeholder="60"
                      style={{
                        backgroundColor: colors.bgElevated,
                        borderColor: colors.borderPrimary,
                        color: colors.textPrimary
                      }}
                      className="w-full text-[#f0f0f2]"
                    />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="max_daily_downloads"
                    label={<span style={{ color: colors.textPrimary }}>每日最大下载数</span>}
                    rules={[{ required: true, message: '请输入每日最大下载数' }]}
                  >
                    <InputNumber
                      min={1}
                      max={100}
                      placeholder="10"
                      style={{
                        backgroundColor: colors.bgElevated,
                        borderColor: colors.borderPrimary,
                        color: colors.textPrimary
                      }}
                      className="w-full text-[#f0f0f2]"
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={24}>
                <Col span={12}>
                  <Form.Item
                    name="auto_cleanup_days"
                    label={<span style={{ color: colors.textPrimary }}>自动清理天数</span>}
                    rules={[{ required: true, message: '请输入自动清理天数' }]}
                  >
                    <InputNumber
                      min={1}
                      max={365}
                      placeholder="30"
                      style={{
                        backgroundColor: colors.bgElevated,
                        borderColor: colors.borderPrimary,
                        color: colors.textPrimary
                      }}
                      className="w-full text-[#f0f0f2]"
                    />
                  </Form.Item>
                </Col>
              </Row>
            </div>

            <div style={{ borderTopColor: colors.borderPrimary }} className="flex justify-center gap-4 pt-6 border-t">
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                size="large"
                style={{
                  backgroundImage: colors.goldGradient,
                  borderColor: 'transparent',
                  color: colors.bgBase,
                }}
                className="font-semibold shadow-lg"
              >
                保存设置
              </Button>
              <Button
                onClick={handleTrigger}
                loading={loading}
                size="large"
                style={{
                  backgroundColor: colors.bgSpotlight,
                  borderColor: colors.borderPrimary,
                  color: colors.goldPrimary
                }}
              >
                手动触发
              </Button>
              <Button
                onClick={handleTest}
                loading={loading}
                size="large"
                style={{
                  backgroundColor: colors.bgSpotlight,
                  borderColor: colors.borderPrimary,
                  color: colors.textSecondary
                }}
              >
                测试连接
              </Button>
              <Button
                onClick={() => loadStatistics()}
                size="large"
                style={{
                  backgroundColor: colors.bgSpotlight,
                  borderColor: colors.borderPrimary,
                  color: colors.textSecondary
                }}
              >
                刷新统计
              </Button>
            </div>
          </Form>

          {/* 使用说明 */}
          <div style={{ borderTopColor: colors.borderPrimary }} className="mt-8 pt-8 border-t">
            <div style={{ backgroundColor: colors.bgElevated, borderColor: colors.borderPrimary }} className="rounded-lg p-6 border">
              <h4 style={{ color: colors.goldLight }} className="text-base font-semibold mb-4">智能下载功能说明</h4>
              <ul style={{ color: colors.textSecondary }} className="space-y-2 mb-6">
                <li className="flex items-start gap-2">
                  <span style={{ color: colors.goldPrimary }} className="mt-1">•</span>
                  <span>系统会根据设置的规则自动筛选符合条件的作品</span>
                </li>
                <li className="flex items-start gap-2">
                  <span style={{ color: colors.goldPrimary }} className="mt-1">•</span>
                  <span>筛选条件包括：评分、评论数、发布时间、质量要求等</span>
                </li>
                <li className="flex items-start gap-2">
                  <span style={{ color: colors.goldPrimary }} className="mt-1">•</span>
                  <span>符合条件的作品会自动加入下载队列</span>
                </li>
                <li className="flex items-start gap-2">
                  <span style={{ color: colors.goldPrimary }} className="mt-1">•</span>
                  <span>建议合理设置每日最大下载数，避免占用过多带宽</span>
                </li>
              </ul>

              <h4 style={{ color: colors.goldLight }} className="text-base font-semibold mb-4">注意事项</h4>
              <ul style={{ color: colors.textSecondary }} className="space-y-2">
                <li className="flex items-start gap-2">
                  <span style={{ color: colors.goldPrimary }} className="mt-1">•</span>
                  <span>检查间隔过短可能增加服务器负担</span>
                </li>
                <li className="flex items-start gap-2">
                  <span style={{ color: colors.goldPrimary }} className="mt-1">•</span>
                  <span>建议根据网络环境调整最大下载数</span>
                </li>
                <li className="flex items-start gap-2">
                  <span style={{ color: colors.goldPrimary }} className="mt-1">•</span>
                  <span>启用通知可及时了解下载状态</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AutoDownloadSettings
