import React, { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  Statistic,
  Button,
  Space,
  Table,
  Tag,
  Alert,
  Modal,
  Progress,
  Descriptions,
  List,
  Typography,
  Divider,
  message,
  Popconfirm
} from 'antd'
import {
  ReloadOutlined,
  CloudUploadOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  SettingOutlined
} from '@ant-design/icons'
import { createFileRoute } from '@tanstack/react-router'
import {
  getVersionInfo,
  getVersionHistory,
  checkVersionUpdate,
  triggerMigration,
  checkMigrationRequirements,
  forceSaveVersion,
  getVersionStatus,
  type VersionInfo,
  type VersionStatus
} from '@/apis/version'

export const Route = createFileRoute('/_index/setting/version')({
  component: VersionManagement
})

const { Title, Text } = Typography

function VersionManagement() {
  const [versionInfo, setVersionInfo] = useState<VersionInfo | null>(null)
  const [versionStatus, setVersionStatus] = useState<VersionStatus | null>(null)
  const [versionHistory, setVersionHistory] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [migrationLoading, setMigrationLoading] = useState(false)
  const [migrationModalVisible, setMigrationModalVisible] = useState(false)

  // 加载版本信息
  const loadVersionInfo = async () => {
    try {
      setLoading(true)
      const [info, status, historyResponse] = await Promise.all([
        getVersionInfo(),
        getVersionStatus(),
        getVersionHistory()
      ])
      
      setVersionInfo(info)
      setVersionStatus(status.data)
      setVersionHistory(historyResponse.data?.history || [])
    } catch (error) {
      message.error('加载版本信息失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadVersionInfo()
  }, [])

  // 检查版本更新
  const handleCheckUpdate = async () => {
    try {
      setLoading(true)
      const response = await checkVersionUpdate()
      
      if (response.data?.is_updated) {
        message.warning('检测到版本更新，建议执行数据库迁移')
      } else {
        message.success('当前版本是最新的')
      }
      
      loadVersionInfo()
    } catch (error) {
      message.error('检查版本更新失败')
    } finally {
      setLoading(false)
    }
  }

  // 执行迁移
  const handleMigration = async (forceBackup: boolean = true, forceMigration: boolean = false) => {
    try {
      setMigrationLoading(true)
      
      // 先检查前置条件
      const requirementsResponse = await checkMigrationRequirements()
      
      if (!requirementsResponse.data?.all_satisfied && !forceMigration) {
        Modal.warning({
          title: '迁移前置条件不满足',
          content: (
            <div>
              <p>{requirementsResponse.data?.recommendation}</p>
              <ul>
                {requirementsResponse.data?.details.errors.map((error, index) => (
                  <li key={index}>{error}</li>
                ))}
              </ul>
            </div>
          )
        })
        return
      }
      
      // 执行迁移
      const migrationResponse = await triggerMigration({
        force_backup: forceBackup,
        force_migration: forceMigration
      })
      
      if (migrationResponse.success) {
        message.success('数据库迁移执行成功')
        setMigrationModalVisible(false)
        loadVersionInfo()
      } else {
        message.error(`数据库迁移执行失败: ${migrationResponse.message}`)
      }
      
    } catch (error) {
      message.error('执行数据库迁移失败')
    } finally {
      setMigrationLoading(false)
    }
  }

  // 强制保存版本
  const handleForceSave = async () => {
    try {
      await forceSaveVersion()
      message.success('版本信息已强制保存')
      loadVersionInfo()
    } catch (error) {
      message.error('强制保存版本信息失败')
    }
  }

  // 获取健康状态颜色
  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case 'excellent':
        return 'success'
      case 'good':
        return 'processing'
      case 'warning':
        return 'warning'
      case 'critical':
        return 'exception'
      default:
        return 'normal'
    }
  }

  // 获取健康状态图标
  const getHealthStatusIcon = (status: string) => {
    switch (status) {
      case 'excellent':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />
      case 'good':
        return <InfoCircleOutlined style={{ color: '#1890ff' }} />
      case 'warning':
        return <WarningOutlined style={{ color: '#faad14' }} />
      case 'critical':
        return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />
      default:
        return <InfoCircleOutlined />
    }
  }

  // 版本历史表格列
  const historyColumns = [
    {
      title: '版本',
      dataIndex: 'version',
      key: 'version',
      render: (version: string) => <Tag color="blue">{version}</Tag>
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      render: (time: string) => new Date(time).toLocaleString()
    },
    {
      title: '迁移状态',
      dataIndex: 'migration_success',
      key: 'migration_success',
      render: (success: boolean) => (
        <Tag color={success ? 'success' : 'error'}>
          {success ? '成功' : '失败'}
        </Tag>
      )
    }
  ]

  return (
    <div>
      {/* 版本状态概览 */}
      <Card title="版本状态概览" style={{ marginBottom: 24 }}>
        <Row gutter={16}>
          <Col span={6}>
            <Card>
              <Statistic
                title="当前版本"
                value={versionInfo?.current_version || 'N/A'}
                prefix={<SettingOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="系统健康度"
                value={versionStatus?.health_score || 0}
                suffix="%"
                valueStyle={{
                  color: versionStatus?.health_status === 'excellent' ? '#3f8600' :
                         versionStatus?.health_status === 'good' ? '#1890ff' :
                         versionStatus?.health_status === 'warning' ? '#cf1322' : '#cf1322'
                }}
                prefix={getHealthStatusIcon(versionStatus?.health_status || '')}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="存储版本"
                value={versionInfo?.stored_version || 'N/A'}
                prefix={<InfoCircleOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="版本状态"
                value={versionInfo?.is_updated ? '需要更新' : '已是最新'}
                valueStyle={{
                  color: versionInfo?.is_updated ? '#cf1322' : '#3f8600'
                }}
                prefix={versionInfo?.is_updated ? 
                  <ExclamationCircleOutlined /> : 
                  <CheckCircleOutlined />
                }
              />
            </Card>
          </Col>
        </Row>

        {/* 系统健康状态 */}
        {versionStatus && (
          <div style={{ marginTop: 16 }}>
            <Title level={5}>系统健康状态</Title>
            <Progress
              percent={versionStatus.health_score}
              status={getHealthStatusColor(versionStatus.health_status)}
              format={() => `${versionStatus.health_score}% - ${versionStatus.health_message}`}
            />
          </div>
        )}

        {/* 操作按钮 */}
        <div style={{ marginTop: 16 }}>
          <Space>
            <Button
              type="primary"
              icon={<ReloadOutlined />}
              onClick={handleCheckUpdate}
              loading={loading}
            >
              检查更新
            </Button>
            <Button
              icon={<CloudUploadOutlined />}
              onClick={() => setMigrationModalVisible(true)}
              disabled={!versionInfo?.is_updated}
            >
              执行迁移
            </Button>
            <Button onClick={loadVersionInfo} loading={loading}>
              刷新状态
            </Button>
            <Popconfirm
              title="确定要强制保存当前版本信息吗？"
              onConfirm={handleForceSave}
            >
              <Button type="dashed">
                强制保存版本
              </Button>
            </Popconfirm>
          </Space>
        </div>
      </Card>

      {/* 版本详细信息 */}
      <Row gutter={16}>
        <Col span={12}>
          <Card title="版本详细信息" size="small">
            <Descriptions column={1} size="small">
              <Descriptions.Item label="当前版本">
                {versionInfo?.current_version}
              </Descriptions.Item>
              <Descriptions.Item label="存储版本">
                {versionInfo?.stored_version || '未记录'}
              </Descriptions.Item>
              <Descriptions.Item label="最后更新">
                {versionInfo?.last_updated ? 
                  new Date(versionInfo.last_updated).toLocaleString() : 
                  '未记录'
                }
              </Descriptions.Item>
              <Descriptions.Item label="迁移状态">
                <Tag color={versionInfo?.migration_success ? 'success' : 'error'}>
                  {versionInfo?.migration_success ? '成功' : '失败'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="备注">
                {versionInfo?.notes || '无'}
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        <Col span={12}>
          <Card title="系统建议" size="small">
            {versionStatus?.recommendations && (
              <List
                size="small"
                dataSource={versionStatus.recommendations}
                renderItem={(item, index) => (
                  <List.Item>
                    <Text>{index + 1}. {item}</Text>
                  </List.Item>
                )}
              />
            )}
          </Card>
        </Col>
      </Row>

      {/* 版本历史 */}
      <Card title="版本历史" style={{ marginTop: 16 }}>
        <Table
          columns={historyColumns}
          dataSource={versionHistory}
          rowKey="version"
          size="small"
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* 警告信息 */}
      {versionInfo?.is_updated && (
        <Alert
          message="检测到版本更新"
          description="当前版本与存储版本不一致，建议执行数据库迁移以确保功能正常运行。"
          type="warning"
          showIcon
          style={{ marginTop: 16 }}
          action={
            <Button size="small" onClick={() => setMigrationModalVisible(true)}>
              立即迁移
            </Button>
          }
        />
      )}

      {/* 迁移执行对话框 */}
      <Modal
        title="执行数据库迁移"
        open={migrationModalVisible}
        onCancel={() => setMigrationModalVisible(false)}
        footer={null}
        width={600}
      >
        <div>
          <Alert
            message="重要提示"
            description="数据库迁移是一个重要操作，建议在执行前备份数据库。"
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />

          <Divider>迁移选项</Divider>

          <Space direction="vertical" style={{ width: '100%' }}>
            <Button
              type="primary"
              size="large"
              block
              loading={migrationLoading}
              onClick={() => handleMigration(true, false)}
            >
              标准迁移（推荐）
            </Button>
            <Text type="secondary">自动备份 + 条件检查 + 安全迁移</Text>

            <Button
              size="large"
              block
              loading={migrationLoading}
              onClick={() => handleMigration(false, false)}
            >
              快速迁移
            </Button>
            <Text type="secondary">跳过备份 + 条件检查 + 快速迁移</Text>

            <Button
              danger
              size="large"
              block
              loading={migrationLoading}
              onClick={() => handleMigration(true, true)}
            >
              强制迁移
            </Button>
            <Text type="secondary">忽略所有检查 + 强制执行（谨慎使用）</Text>
          </Space>
        </div>
      </Modal>
    </div>
  )
}

export default VersionManagement