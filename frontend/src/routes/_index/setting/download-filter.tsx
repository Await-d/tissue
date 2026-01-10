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
  FilterOutlined
} from '@ant-design/icons'
import { createFileRoute } from '@tanstack/react-router'
import { useRequest } from 'ahooks'
import * as api from '@/apis/downloadFilter'

export const Route = createFileRoute('/_index/setting/download-filter')({
  component: DownloadFilterSettings
})

const { Text, Title } = Typography

function DownloadFilterSettings() {
  const { message } = App.useApp()
  const [form] = Form.useForm()
  const [testModalVisible, setTestModalVisible] = useState(false)
  const [testMagnetUrl, setTestMagnetUrl] = useState('')
  const [testResult, setTestResult] = useState<api.MagnetFilterResult | null>(null)

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

  const renderTestResult = () => {
    if (!testResult) return null

    return (
      <div className="mt-4">
        <Row gutter={16} className="mb-4">
          <Col span={6}>
            <div className="bg-[#1a1a1d] p-4 rounded-lg border border-white/8">
              <div className="text-[#6a6a72] text-xs mb-1">原始文件数</div>
              <div className="text-[#f0f0f2] text-2xl font-bold">{testResult.total_files}</div>
            </div>
          </Col>
          <Col span={6}>
            <div className="bg-[#1a1a1d] p-4 rounded-lg border border-white/8">
              <div className="text-[#6a6a72] text-xs mb-1">过滤后文件数</div>
              <div className="text-[#d4a852] text-2xl font-bold">{testResult.filtered_files}</div>
            </div>
          </Col>
          <Col span={6}>
            <div className="bg-[#1a1a1d] p-4 rounded-lg border border-white/8">
              <div className="text-[#6a6a72] text-xs mb-1">过滤后大小</div>
              <div className="text-[#f0f0f2] text-2xl font-bold">{testResult.filtered_size_mb}<span className="text-sm text-[#6a6a72] ml-1">MB</span></div>
            </div>
          </Col>
          <Col span={6}>
            <div className="bg-[#1a1a1d] p-4 rounded-lg border border-white/8">
              <div className="text-[#6a6a72] text-xs mb-1">建议下载</div>
              <Tag color={testResult.should_download ? 'success' : 'error'} className="mt-2">
                {testResult.should_download ? '是' : '否'}
              </Tag>
            </div>
          </Col>
        </Row>

        <Alert
          message={testResult.filter_reason}
          type={testResult.should_download ? 'success' : 'warning'}
          className="mb-4 bg-[#1a1a1d] border-white/8"
        />

        {testResult.files.length > 0 && (
          <div className="bg-[#1a1a1d] rounded-lg border border-white/8 p-4">
            <div className="text-[#e8c780] font-semibold mb-3">过滤后的文件</div>
            {testResult.files.map((file, index) => (
              <div key={index} className="mb-2 p-2 bg-[#141416] rounded border border-white/8">
                <Text className="text-[#f0f0f2]">{file.name}</Text>
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
      <div className="bg-[#1a1a1d] rounded-2xl border border-white/8 shadow-2xl overflow-hidden">
        {/* 页面标题 */}
        <div className="px-8 py-6 border-b border-white/8 bg-gradient-to-r from-[#141416] to-[#1a1a1d]">
          <h2 className="text-2xl font-bold text-[#d4a852] flex items-center gap-3">
            <span className="w-1.5 h-8 bg-gradient-to-b from-[#d4a852] to-[#b08d3e] rounded-full"></span>
            下载过滤设置
          </h2>
          <p className="text-[#a0a0a8] text-sm mt-2 ml-6">智能过滤种子文件，只下载符合条件的内容</p>
        </div>

        <div className="p-8">
          <Alert
            message="下载过滤功能说明"
            description="此功能会分析种子中的文件，根据设置的规则过滤掉不需要的文件，只下载符合条件的内容。"
            type="info"
            showIcon
            className="mb-6 bg-[#141416] border-[#d4a852]/20"
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
              <h3 className="text-[#e8c780] text-lg font-semibold mb-4 flex items-center gap-2">
                <span className="w-1 h-5 bg-[#d4a852] rounded-full"></span>
                文件大小过滤
              </h3>
              <Row gutter={24}>
                <Col span={12}>
                  <Form.Item
                    name="min_file_size_mb"
                    label={
                      <span className="text-[#f0f0f2] flex items-center gap-2">
                        最小文件大小 (MB)
                        <Tooltip title="小于此大小的文件将被过滤掉">
                          <InfoCircleOutlined className="text-[#6a6a72]" />
                        </Tooltip>
                      </span>
                    }
                    rules={[{ required: true, message: '请输入最小文件大小' }]}
                  >
                    <InputNumber
                      min={1}
                      max={10000}
                      placeholder="300"
                      className="w-full bg-[#141416] border-white/8 text-[#f0f0f2] hover:border-[#d4a852]/50 focus:border-[#d4a852] focus:shadow-[0_0_0_2px_rgba(212,168,82,0.1)]"
                    />
                  </Form.Item>
                </Col>

                <Col span={12}>
                  <Form.Item
                    name="max_file_size_mb"
                    label={
                      <span className="text-[#f0f0f2] flex items-center gap-2">
                        最大文件大小 (MB)
                        <Tooltip title="大于此大小的文件将被过滤掉，留空表示无限制">
                          <InfoCircleOutlined className="text-[#6a6a72]" />
                        </Tooltip>
                      </span>
                    }
                  >
                    <InputNumber
                      min={1}
                      max={50000}
                      placeholder="无限制"
                      className="w-full bg-[#141416] border-white/8 text-[#f0f0f2] hover:border-[#d4a852]/50 focus:border-[#d4a852] focus:shadow-[0_0_0_2px_rgba(212,168,82,0.1)]"
                    />
                  </Form.Item>
                </Col>
              </Row>
            </div>

            {/* 智能过滤选项 */}
            <div className="mb-8 pt-8 border-t border-white/8">
              <h3 className="text-[#e8c780] text-lg font-semibold mb-4 flex items-center gap-2">
                <span className="w-1 h-5 bg-[#d4a852] rounded-full"></span>
                智能过滤选项
              </h3>
              <Row gutter={24}>
                <Col span={8}>
                  <Form.Item
                    name="enable_smart_filter"
                    label={<span className="text-[#f0f0f2]">启用智能过滤</span>}
                    valuePropName="checked"
                    className="mb-0"
                  >
                    <Switch className="custom-switch-gold" />
                  </Form.Item>
                </Col>

                <Col span={8}>
                  <Form.Item
                    name="skip_sample_files"
                    label={<span className="text-[#f0f0f2]">跳过样本文件</span>}
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
                      <span className="text-[#f0f0f2] flex items-center gap-2">
                        只保留媒体文件
                        <Tooltip title="启用后只保留视频文件和字幕文件，过滤其他所有文件类型">
                          <InfoCircleOutlined className="text-[#6a6a72]" />
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
            <div className="mb-8 pt-8 border-t border-white/8">
              <h3 className="text-[#e8c780] text-lg font-semibold mb-4 flex items-center gap-2">
                <span className="w-1 h-5 bg-[#d4a852] rounded-full"></span>
                字幕控制
              </h3>
              <Row gutter={24}>
                <Col span={12}>
                  <Form.Item
                    name="include_subtitles"
                    label={
                      <span className="text-[#f0f0f2] flex items-center gap-2">
                        包含字幕文件
                        <Tooltip title="在媒体文件模式下是否包含字幕文件">
                          <InfoCircleOutlined className="text-[#6a6a72]" />
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
                      <span className="text-[#f0f0f2] flex items-center gap-2">
                        跳过纯字幕文件
                        <Tooltip title="在非媒体文件模式下是否跳过字幕文件">
                          <InfoCircleOutlined className="text-[#6a6a72]" />
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

            <div className="flex justify-center gap-4 pt-6 border-t border-white/8">
              <Button
                type="primary"
                htmlType="submit"
                loading={saving}
                size="large"
                icon={<SettingOutlined />}
                className="bg-gradient-to-r from-[#d4a852] to-[#b08d3e] border-0 text-[#0d0d0f] font-semibold hover:from-[#e8c780] hover:to-[#d4a852] shadow-lg hover:shadow-[#d4a852]/20"
              >
                保存设置
              </Button>

              <Button
                onClick={() => setTestModalVisible(true)}
                size="large"
                icon={<ExperimentOutlined />}
                className="bg-[#222226] border-white/8 text-[#d4a852] hover:border-[#d4a852] hover:text-[#e8c780]"
              >
                测试过滤
              </Button>

              <Button
                onClick={resetSettings}
                loading={resetting}
                size="large"
                icon={<ReloadOutlined />}
                className="bg-[#222226] border-white/8 text-[#a0a0a8] hover:border-white/20 hover:text-[#f0f0f2]"
              >
                重置为默认
              </Button>
            </div>
          </Form>

          {/* 使用说明 */}
          <div className="mt-8 pt-8 border-t border-white/8">
            <div className="bg-[#141416] rounded-lg p-6 border border-white/8">
              <h4 className="text-[#e8c780] text-base font-semibold mb-4">功能特点</h4>
              <ul className="text-[#a0a0a8] space-y-2 mb-6">
                <li className="flex items-start gap-2">
                  <span className="text-[#d4a852] mt-1">•</span>
                  <span><span className="text-[#f0f0f2] font-medium">文件大小过滤</span>：设置最小和最大文件大小限制</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[#d4a852] mt-1">•</span>
                  <span><span className="text-[#f0f0f2] font-medium">智能过滤</span>：自动识别和过滤样本文件、宣传文件等</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[#d4a852] mt-1">•</span>
                  <span><span className="text-[#f0f0f2] font-medium">媒体文件模式</span>：只保留视频文件和字幕文件，过滤其他类型</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[#d4a852] mt-1">•</span>
                  <span><span className="text-[#f0f0f2] font-medium">字幕控制</span>：可单独控制是否包含字幕文件</span>
                </li>
              </ul>

              <h4 className="text-[#e8c780] text-base font-semibold mb-4">注意事项</h4>
              <ul className="text-[#a0a0a8] space-y-2">
                <li className="flex items-start gap-2">
                  <span className="text-[#d4a852] mt-1">•</span>
                  <span>过滤规则会应用到所有新添加的种子</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[#d4a852] mt-1">•</span>
                  <span>建议合理设置文件大小，避免过滤掉重要内容</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-[#d4a852] mt-1">•</span>
                  <span>样本文件通常很小，建议保持"跳过样本文件"开启</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* 测试磁力链接对话框 */}
      <Modal
        title={<span className="text-[#d4a852]">测试过滤规则</span>}
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
        <div className="bg-[#1a1a1d] p-6 rounded-lg">
          <div className="flex gap-2 mb-4">
            <Input
              placeholder="输入磁力链接进行测试..."
              value={testMagnetUrl}
              onChange={(e) => setTestMagnetUrl(e.target.value)}
              onPressEnter={handleTestMagnet}
              className="flex-1 bg-[#141416] border-white/8 text-[#f0f0f2] hover:border-[#d4a852]/50 focus:border-[#d4a852] focus:shadow-[0_0_0_2px_rgba(212,168,82,0.1)]"
            />
            <Button
              type="primary"
              onClick={handleTestMagnet}
              loading={testingMagnet}
              className="bg-gradient-to-r from-[#d4a852] to-[#b08d3e] border-0 text-[#0d0d0f] hover:from-[#e8c780] hover:to-[#d4a852]"
            >
              测试
            </Button>
          </div>

          {renderTestResult()}
        </div>
      </Modal>
    </div>
  )
}

export default DownloadFilterSettings
