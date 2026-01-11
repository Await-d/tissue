import React, { useState, useEffect } from 'react'
import {
  Form,
  InputNumber,
  Switch,
  Button,
  Card,
  Space,
  App,
  Divider,
  Row,
  Col,
  Alert,
  Tag,
  Modal,
  Input,
  Statistic,
  Tooltip,
  Typography
} from 'antd'
import {
  InfoCircleOutlined,
  ExperimentOutlined,
  ReloadOutlined,
  SettingOutlined,
  FilterOutlined,
  DeleteOutlined,
  EyeOutlined
} from '@ant-design/icons'
import { createFileRoute } from '@tanstack/react-router'
import { useRequest } from 'ahooks'
import * as api from '@/apis/downloadFilter'
import { cleanupAllTorrents } from '@/apis/downloadFilter'
import { useThemeColors } from '../../../hooks/useThemeColors'
import type { CleanupResultData } from '@/types/cleanup'

export const Route = createFileRoute('/_index/setting/download-filter')({
  component: DownloadFilterSettings
})

const { Text, Title } = Typography

function DownloadFilterSettings() {
  const { message, modal } = App.useApp()
  const colors = useThemeColors()
  const [form] = Form.useForm()
  const [testModalVisible, setTestModalVisible] = useState(false)
  const [testMagnetUrl, setTestMagnetUrl] = useState('')
  const [testResult, setTestResult] = useState<api.MagnetFilterResult | null>(null)
  const [cleanupResultModalVisible, setCleanupResultModalVisible] = useState(false)
  const [cleanupResult, setCleanupResult] = useState<CleanupResultData | null>(null)

  const { loading } = useRequest(api.getFilterSettings, {
    onSuccess: (res) => {
      if (res.data) {
        form.setFieldsValue(res.data)
      }
    },
    onError: (err) => {
      console.error('获取过滤设置失败:', err)
    }
  })

  const { run: saveSettings, loading: saving } = useRequest(api.saveFilterSettings, {
    manual: true,
    onSuccess: (res) => {
      if (res.success) {
        message.success('设置保存成功')
      } else {
        message.error(res.message || '保存失败')
      }
    },
    onError: (err) => {
      message.error('保存设置失败：' + (err.message || '未知错误'))
    }
  })

  const { run: resetSettings, loading: resetting } = useRequest(api.resetToDefaultSettings, {
    manual: true,
    onSuccess: (res) => {
      if (res.success) {
        message.success('设置已重置为默认值')
        window.location.reload()
      } else {
        message.error(res.message || '重置失败')
      }
    }
  })

  const { run: testMagnet, loading: testingMagnet } = useRequest(api.testMagnetFilter, {
    manual: true,
    onSuccess: (res) => {
      if (res.data) {
        setTestResult(res.data)
      }
    },
    onError: (err) => {
      message.error('测试失败：' + (err.message || '未知错误'))
    }
  })

  const handleSubmit = (values: any) => {
    const settings = {
      min_file_size_mb: values.min_file_size_mb || 300,
      max_file_size_mb: values.max_file_size_mb || null,
      enable_smart_filter: values.enable_smart_filter !== false,
      skip_sample_files: values.skip_sample_files !== false,
      skip_subtitle_only: values.skip_subtitle_only !== false,
      media_files_only: values.media_files_only === true,
      include_subtitles: values.include_subtitles !== false,
    }
    saveSettings(settings)
  }

  const handleTestMagnet = () => {
    if (!testMagnetUrl.trim()) {
      message.error('请输入磁力链接')
      return
    }
    testMagnet(testMagnetUrl)
  }

  const handlePreviewCleanup = async () => {
    try {
      const res = await cleanupAllTorrents(undefined, true)
      if (res.success) {
        setCleanupResult(res.data)
        setCleanupResultModalVisible(true)
      } else {
        message.error(res.message || '预览清理失败')
      }
    } catch (err: any) {
      message.error('预览清理失败：' + (err.message || '未知错误'))
    }
  }

  const handleExecuteCleanup = () => {
    modal.confirm({
      title: '确认执行清理',
      content: '此操作将删除不符合过滤规则的文件，无法恢复。是否继续？',
      okText: '确认清理',
      cancelText: '取消',
      okButtonProps: {
        danger: true
      },
      onOk: async () => {
        try {
          const res = await cleanupAllTorrents(undefined, false)
          if (res.success) {
            setCleanupResult(res.data)
            setCleanupResultModalVisible(true)
            message.success('清理完成')
          } else {
            message.error(res.message || '清理失败')
          }
        } catch (err: any) {
          message.error('清理失败：' + (err.message || '未知错误'))
        }
      }
    })
  }

  const renderTestResult = () => {
    if (!testResult) return null

    return (
      <div className="mt-4">
        <Row gutter={16} className="mb-4">
          <Col span={6}>
            <div className="p-4 rounded-lg border" style={{ backgroundColor: colors.bgContainer, borderColor: colors.borderPrimary }}>
              <div className="text-xs mb-1" style={{ color: colors.textTertiary }}>原始文件数</div>
              <div className="text-2xl font-bold" style={{ color: colors.textPrimary }}>{testResult.total_files}</div>
            </div>
          </Col>
          <Col span={6}>
            <div className="p-4 rounded-lg border" style={{ backgroundColor: colors.bgContainer, borderColor: colors.borderPrimary }}>
              <div className="text-xs mb-1" style={{ color: colors.textTertiary }}>过滤后文件数</div>
              <div className="text-2xl font-bold" style={{ color: colors.goldPrimary }}>{testResult.filtered_files}</div>
            </div>
          </Col>
          <Col span={6}>
            <div className="p-4 rounded-lg border" style={{ backgroundColor: colors.bgContainer, borderColor: colors.borderPrimary }}>
              <div className="text-xs mb-1" style={{ color: colors.textTertiary }}>过滤后大小</div>
              <div className="text-2xl font-bold" style={{ color: colors.textPrimary }}>{testResult.filtered_size_mb}<span className="text-sm ml-1" style={{ color: colors.textTertiary }}>MB</span></div>
            </div>
          </Col>
          <Col span={6}>
            <div className="p-4 rounded-lg border" style={{ backgroundColor: colors.bgContainer, borderColor: colors.borderPrimary }}>
              <div className="text-xs mb-1" style={{ color: colors.textTertiary }}>建议下载</div>
              <Tag color={testResult.should_download ? 'success' : 'error'} className="mt-2">
                {testResult.should_download ? '是' : '否'}
              </Tag>
            </div>
          </Col>
        </Row>

        <Alert
          message={testResult.filter_reason}
          type={testResult.should_download ? 'success' : 'warning'}
          className="mb-4"
          style={{ backgroundColor: colors.bgElevated, borderColor: colors.borderPrimary }}
        />

        {testResult.files.length > 0 && (
          <div className="rounded-lg border p-4" style={{ backgroundColor: colors.bgContainer, borderColor: colors.borderPrimary }}>
            <div className="font-semibold mb-3" style={{ color: colors.goldLight }}>过滤后的文件</div>
            {testResult.files.map((file, index) => (
              <div key={index} className="mb-2 p-2 rounded border" style={{ backgroundColor: colors.bgElevated, borderColor: colors.borderPrimary }}>
                <Text style={{ color: colors.textPrimary }}>{file.name}</Text>
                <Tag color="blue" className="ml-2">{file.size_mb} MB</Tag>
                {file.is_video && <Tag color="green">视频</Tag>}
                {file.is_sample && <Tag color="orange">样本</Tag>}
              </div>
            ))}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="rounded-2xl border shadow-2xl overflow-hidden" style={{ backgroundColor: colors.bgContainer, borderColor: colors.borderPrimary }}>
        {/* 页面标题 */}
        <div className="px-8 py-6 border-b" style={{ borderColor: colors.borderPrimary, background: `linear-gradient(to right, ${colors.bgElevated}, ${colors.bgContainer})` }}>
          <h2 className="text-2xl font-bold flex items-center gap-3" style={{ color: colors.goldPrimary }}>
            <span className="w-1.5 h-8 rounded-full" style={{ background: `linear-gradient(to bottom, ${colors.goldPrimary}, ${colors.goldDark})` }}></span>
            下载过滤设置
          </h2>
          <p className="text-sm mt-2 ml-6" style={{ color: colors.textSecondary }}>智能过滤种子文件，只下载符合条件的内容</p>
        </div>

        <div className="p-8">
          <Alert
            message="下载过滤功能说明"
            description="此功能会分析种子中的文件，根据设置的规则过滤掉不需要的文件，只下载符合条件的内容。"
            type="info"
            showIcon
            className="mb-6"
            style={{ backgroundColor: colors.bgElevated, borderColor: colors.borderGold }}
          />

          <Form
            form={form}
            layout="vertical"
            onFinish={handleSubmit}
            initialValues={{
              min_file_size_mb: 300,
              enable_smart_filter: true,
              skip_sample_files: true,
              skip_subtitle_only: true,
              media_files_only: false,
              include_subtitles: true
            }}
          >
            {/* 文件大小过滤 */}
            <div className="mb-8">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ color: colors.goldLight }}>
                <span className="w-1 h-5 rounded-full" style={{ backgroundColor: colors.goldPrimary }}></span>
                文件大小过滤
              </h3>
              <Row gutter={24}>
                <Col span={12}>
                  <Form.Item
                    name="min_file_size_mb"
                    label={
                      <span className="flex items-center gap-2" style={{ color: colors.textPrimary }}>
                        最小文件大小 (MB)
                        <Tooltip title="小于此大小的文件将被过滤掉">
                          <InfoCircleOutlined style={{ color: colors.textTertiary }} />
                        </Tooltip>
                      </span>
                    }
                    rules={[{ required: true, message: '请输入最小文件大小' }]}
                  >
                    <InputNumber
                      min={1}
                      max={10000}
                      placeholder="300"
                      className="w-full"
                      style={{ backgroundColor: colors.bgElevated, color: colors.textPrimary }}
                    />
                  </Form.Item>
                </Col>

                <Col span={12}>
                  <Form.Item
                    name="max_file_size_mb"
                    label={
                      <span className="flex items-center gap-2" style={{ color: colors.textPrimary }}>
                        最大文件大小 (MB)
                        <Tooltip title="大于此大小的文件将被过滤掉，留空表示无限制">
                          <InfoCircleOutlined style={{ color: colors.textTertiary }} />
                        </Tooltip>
                      </span>
                    }
                  >
                    <InputNumber
                      min={1}
                      max={50000}
                      placeholder="无限制"
                      className="w-full"
                      style={{ backgroundColor: colors.bgElevated, color: colors.textPrimary }}
                    />
                  </Form.Item>
                </Col>
              </Row>
            </div>

            {/* 智能过滤选项 */}
            <div className="mb-8 pt-8" style={{ borderTop: `1px solid ${colors.borderPrimary}` }}>
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ color: colors.goldLight }}>
                <span className="w-1 h-5 rounded-full" style={{ backgroundColor: colors.goldPrimary }}></span>
                智能过滤选项
              </h3>
              <Row gutter={24}>
                <Col span={8}>
                  <Form.Item
                    name="enable_smart_filter"
                    label={<span style={{ color: colors.textPrimary }}>启用智能过滤</span>}
                    valuePropName="checked"
                    className="mb-0"
                  >
                    <Switch className="custom-switch-gold" />
                  </Form.Item>
                </Col>

                <Col span={8}>
                  <Form.Item
                    name="skip_sample_files"
                    label={<span style={{ color: colors.textPrimary }}>跳过样本文件</span>}
                    valuePropName="checked"
                    className="mb-0"
                  >
                    <Switch className="custom-switch-gold" />
                  </Form.Item>
                </Col>

                <Col span={8}>
                  <Form.Item
                    name="media_files_only"
                    label={
                      <span className="flex items-center gap-2" style={{ color: colors.textPrimary }}>
                        只保留媒体文件
                        <Tooltip title="启用后只保留视频文件和字幕文件，过滤其他所有文件类型">
                          <InfoCircleOutlined style={{ color: colors.textTertiary }} />
                        </Tooltip>
                      </span>
                    }
                    valuePropName="checked"
                    className="mb-0"
                  >
                    <Switch className="custom-switch-gold" />
                  </Form.Item>
                </Col>
              </Row>
            </div>

            {/* 字幕控制 */}
            <div className="mb-8 pt-8" style={{ borderTop: `1px solid ${colors.borderPrimary}` }}>
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ color: colors.goldLight }}>
                <span className="w-1 h-5 rounded-full" style={{ backgroundColor: colors.goldPrimary }}></span>
                字幕控制
              </h3>
              <Row gutter={24}>
                <Col span={12}>
                  <Form.Item
                    name="include_subtitles"
                    label={
                      <span className="flex items-center gap-2" style={{ color: colors.textPrimary }}>
                        包含字幕文件
                        <Tooltip title="在媒体文件模式下是否包含字幕文件">
                          <InfoCircleOutlined style={{ color: colors.textTertiary }} />
                        </Tooltip>
                      </span>
                    }
                    valuePropName="checked"
                    className="mb-0"
                  >
                    <Switch className="custom-switch-gold" />
                  </Form.Item>
                </Col>

                <Col span={12}>
                  <Form.Item
                    name="skip_subtitle_only"
                    label={
                      <span className="flex items-center gap-2" style={{ color: colors.textPrimary }}>
                        跳过纯字幕文件
                        <Tooltip title="在非媒体文件模式下是否跳过字幕文件">
                          <InfoCircleOutlined style={{ color: colors.textTertiary }} />
                        </Tooltip>
                      </span>
                    }
                    valuePropName="checked"
                    className="mb-0"
                  >
                    <Switch className="custom-switch-gold" />
                  </Form.Item>
                </Col>
              </Row>
            </div>

            <div className="flex justify-center gap-4 pt-6" style={{ borderTop: `1px solid ${colors.borderPrimary}` }}>
              <Button
                type="primary"
                htmlType="submit"
                loading={saving}
                size="large"
                icon={<SettingOutlined />}
                style={{ background: colors.goldGradient, borderColor: colors.goldPrimary, color: colors.bgBase }}
                className="font-semibold hover:shadow-lg"
              >
                保存设置
              </Button>

              <Button
                onClick={() => setTestModalVisible(true)}
                size="large"
                icon={<ExperimentOutlined />}
                style={{ backgroundColor: colors.bgSpotlight, borderColor: colors.borderPrimary, color: colors.goldPrimary }}
              >
                测试过滤
              </Button>

              <Button
                onClick={resetSettings}
                loading={resetting}
                size="large"
                icon={<ReloadOutlined />}
                style={{ backgroundColor: colors.bgSpotlight, borderColor: colors.borderPrimary, color: colors.textSecondary }}
              >
                重置为默认
              </Button>
            </div>
          </Form>

          {/* 使用说明 */}
          <div className="mt-8 pt-8" style={{ borderTop: `1px solid ${colors.borderPrimary}` }}>
            <div className="rounded-lg p-6 border" style={{ backgroundColor: colors.bgElevated, borderColor: colors.borderPrimary }}>
              <h4 className="text-base font-semibold mb-4" style={{ color: colors.goldLight }}>功能特点</h4>
              <ul className="space-y-2 mb-6" style={{ color: colors.textSecondary }}>
                <li className="flex items-start gap-2">
                  <span className="mt-1" style={{ color: colors.goldPrimary }}>•</span>
                  <span><span className="font-medium" style={{ color: colors.textPrimary }}>文件大小过滤</span>：设置最小和最大文件大小限制</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-1" style={{ color: colors.goldPrimary }}>•</span>
                  <span><span className="font-medium" style={{ color: colors.textPrimary }}>智能过滤</span>：自动识别和过滤样本文件、宣传文件等</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-1" style={{ color: colors.goldPrimary }}>•</span>
                  <span><span className="font-medium" style={{ color: colors.textPrimary }}>媒体文件模式</span>：只保留视频文件和字幕文件，过滤其他类型</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-1" style={{ color: colors.goldPrimary }}>•</span>
                  <span><span className="font-medium" style={{ color: colors.textPrimary }}>字幕控制</span>：可单独控制是否包含字幕文件</span>
                </li>
              </ul>

              <h4 className="text-base font-semibold mb-4" style={{ color: colors.goldLight }}>注意事项</h4>
              <ul className="space-y-2" style={{ color: colors.textSecondary }}>
                <li className="flex items-start gap-2">
                  <span className="mt-1" style={{ color: colors.goldPrimary }}>•</span>
                  <span>过滤规则会应用到所有新添加的种子</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-1" style={{ color: colors.goldPrimary }}>•</span>
                  <span>建议合理设置文件大小，避免过滤掉重要内容</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-1" style={{ color: colors.goldPrimary }}>•</span>
                  <span>样本文件通常很小，建议保持"跳过样本文件"开启</span>
                </li>
              </ul>
            </div>
          </div>

          {/* 历史种子清理 */}
          <div className="mt-8 pt-8" style={{ borderTop: `1px solid ${colors.borderPrimary}` }}>
            <div className="rounded-lg p-6 border" style={{ backgroundColor: colors.bgElevated, borderColor: colors.borderPrimary }}>
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ color: colors.goldLight }}>
                <span className="w-1 h-5 rounded-full" style={{ backgroundColor: colors.goldPrimary }}></span>
                历史种子清理
              </h3>

              <Alert
                message="对 qBittorrent 中已下载的种子应用过滤规则，删除不符合条件的文件（如广告、样本等）"
                type="info"
                showIcon
                className="mb-4"
                style={{ backgroundColor: colors.bgContainer, borderColor: colors.borderGold }}
              />

              <div className="flex justify-center gap-4">
                <Button
                  size="large"
                  icon={<EyeOutlined />}
                  onClick={handlePreviewCleanup}
                  style={{ backgroundColor: colors.bgSpotlight, borderColor: colors.borderPrimary, color: colors.goldPrimary }}
                >
                  预览清理
                </Button>

                <Button
                  size="large"
                  icon={<DeleteOutlined />}
                  onClick={handleExecuteCleanup}
                  danger
                  style={{ borderColor: colors.borderPrimary }}
                >
                  执行清理
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 测试磁力链接对话框 */}
      <Modal
        title={<span style={{ color: colors.goldPrimary }}>测试过滤规则</span>}
        open={testModalVisible}
        onCancel={() => {
          setTestModalVisible(false)
          setTestResult(null)
          setTestMagnetUrl('')
        }}
        footer={null}
        width={800}
        className="dark-modal"
      >
        <div className="p-6 rounded-lg" style={{ backgroundColor: colors.bgContainer }}>
          <div className="flex gap-2 mb-4">
            <Input
              placeholder="输入磁力链接进行测试..."
              value={testMagnetUrl}
              onChange={(e) => setTestMagnetUrl(e.target.value)}
              onPressEnter={handleTestMagnet}
              className="flex-1"
              style={{ backgroundColor: colors.bgElevated, color: colors.textPrimary }}
            />
            <Button
              type="primary"
              onClick={handleTestMagnet}
              loading={testingMagnet}
              style={{ background: colors.goldGradient, borderColor: colors.goldPrimary, color: colors.bgBase }}
            >
              测试
            </Button>
          </div>

          {renderTestResult()}
        </div>
      </Modal>

      {/* 清理结果对话框 */}
      <Modal
        title={<span style={{ color: colors.goldPrimary }}>清理结果</span>}
        open={cleanupResultModalVisible}
        onCancel={() => {
          setCleanupResultModalVisible(false)
          setCleanupResult(null)
        }}
        footer={[
          <Button
            key="close"
            onClick={() => {
              setCleanupResultModalVisible(false)
              setCleanupResult(null)
            }}
            style={{ backgroundColor: colors.bgSpotlight, borderColor: colors.borderPrimary, color: colors.textPrimary }}
          >
            关闭
          </Button>
        ]}
        width={800}
        className="dark-modal"
      >
        <div className="p-6 rounded-lg" style={{ backgroundColor: colors.bgContainer }}>
          {cleanupResult && (
            <>
              <Row gutter={16} className="mb-4">
                <Col span={6}>
                  <div className="p-4 rounded-lg border" style={{ backgroundColor: colors.bgContainer, borderColor: colors.borderPrimary }}>
                    <div className="text-xs mb-1" style={{ color: colors.textTertiary }}>总种子数</div>
                    <div className="text-2xl font-bold" style={{ color: colors.textPrimary }}>
                      {cleanupResult.total_torrents || 0}
                    </div>
                  </div>
                </Col>
                <Col span={6}>
                  <div className="p-4 rounded-lg border" style={{ backgroundColor: colors.bgContainer, borderColor: colors.borderPrimary }}>
                    <div className="text-xs mb-1" style={{ color: colors.textTertiary }}>处理成功</div>
                    <div className="text-2xl font-bold" style={{ color: colors.textPrimary }}>
                      {cleanupResult.processed_torrents || 0}
                    </div>
                  </div>
                </Col>
                <Col span={6}>
                  <div className="p-4 rounded-lg border" style={{ backgroundColor: colors.bgContainer, borderColor: colors.borderPrimary }}>
                    <div className="text-xs mb-1" style={{ color: colors.textTertiary }}>删除文件数</div>
                    <div className="text-2xl font-bold" style={{ color: colors.goldPrimary }}>
                      {cleanupResult.total_deleted_files || 0}
                    </div>
                  </div>
                </Col>
                <Col span={6}>
                  <div className="p-4 rounded-lg border" style={{ backgroundColor: colors.bgContainer, borderColor: colors.borderPrimary }}>
                    <div className="text-xs mb-1" style={{ color: colors.textTertiary }}>释放空间</div>
                    <div className="text-2xl font-bold" style={{ color: colors.textPrimary }}>
                      {cleanupResult.total_deleted_size_gb ? `${cleanupResult.total_deleted_size_gb} GB` : '0 GB'}
                    </div>
                  </div>
                </Col>
              </Row>

              {cleanupResult.torrent_results && cleanupResult.torrent_results.length > 0 && (
                <div className="rounded-lg border p-4" style={{ backgroundColor: colors.bgContainer, borderColor: colors.borderPrimary }}>
                  <div className="font-semibold mb-3" style={{ color: colors.goldLight }}>清理详情</div>
                  <div className="max-h-96 overflow-y-auto">
                    {cleanupResult.torrent_results
                      .filter(item => item.deleted_files > 0)
                      .map((item, index) => (
                      <div key={index} className="mb-3 p-3 rounded border" style={{ backgroundColor: colors.bgElevated, borderColor: colors.borderPrimary }}>
                        <div className="flex justify-between items-center">
                          <div className="font-medium" style={{ color: colors.textPrimary }}>
                            {item.name}
                          </div>
                          <div className="text-sm" style={{ color: colors.textSecondary }}>
                            删除 {item.deleted_files} 个文件，释放 {item.deleted_size_mb} MB
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </Modal>
    </div>
  )
}

export default DownloadFilterSettings
