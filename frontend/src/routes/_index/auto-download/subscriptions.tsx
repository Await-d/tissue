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
import { DeleteOutlined, ReloadOutlined, SearchOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
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

const AutoDownloadSubscriptions: React.FC = () => {
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
      // 移除空值参数
      Object.keys(params).forEach(key => {
        if (params[key] === '' || params[key] === undefined) {
          delete params[key]
        }
      })
      
      const response = await getSubscriptions(params)
      setSubscriptions(response.items)
      setPagination({
        current: page,
        pageSize,
        total: response.total
      })
    } catch (error) {
      message.error('加载订阅记录失败')
    } finally {
      setLoading(false)
    }
  }

  // 加载规则列表
  const loadRules = async () => {
    try {
      const response = await getRules({ page: 1, page_size: 100 })
      setRules(response.items)
    } catch (error) {
      message.error('加载规则列表失败')
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
  const handleBatchOperation = async (action: string) => {
    if (selectedRowKeys.length === 0) {
      message.warning('请选择要操作的记录')
      return
    }

    try {
      await batchOperation({
        ids: selectedRowKeys as number[],
        action: action as any
      })
      message.success('操作成功')
      setSelectedRowKeys([])
      loadSubscriptions(pagination.current, pagination.pageSize)
    } catch (error) {
      message.error('操作失败')
    }
  }

  // 应用筛选
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

  // 状态颜色映射
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'default'
      case 'downloading':
        return 'processing'
      case 'completed':
        return 'success'
      case 'failed':
        return 'error'
      default:
        return 'default'
    }
  }

  // 状态文本映射
  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending':
        return '待处理'
      case 'downloading':
        return '下载中'
      case 'completed':
        return '已完成'
      case 'failed':
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
          {record.status === 'failed' && (
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
      width: 120
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
        <Row gutter={16} align="middle">
          <Col span={4}>
            <Select
              placeholder="选择规则"
              allowClear
              value={filters.rule_id}
              onChange={(value) => setFilters(prev => ({ ...prev, rule_id: value }))}
              style={{ width: '100%' }}
            >
              {rules.map(rule => (
                <Option key={rule.id} value={rule.id}>
                  {rule.name}
                </Option>
              ))}
            </Select>
          </Col>
          <Col span={3}>
            <Select
              placeholder="状态"
              allowClear
              value={filters.status}
              onChange={(value) => setFilters(prev => ({ ...prev, status: value }))}
              style={{ width: '100%' }}
            >
              <Option value="pending">待处理</Option>
              <Option value="downloading">下载中</Option>
              <Option value="completed">已完成</Option>
              <Option value="failed">失败</Option>
            </Select>
          </Col>
          <Col span={4}>
            <Search
              placeholder="搜索番号"
              value={filters.num}
              onChange={(e) => setFilters(prev => ({ ...prev, num: e.target.value }))}
              onSearch={handleSearch}
            />
          </Col>
          <Col span={6}>
            <RangePicker
              onChange={(dates, dateStrings) => {
                setFilters(prev => ({
                  ...prev,
                  start_date: dateStrings[0],
                  end_date: dateStrings[1]
                }))
              }}
            />
          </Col>
          <Col span={7}>
            <Space>
              <Button
                type="primary"
                icon={<SearchOutlined />}
                onClick={handleSearch}
              >
                搜索
              </Button>
              <Button onClick={handleReset}>
                重置
              </Button>
              <Button onClick={() => loadSubscriptions()}>
                刷新
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 批量操作栏 */}
      {selectedRowKeys.length > 0 && (
        <Card style={{ marginBottom: 16 }}>
          <Space>
            <span>已选择 {selectedRowKeys.length} 项</span>
            <Popconfirm
              title="确定要删除选中的记录吗？"
              onConfirm={() => handleBatchOperation('delete')}
            >
              <Button danger>
                批量删除
              </Button>
            </Popconfirm>
            <Button onClick={() => handleBatchOperation('retry')}>
              批量重试
            </Button>
            <Button onClick={() => setSelectedRowKeys([])}>
              取消选择
            </Button>
          </Space>
        </Card>
      )}

      {/* 订阅记录表格 */}
      <Table
        columns={columns}
        dataSource={subscriptions}
        rowKey="id"
        loading={loading}
        rowSelection={rowSelection}
        pagination={{
          current: pagination.current,
          pageSize: pagination.pageSize,
          total: pagination.total,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (page, pageSize) => {
            loadSubscriptions(page, pageSize)
          }
        }}
        scroll={{ x: 1200 }}
      />
    </div>
  )
}

export default AutoDownloadSubscriptions