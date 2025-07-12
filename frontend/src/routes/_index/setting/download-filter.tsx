import React, { useState, useEffect } from 'react'
import {
  Form,
  InputNumber,
  Switch,
  Button,
  Card,
  Space,
  message,
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
  const [form] = Form.useForm()
  const [testModalVisible, setTestModalVisible] = useState(false)
  const [testMagnetUrl, setTestMagnetUrl] = useState('')
  const [testResult, setTestResult] = useState<api.MagnetFilterResult | null>(null)

  // 获取当前设置
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

  // 保存设置
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

  // 重置为默认设置
  const { run: resetSettings, loading: resetting } = useRequest(api.resetToDefaultSettings, {
    manual: true,
    onSuccess: (res) => {
      if (res.success) {
        message.success('设置已重置为默认值')
        // 重新获取设置
        window.location.reload()
      } else {
        message.error(res.message || '重置失败')
      }
    }
  })

  // 测试磁力链接
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

  // 表单提交
  const handleSubmit = (values: any) => {
    // 处理数据格式
    const settings = {
      min_file_size_mb: values.min_file_size_mb || 300,
      max_file_size_mb: values.max_file_size_mb || null,
      enable_smart_filter: values.enable_smart_filter !== false,
      skip_sample_files: values.skip_sample_files !== false,
      skip_subtitle_only: values.skip_subtitle_only !== false,
    }

    saveSettings(settings)
  }

  // 测试磁力链接
  const handleTestMagnet = () => {
    if (!testMagnetUrl.trim()) {
      message.error('请输入磁力链接')
      return
    }
    testMagnet(testMagnetUrl)
  }

  // 渲染测试结果
  const renderTestResult = () => {
    if (!testResult) return null

    return (
      <div style={{ marginTop: 16 }}>
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={6}>
            <Statistic 
              title="原始文件数" 
              value={testResult.total_files} 
            />
          </Col>
          <Col span={6}>
            <Statistic 
              title="过滤后文件数" 
              value={testResult.filtered_files} 
              valueStyle={{ color: testResult.filtered_files > 0 ? '#3f8600' : '#cf1322' }}
            />
          </Col>
          <Col span={6}>
            <Statistic 
              title="过滤后大小" 
              value={testResult.filtered_size_mb} 
              suffix="MB" 
              precision={1}
            />
          </Col>
          <Col span={6}>
            <div>
              <Text strong>建议下载：</Text>
              <Tag color={testResult.should_download ? 'success' : 'error'}>
                {testResult.should_download ? '是' : '否'}
              </Tag>
            </div>
          </Col>
        </Row>

        <Alert 
          message={testResult.filter_reason} 
          type={testResult.should_download ? 'success' : 'warning'}
          style={{ marginBottom: 16 }}
        />

        {testResult.files.length > 0 && (
          <Card title="过滤后的文件" size="small">
            {testResult.files.map((file, index) => (
              <div key={index} style={{ marginBottom: 8 }}>
                <Text>{file.name}</Text>
                <Tag color="blue" style={{ marginLeft: 8 }}>
                  {file.size_mb} MB
                </Tag>
                {file.is_video && <Tag color="green">视频</Tag>}
                {file.is_sample && <Tag color="orange">样本</Tag>}
              </div>
            ))}
          </Card>
        )}
      </div>
    )
  }

  return (
    <div>
      <Card title={
        <Space>
          <FilterOutlined />
          下载过滤设置
        </Space>
      }>
        <Alert
          message="下载过滤功能说明"
          description="此功能会分析种子中的文件，根据设置的规则过滤掉不需要的文件，只下载符合条件的内容。"
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            min_file_size_mb: 300,
            enable_smart_filter: true,
            skip_sample_files: true,
            skip_subtitle_only: true
          }}
        >
          <Row gutter={24}>
            <Col span={12}>
              <Form.Item
                name="min_file_size_mb"
                label={
                  <Space>
                    最小文件大小 (MB)
                    <Tooltip title="小于此大小的文件将被过滤掉">
                      <InfoCircleOutlined />
                    </Tooltip>
                  </Space>
                }
                rules={[{ required: true, message: '请输入最小文件大小' }]}
              >
                <InputNumber
                  min={1}
                  max={10000}
                  placeholder="300"
                  style={{ width: '100%' }}
                  addonAfter="MB"
                />
              </Form.Item>
            </Col>

            <Col span={12}>
              <Form.Item
                name="max_file_size_mb"
                label={
                  <Space>
                    最大文件大小 (MB)
                    <Tooltip title="大于此大小的文件将被过滤掉，留空表示无限制">
                      <InfoCircleOutlined />
                    </Tooltip>
                  </Space>
                }
              >
                <InputNumber
                  min={1}
                  max={50000}
                  placeholder="无限制"
                  style={{ width: '100%' }}
                  addonAfter="MB"
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={24}>
            <Col span={8}>
              <Form.Item
                name="enable_smart_filter"
                label="启用智能过滤"
                valuePropName="checked"
              >
                <Switch 
                  checkedChildren="开启" 
                  unCheckedChildren="关闭"
                />
              </Form.Item>
            </Col>

            <Col span={8}>
              <Form.Item
                name="skip_sample_files"
                label="跳过样本文件"
                valuePropName="checked"
              >
                <Switch 
                  checkedChildren="跳过" 
                  unCheckedChildren="保留"
                />
              </Form.Item>
            </Col>

            <Col span={8}>
              <Form.Item
                name="skip_subtitle_only"
                label="跳过字幕文件"
                valuePropName="checked"
              >
                <Switch 
                  checkedChildren="跳过" 
                  unCheckedChildren="保留"
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
                loading={saving}
                icon={<SettingOutlined />}
              >
                保存设置
              </Button>

              <Button 
                onClick={() => setTestModalVisible(true)}
                icon={<ExperimentOutlined />}
              >
                测试过滤
              </Button>

              <Button 
                onClick={resetSettings} 
                loading={resetting}
                icon={<ReloadOutlined />}
              >
                重置为默认
              </Button>
            </Space>
          </Form.Item>
        </Form>

        <Divider />

        {/* 使用说明 */}
        <Card type="inner" title="使用说明" size="small">
          <div style={{ color: '#666', lineHeight: '1.6' }}>
            <Title level={5}>功能特点：</Title>
            <ul>
              <li><strong>文件大小过滤</strong>：设置最小和最大文件大小限制</li>
              <li><strong>智能过滤</strong>：自动识别和过滤样本文件、宣传文件等</li>
              <li><strong>类型过滤</strong>：可选择只保留视频文件，跳过字幕文件</li>
              <li><strong>实时生效</strong>：新设置会应用到后续的下载任务</li>
            </ul>
            
            <Title level={5}>注意事项：</Title>
            <ul>
              <li>过滤规则会应用到所有新添加的种子</li>
              <li>已存在的种子需要手动应用过滤规则</li>
              <li>建议合理设置文件大小，避免过滤掉重要内容</li>
              <li>样本文件通常很小，建议保持"跳过样本文件"开启</li>
            </ul>
          </div>
        </Card>
      </Card>

      {/* 测试磁力链接对话框 */}
      <Modal
        title="测试过滤规则"
        open={testModalVisible}
        onCancel={() => {
          setTestModalVisible(false)
          setTestResult(null)
          setTestMagnetUrl('')
        }}
        footer={null}
        width={800}
      >
        <Space.Compact style={{ width: '100%', marginBottom: 16 }}>
          <Input
            placeholder="输入磁力链接进行测试..."
            value={testMagnetUrl}
            onChange={(e) => setTestMagnetUrl(e.target.value)}
            onPressEnter={handleTestMagnet}
          />
          <Button 
            type="primary" 
            onClick={handleTestMagnet}
            loading={testingMagnet}
          >
            测试
          </Button>
        </Space.Compact>

        {renderTestResult()}
      </Modal>
    </div>
  )
}

export default DownloadFilterSettings