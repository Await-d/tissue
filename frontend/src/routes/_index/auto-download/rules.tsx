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
  Statistic
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, PlayCircleOutlined, PauseCircleOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
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

const AutoDownloadRules: React.FC = () => {
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

  // 加载规则列表
  const loadRules = async (page = 1, pageSize = 20) => {
    try {
      setLoading(true)
      const response = await getRules({
        page,
        page_size: pageSize
      })
      setRules(response.items)
      setPagination({
        current: page,
        pageSize,
        total: response.total
      })
    } catch (error) {
      message.error('加载规则列表失败')
    } finally {
      setLoading(false)
    }
  }

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
    loadRules()
    loadStatistics()
  }, [])

  // 创建/更新规则
  const handleSubmit = async (values: any) => {
    try {
      if (editingRule) {
        await updateRule(editingRule.id, values)
        message.success('规则更新成功')
      } else {
        await createRule(values)
        message.success('规则创建成功')
      }
      setModalVisible(false)
      setEditingRule(null)
      form.resetFields()
      loadRules(pagination.current, pagination.pageSize)
      loadStatistics()
    } catch (error) {
      message.error(editingRule ? '规则更新失败' : '规则创建失败')
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
      render: (_, record) => (
        <Space direction="vertical" size="small">
          <div>评分 ≥ {record.min_rating}</div>
          <div>评论 ≥ {record.min_comments}</div>
          <div>时间: {record.time_range_value} {record.time_range_type === 'day' ? '天' : record.time_range_type === 'week' ? '周' : '月'}</div>
        </Space>
      ),
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
          <Col span={6}>
            <Card>
              <Statistic title="总规则数" value={statistics.total_rules} />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic title="活跃规则" value={statistics.active_rules} />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic title="总订阅数" value={statistics.total_subscriptions} />
            </Card>
          </Col>
          <Col span={6}>
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

      {/* 规则表格 */}
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
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            min_rating: 0,
            min_comments: 0,
            time_range_type: 'week',
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
            <Col span={12}>
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
            <Col span={12}>
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
            <Col span={12}>
              <Form.Item
                name="time_range_type"
                label="时间范围类型"
                rules={[{ required: true, message: '请选择时间范围类型' }]}
              >
                <Select>
                  <Option value="day">天</Option>
                  <Option value="week">周</Option>
                  <Option value="month">月</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
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
            <Col span={8}>
              <Form.Item name="is_hd" valuePropName="checked">
                <Switch checkedChildren="高清" unCheckedChildren="不限" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="is_zh" valuePropName="checked">
                <Switch checkedChildren="中文" unCheckedChildren="不限" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="is_uncensored" valuePropName="checked">
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

export default AutoDownloadRules