import React, { useState, useEffect } from 'react'
import {
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  InputNumber,
  Select,
  Switch,
  message,
  Popconfirm,
  Card,
  Row,
  Col,
  Statistic,
  List,
  Avatar,
  Divider,
  Grid
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, PlayCircleOutlined, PauseCircleOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { createFileRoute } from '@tanstack/react-router'
import {
  getRules,
  createRule,
  updateRule,
  deleteRule,
  toggleRule,
  getStatistics,
  triggerAutoDownload,
  type AutoDownloadRule,
  type AutoDownloadStatistics
} from '@/apis/autoDownload'

const { Option } = Select
const { useBreakpoint } = Grid

function AutoDownloadRules() {
  const [rules, setRules] = useState<AutoDownloadRule[]>([])
  const [statistics, setStatistics] = useState<AutoDownloadStatistics | null>(null)
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingRule, setEditingRule] = useState<AutoDownloadRule | null>(null)
  const [form] = Form.useForm()
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0
  })
  const screens = useBreakpoint()

  // 加载规则列表
  const loadRules = async (page = 1, pageSize = 20) => {
    try {
      setLoading(true)
      const response = await getRules({
        page,
        page_size: pageSize
      })
      console.log('接收到的规则数据:', response)
      
      // API返回的数据在response.data中
      const { items = [], total = 0 } = response.data || {};
      
      setRules(items)
      setPagination({
        current: page,
        pageSize,
        total: total
      })
    } catch (error) {
      console.error('加载规则失败:', error)
      message.error('加载规则列表失败')
      setRules([]) // 确保在错误情况下rules为空数组
    } finally {
      setLoading(false)
    }
  }

  // 加载统计信息
  const loadStatistics = async () => {
    try {
      const stats = await getStatistics()
      console.log('获取到的统计数据:', stats)
      setStatistics(stats)
    } catch (error) {
      console.error('加载统计信息失败:', error)
      message.error('加载统计信息失败')
    }
  }

  useEffect(() => {
    loadRules()
    loadStatistics()
  }, [])

  // 创建/更新规则
  const handleSubmit = async (values: any) => {
    try {
      console.log('提交表单数据:', values)
      if (editingRule) {
        console.log('更新规则:', editingRule.id, values)
        await updateRule(editingRule.id, values)
        message.success('规则更新成功')
      } else {
        console.log('创建新规则:', values)
        const result = await createRule(values)
        console.log('创建规则响应:', result)
        message.success('规则创建成功')
      }
      setModalVisible(false)
      setEditingRule(null)
      form.resetFields()
      loadRules(pagination.current, pagination.pageSize)
      loadStatistics()
    } catch (error: any) {
      console.error('创建规则失败:', error)
      console.error('错误详情:', error?.response?.data)
      const errorMessage = error?.response?.data?.detail || error?.message || '未知错误'
      message.error(`${editingRule ? '规则更新失败' : '规则创建失败'}: ${errorMessage}`)
    }
  }

  // 删除规则
  const handleDelete = async (id: number) => {
    try {
      await deleteRule(id)
      message.success('规则删除成功')
      loadRules(pagination.current, pagination.pageSize)
      loadStatistics()
    } catch (error) {
      message.error('规则删除失败')
    }
  }

  // 切换规则状态
  const handleToggle = async (id: number, enabled: boolean) => {
    try {
      await toggleRule(id, enabled)
      message.success(`规则已${enabled ? '启用' : '禁用'}`)
      loadRules(pagination.current, pagination.pageSize)
      loadStatistics()
    } catch (error) {
      message.error('操作失败')
    }
  }

  // 手动触发
  const handleTrigger = async (ruleIds?: number[]) => {
    try {
      setLoading(true)
      await triggerAutoDownload({ rule_ids: ruleIds })
      message.success('触发成功')
      loadStatistics()
    } catch (error) {
      message.error('触发失败')
    } finally {
      setLoading(false)
    }
  }

  // 打开编辑对话框
  const handleEdit = (rule: AutoDownloadRule) => {
    setEditingRule(rule)
    form.setFieldsValue(rule)
    setModalVisible(true)
  }

  // 表格列定义
  const columns: ColumnsType<AutoDownloadRule> = [
    {
      title: '规则名称',
      dataIndex: 'name',
      key: 'name',
      width: 150
    },
    {
      title: '筛选条件',
      key: 'conditions',
      render: (_, record) => {
        // 确保time_range_type是大写的
        const timeRangeType = record.time_range_type?.toUpperCase();
        return (
          <Space direction="vertical" size="small">
            <div>评分 ≥ {record.min_rating}</div>
            <div>评论 ≥ {record.min_comments}</div>
            <div>时间: {record.time_range_value} {timeRangeType === 'DAY' ? '天' : timeRangeType === 'WEEK' ? '周' : '月'}</div>
            <div style={{ fontSize: '10px', color: '#999' }}>枚举值: {record.time_range_type}</div>
          </Space>
        );
      },
      width: 120
    },
    {
      title: '质量要求',
      key: 'quality',
      render: (_, record) => (
        <Space>
          {record.is_hd && <Tag color="blue">高清</Tag>}
          {record.is_zh && <Tag color="green">中文</Tag>}
          {record.is_uncensored && <Tag color="red">无码</Tag>}
        </Space>
      ),
      width: 120
    },
    {
      title: '状态',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      render: (enabled: boolean) => (
        <Tag color={enabled ? 'green' : 'default'}>
          {enabled ? '启用' : '禁用'}
        </Tag>
      ),
      width: 80
    },
    {
      title: '统计',
      key: 'stats',
      render: (_, record) => (
        <Space direction="vertical" size="small">
          <div>订阅: {record.subscription_count || 0}</div>
          <div>成功: {record.success_count || 0}</div>
        </Space>
      ),
      width: 80
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time: string) => new Date(time).toLocaleDateString(),
      width: 100
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button
            type="text"
            icon={record.is_enabled ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
            onClick={() => handleToggle(record.id, !record.is_enabled)}
          >
            {record.is_enabled ? '禁用' : '启用'}
          </Button>
          <Button
            type="text"
            onClick={() => handleTrigger([record.id])}
          >
            执行
          </Button>
          <Popconfirm
            title="确定要删除这个规则吗？"
            onConfirm={() => handleDelete(record.id)}
          >
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
      width: 200
    }
  ]

  return (
    <div>
      {/* 统计卡片 */}
      {statistics && (
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic title="总规则数" value={statistics.total_rules} />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic title="活跃规则" value={statistics.active_rules} />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic title="总订阅数" value={statistics.total_subscriptions} />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic 
                title="成功率" 
                value={statistics.success_rate} 
                suffix="%" 
                precision={1}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 操作栏 */}
      <div style={{ marginBottom: 16 }}>
        <Space>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              setEditingRule(null)
              form.resetFields()
              setModalVisible(true)
            }}
          >
            创建规则
          </Button>
          <Button
            onClick={() => handleTrigger()}
            loading={loading}
          >
            执行所有规则
          </Button>
          <Button onClick={() => loadRules()}>
            刷新
          </Button>
        </Space>
      </div>

      {/* 规则显示 - 根据屏幕大小选择表格或卡片 */}
      {screens.md ? (
        // 桌面模式：使用表格
        <Table
          columns={columns}
          dataSource={rules}
          rowKey="id"
          loading={loading}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, pageSize) => {
              loadRules(page, pageSize)
            }
          }}
        />
      ) : (
        // 手机模式：使用卡片列表
        <List
          loading={loading}
          dataSource={rules}
          renderItem={(rule) => (
            <List.Item style={{ padding: 0, marginBottom: 16 }}>
              <Card
                size="small"
                title={
                  <Space>
                    <span>{rule.name}</span>
                    <Tag color={rule.is_enabled ? 'green' : 'default'}>
                      {rule.is_enabled ? '启用' : '禁用'}
                    </Tag>
                  </Space>
                }
                extra={
                  <Space>
                    <Button
                      type="text"
                      size="small"
                      icon={<EditOutlined />}
                      onClick={() => handleEdit(rule)}
                    />
                    <Button
                      type="text"
                      size="small"
                      icon={rule.is_enabled ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
                      onClick={() => handleToggle(rule.id, !rule.is_enabled)}
                    />
                  </Space>
                }
                style={{ width: '100%' }}
              >
                <Row gutter={[16, 8]}>
                  <Col span={24}>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      <div>评分 ≥ {rule.min_rating} | 评论 ≥ {rule.min_comments}</div>
                      <div>时间: {rule.time_range_value} {rule.time_range_type === 'DAY' ? '天' : rule.time_range_type === 'WEEK' ? '周' : '月'}</div>
                    </div>
                  </Col>
                  <Col span={24}>
                    <Space size="small">
                      {rule.is_hd && <Tag color="blue">高清</Tag>}
                      {rule.is_zh && <Tag color="green">中文</Tag>}
                      {rule.is_uncensored && <Tag color="red">无码</Tag>}
                    </Space>
                  </Col>
                  <Col span={12}>
                    <div style={{ fontSize: '12px', color: '#999' }}>
                      订阅: {rule.subscription_count || 0} | 成功: {rule.success_count || 0}
                    </div>
                  </Col>
                  <Col span={12}>
                    <div style={{ fontSize: '12px', color: '#999', textAlign: 'right' }}>
                      {new Date(rule.created_at).toLocaleDateString()}
                    </div>
                  </Col>
                </Row>
                <Divider style={{ margin: '8px 0' }} />
                <Row gutter={8}>
                  <Col span={8}>
                    <Button
                      type="text"
                      size="small"
                      block
                      onClick={() => handleTrigger([rule.id])}
                    >
                      执行
                    </Button>
                  </Col>
                  <Col span={8}>
                    <Button
                      type="text"
                      size="small"
                      block
                      onClick={() => handleToggle(rule.id, !rule.is_enabled)}
                    >
                      {rule.is_enabled ? '禁用' : '启用'}
                    </Button>
                  </Col>
                  <Col span={8}>
                    <Popconfirm
                      title="确定要删除这个规则吗？"
                      onConfirm={() => handleDelete(rule.id)}
                    >
                      <Button
                        type="text"
                        size="small"
                        danger
                        block
                      >
                        删除
                      </Button>
                    </Popconfirm>
                  </Col>
                </Row>
              </Card>
            </List.Item>
          )}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: false,
            showQuickJumper: false,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, pageSize) => {
              loadRules(page, pageSize)
            }
          }}
        />
      )}

      {/* 创建/编辑对话框 */}
      <Modal
        title={editingRule ? '编辑规则' : '创建规则'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false)
          setEditingRule(null)
          form.resetFields()
        }}
        onOk={() => form.submit()}
        width={screens.md ? 600 : '90%'}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            min_rating: 0,
            min_comments: 0,
            time_range_type: 'WEEK',
            time_range_value: 1,
            is_hd: true,
            is_zh: false,
            is_uncensored: false,
            is_enabled: true
          }}
        >
          <Form.Item
            name="name"
            label="规则名称"
            rules={[{ required: true, message: '请输入规则名称' }]}
          >
            <Input placeholder="输入规则名称" />
          </Form.Item>

          <Row gutter={16}>
            <Col xs={24} sm={12}>
              <Form.Item
                name="min_rating"
                label="最低评分"
                rules={[{ required: true, message: '请输入最低评分' }]}
              >
                <InputNumber
                  min={0}
                  max={10}
                  step={0.1}
                  placeholder="0.0"
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item
                name="min_comments"
                label="最低评论数"
                rules={[{ required: true, message: '请输入最低评论数' }]}
              >
                <InputNumber
                  min={0}
                  placeholder="0"
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} sm={12}>
              <Form.Item
                name="time_range_type"
                label="时间范围类型"
                rules={[{ required: true, message: '请选择时间范围类型' }]}
              >
                <Select>
                  <Option value="DAY">天</Option>
                  <Option value="WEEK">周</Option>
                  <Option value="MONTH">月</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item
                name="time_range_value"
                label="时间范围值"
                rules={[{ required: true, message: '请输入时间范围值' }]}
              >
                <InputNumber
                  min={1}
                  placeholder="1"
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} sm={8}>
              <Form.Item name="is_hd" valuePropName="checked" label="质量要求">
                <Switch checkedChildren="高清" unCheckedChildren="不限" />
              </Form.Item>
            </Col>
            <Col xs={24} sm={8}>
              <Form.Item name="is_zh" valuePropName="checked" label=" ">
                <Switch checkedChildren="中文" unCheckedChildren="不限" />
              </Form.Item>
            </Col>
            <Col xs={24} sm={8}>
              <Form.Item name="is_uncensored" valuePropName="checked" label=" ">
                <Switch checkedChildren="无码" unCheckedChildren="不限" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="is_enabled" valuePropName="checked">
            <Switch checkedChildren="启用" unCheckedChildren="禁用" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export const Route = createFileRoute('/_index/auto-download/rules')({
  component: AutoDownloadRules
})

export default AutoDownloadRules