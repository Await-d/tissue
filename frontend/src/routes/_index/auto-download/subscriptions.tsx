import React, { useState, useEffect } from 'react'
import {
  Table,
  Button,
  Space,
  Tag,
  Input,
  Select,
  DatePicker,
  message,
  Popconfirm,
  Card,
  Row,
  Col,
  Image
} from 'antd'
import { DeleteOutlined, ReloadOutlined, SearchOutlined, EyeOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { createFileRoute, useNavigate } from '@tanstack/react-router'
import {
  getSubscriptions,
  deleteSubscription,
  batchOperation,
  getRules,
  type AutoDownloadSubscription,
  type AutoDownloadRule
} from '@/apis/autoDownload'

const { Search } = Input
const { Option } = Select
const { RangePicker } = DatePicker

function AutoDownloadSubscriptions() {
  const navigate = useNavigate()
  const [subscriptions, setSubscriptions] = useState<AutoDownloadSubscription[]>([])
  const [rules, setRules] = useState<AutoDownloadRule[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
  const [filters, setFilters] = useState({
    rule_id: undefined as number | undefined,
    status: undefined as string | undefined,
    num: '',
    start_date: '',
    end_date: ''
  })
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0
  })

  // 加载订阅记录列表
  const loadSubscriptions = async (page = 1, pageSize = 20) => {
    try {
      setLoading(true)
      const params = {
        page,
        page_size: pageSize,
        ...filters
      }
      const response = await getSubscriptions(params)
      const { items = [], total = 0 } = response.data || {}
      
      setSubscriptions(items)
      setPagination({
        current: page,
        pageSize,
        total: total
      })
    } catch (error) {
      message.error('加载订阅记录失败')
      setSubscriptions([])
    } finally {
      setLoading(false)
    }
  }

  // 加载规则列表
  const loadRules = async () => {
    try {
      const response = await getRules({ page: 1, page_size: 100 })
      const { items = [] } = response.data || {}
      setRules(items)
    } catch (error) {
      message.error('加载规则列表失败')
      setRules([])
    }
  }

  useEffect(() => {
    loadSubscriptions()
    loadRules()
  }, [])

  // 删除订阅记录
  const handleDelete = async (id: number) => {
    try {
      await deleteSubscription(id)
      message.success('删除成功')
      loadSubscriptions(pagination.current, pagination.pageSize)
    } catch (error) {
      message.error('删除失败')
    }
  }

  // 批量操作
  const handleBatchOperation = async (action: "delete" | "pause" | "retry" | "resume") => {
    if (selectedRowKeys.length === 0 && action !== 'retry') {
      message.warning('请选择要操作的记录')
      return
    }

    try {
      const ids = action === 'retry' ? [] : selectedRowKeys.map(key => Number(key))
      await batchOperation({
        action,
        ids: ids
      })
      message.success('操作成功')
      setSelectedRowKeys([])
      loadSubscriptions(pagination.current, pagination.pageSize)
    } catch (error) {
      message.error('操作失败')
    }
  }

  // 表格筛选
  const handleTableChange = (pagination: any) => {
    loadSubscriptions(pagination.current, pagination.pageSize)
  }

  // 搜索
  const handleSearch = () => {
    loadSubscriptions(1, pagination.pageSize)
  }

  // 重置筛选
  const handleReset = () => {
    setFilters({
      rule_id: undefined,
      status: undefined,
      num: '',
      start_date: '',
      end_date: ''
    })
    loadSubscriptions(1, pagination.pageSize)
  }

  // 查看详情
  const handleViewDetail = (record: AutoDownloadSubscription) => {
    navigate({
      to: '/search',
      search: {
        num: record.num
      }
    })
  }

  // 状态颜色映射
  const getStatusColor = (status: string) => {
    const upperStatus = status?.toUpperCase()
    switch (upperStatus) {
      case 'PENDING':
        return 'default'
      case 'DOWNLOADING':
        return 'processing'
      case 'COMPLETED':
        return 'success'
      case 'FAILED':
        return 'error'
      default:
        return 'default'
    }
  }

  // 状态文本映射
  const getStatusText = (status: string) => {
    const upperStatus = status?.toUpperCase()
    switch (upperStatus) {
      case 'PENDING':
        return '待处理'
      case 'DOWNLOADING':
        return '下载中'
      case 'COMPLETED':
        return '已完成'
      case 'FAILED':
        return '失败'
      default:
        return status
    }
  }

  // 表格列定义
  const columns: ColumnsType<AutoDownloadSubscription> = [
    {
      title: '封面',
      dataIndex: 'cover',
      key: 'cover',
      width: 80,
      render: (cover: string) => (
        cover ? (
          <Image
            src={cover}
            alt="封面"
            width={60}
            height={40}
            style={{ objectFit: 'cover' }}
            fallback="data:image/png;base64,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"
          />
        ) : (
          <div style={{ width: 60, height: 40, background: '#f5f5f5', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            无图
          </div>
        )
      )
    },
    {
      title: '番号',
      dataIndex: 'num',
      key: 'num',
      width: 120
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      width: 200
    },
    {
      title: '规则',
      dataIndex: 'rule_name',
      key: 'rule_name',
      width: 120
    },
    {
      title: '评分/评论',
      key: 'rating_comments',
      render: (_, record) => (
        <Space direction="vertical" size="small">
          <div>评分: {record.rating || 'N/A'}</div>
          <div>评论: {record.comments_count || 0}</div>
        </Space>
      ),
      width: 100
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {getStatusText(status)}
        </Tag>
      ),
      width: 100
    },
    {
      title: '下载时间',
      dataIndex: 'download_time',
      key: 'download_time',
      render: (time: string) => time ? new Date(time).toLocaleString() : '-',
      width: 140
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time: string) => new Date(time).toLocaleString(),
      width: 140
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            查看详情
          </Button>
          {record.status?.toLowerCase() === 'failed' && (
            <Button
              type="text"
              icon={<ReloadOutlined />}
              onClick={() => handleBatchOperation('retry')}
            >
              重试
            </Button>
          )}
          <Popconfirm
            title="确定要删除这条记录吗？"
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

  // 表格行选择配置
  const rowSelection = {
    selectedRowKeys,
    onChange: (newSelectedRowKeys: React.Key[]) => {
      setSelectedRowKeys(newSelectedRowKeys)
    }
  }

  return (
    <div>
      {/* 筛选栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={6}>
            <Input.Search
              placeholder="搜索番号"
              value={filters.num}
              onChange={(e) => setFilters(prev => ({ ...prev, num: e.target.value }))}
              onSearch={handleSearch}
            />
          </Col>
          <Col span={4}>
            <Select
              placeholder="选择规则"
              value={filters.rule_id}
              onChange={(value) => setFilters(prev => ({ ...prev, rule_id: value }))}
              allowClear
              style={{ width: '100%' }}
            >
              {rules.map(rule => (
                <Option key={rule.id} value={rule.id}>
                  {rule.name}
                </Option>
              ))}
            </Select>
          </Col>
          <Col span={4}>
            <Select
              placeholder="选择状态"
              value={filters.status}
              onChange={(value) => setFilters(prev => ({ ...prev, status: value }))}
              allowClear
              style={{ width: '100%' }}
            >
              <Option value="pending">待处理</Option>
              <Option value="downloading">下载中</Option>
              <Option value="completed">已完成</Option>
              <Option value="failed">失败</Option>
            </Select>
          </Col>
          <Col span={6}>
            <RangePicker
              style={{ width: '100%' }}
              onChange={(dates) => {
                if (dates && dates.length === 2) {
                  setFilters(prev => ({
                    ...prev,
                    start_date: dates[0]?.format('YYYY-MM-DD') || '',
                    end_date: dates[1]?.format('YYYY-MM-DD') || ''
                  }))
                } else {
                  setFilters(prev => ({
                    ...prev,
                    start_date: '',
                    end_date: ''
                  }))
                }
              }}
            />
          </Col>
          <Col span={4}>
            <Space>
              <Button
                type="primary"
                icon={<SearchOutlined />}
                onClick={handleSearch}
              >
                搜索
              </Button>
              <Button onClick={handleReset}>重置</Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 批量操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Button
            danger
            disabled={selectedRowKeys.length === 0}
            onClick={() => handleBatchOperation('delete')}
          >
            批量删除
          </Button>
          <Button
            disabled={selectedRowKeys.length === 0}
            onClick={() => handleBatchOperation('retry')}
          >
            批量重试
          </Button>
          <span>已选择 {selectedRowKeys.length} 项</span>
        </Space>
      </Card>

      {/* 数据表格 */}
      <Card>
        <Table
          columns={columns}
          dataSource={subscriptions}
          rowKey="id"
          loading={loading}
          rowSelection={rowSelection}
          pagination={{
            ...pagination,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `第 ${range[0]}-${range[1]} 条/共 ${total} 条`
          }}
          onChange={handleTableChange}
          scroll={{ x: 1200 }}
        />
      </Card>
    </div>
  )
}

export const Route = createFileRoute('/_index/auto-download/subscriptions')({
  component: AutoDownloadSubscriptions
})

export default AutoDownloadSubscriptions