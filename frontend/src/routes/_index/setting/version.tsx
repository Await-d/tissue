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
  App,
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
  const { message, modal } = App.useApp()
  const [versionInfo, setVersionInfo] = useState<VersionInfo | null>(null)
  const [versionStatus, setVersionStatus] = useState<VersionStatus | null>(null)
  const [versionHistory, setVersionHistory] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [migrationLoading, setMigrationLoading] = useState(false)
  const [migrationModalVisible, setMigrationModalVisible] = useState(false)

  const loadVersionInfo = async () => {
    try {
      setLoading(true)
      const [info, status, historyResponse] = await Promise.all([
        getVersionInfo(),
        getVersionStatus(),
        getVersionHistory()
      ])
      
      setVersionInfo(info)
      setVersionStatus(status.data || null)
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

  const handleMigration = async (forceBackup: boolean = true, forceMigration: boolean = false) => {
    try {
      setMigrationLoading(true)
      
      const requirementsResponse = await checkMigrationRequirements()
      
      if (!requirementsResponse.data?.all_satisfied && !forceMigration) {
        modal.warning({
          title: '迁移前置条件不满足',
          content: (
            <div>
              <p>{requirementsResponse.data?.recommendation}</p>
              <ul>
                {requirementsResponse.data?.details.errors.map((error: string, index: number) => (
                  <li key={index}>{error}</li>
                ))}
              </ul>
            </div>
          )
        })
        return
      }
      
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

  const handleForceSave = async () => {
    try {
      await forceSaveVersion()
      message.success('版本信息已强制保存')
      loadVersionInfo()
    } catch (error) {
      message.error('强制保存版本信息失败')
    }
  }

  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case 'excellent': return 'success'
      case 'good': return 'processing'
      case 'warning': return 'warning'
      case 'critical': return 'exception'
      default: return 'normal'
    }
  }

  const getHealthStatusIcon = (status: string) => {
    switch (status) {
      case 'excellent':
        return <CheckCircleOutlined className="text-[#52c41a]" />
      case 'good':
        return <InfoCircleOutlined className="text-[#1890ff]" />
      case 'warning':
        return <WarningOutlined className="text-[#faad14]" />
      case 'critical':
        return <ExclamationCircleOutlined className="text-[#ff4d4f]" />
      default:
        return <InfoCircleOutlined />
    }
  }

  const historyColumns = [
    {
      title: <span className="text-[#f0f0f2]">版本</span>,
      dataIndex: 'version',
      key: 'version',
      render: (version: string) => <Tag color="blue" className="border-0 bg-[#d4a852]/20 text-[#d4a852]">{version}</Tag>
    },
    {
      title: <span className="text-[#f0f0f2]">更新时间</span>,
      dataIndex: 'updated_at',
      key: 'updated_at',
      render: (time: string) => <span className="text-[#a0a0a8]">{new Date(time).toLocaleString()}</span>
    },
    {
      title: <span className="text-[#f0f0f2]">迁移状态</span>,
      dataIndex: 'migration_success',
      key: 'migration_success',
      render: (success: boolean) => (
        <Tag color={success ? 'success' : 'error'} className="border-0">
          {success ? '成功' : '失败'}
        </Tag>
      )
    }
  ]

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* 版本状态概览 */}
      <div className="bg-[#1a1a1d] rounded-2xl border border-white/8 shadow-2xl overflow-hidden mb-6">
        <div className="px-8 py-6 border-b border-white/8 bg-gradient-to-r from-[#141416] to-[#1a1a1d]">
          <h2 className="text-2xl font-bold text-[#d4a852] flex items-center gap-3">
            <span className="w-1.5 h-8 bg-gradient-to-b from-[#d4a852] to-[#b08d3e] rounded-full"></span>
            版本状态概览
          </h2>
          <p className="text-[#a0a0a8] text-sm mt-2 ml-6">系统版本信息和健康状态监控</p>
        </div>

        <div className="p-8">
          <Row gutter={16}>
            <Col span={6}>
              <div className="bg-[#141416] rounded-lg p-6 border border-white/8">
                <div className="flex items-center gap-3 mb-2">
                  <SettingOutlined className="text-[#d4a852] text-xl" />
                  <div className="text-[#6a6a72] text-xs">当前版本</div>
                </div>
                <div className="text-[#f0f0f2] text-2xl font-bold">{versionInfo?.current_version || 'N/A'}</div>
              </div>
            </Col>
            <Col span={6}>
              <div className="bg-[#141416] rounded-lg p-6 border border-white/8">
                <div className="flex items-center gap-3 mb-2">
                  {getHealthStatusIcon(versionStatus?.health_status || '')}
                  <div className="text-[#6a6a72] text-xs">系统健康度</div>
                </div>
                <div className="text-[#d4a852] text-2xl font-bold">
                  {versionStatus?.health_score || 0}
                  <span className="text-sm text-[#6a6a72] ml-1">%</span>
                </div>
              </div>
            </Col>
            <Col span={6}>
              <div className="bg-[#141416] rounded-lg p-6 border border-white/8">
                <div className="flex items-center gap-3 mb-2">
                  <InfoCircleOutlined className="text-[#6a6a72] text-xl" />
                  <div className="text-[#6a6a72] text-xs">存储版本</div>
                </div>
                <div className="text-[#f0f0f2] text-2xl font-bold">{versionInfo?.stored_version || 'N/A'}</div>
              </div>
            </Col>
            <Col span={6}>
              <div className="bg-[#141416] rounded-lg p-6 border border-white/8">
                <div className="flex items-center gap-3 mb-2">
                  {versionInfo?.is_updated ? 
                    <ExclamationCircleOutlined className="text-red-500 text-xl" /> : 
                    <CheckCircleOutlined className="text-green-500 text-xl" />
                  }
                  <div className="text-[#6a6a72] text-xs">版本状态</div>
                </div>
                <div className={`text-xl font-bold ${versionInfo?.is_updated ? 'text-red-400' : 'text-green-400'}`}>
                  {versionInfo?.is_updated ? '需要更新' : '已是最新'}
                </div>
              </div>
            </Col>
          </Row>

          {versionStatus && (
            <div className="mt-6 pt-6 border-t border-white/8">
              <div className="flex items-center gap-3 mb-3">
                <span className="text-[#e8c780] font-semibold">系统健康状态</span>
                <span className="text-[#6a6a72] text-sm">{versionStatus.health_message}</span>
              </div>
              <Progress
                percent={versionStatus.health_score}
                strokeColor={{
                  '0%': '#d4a852',
                  '100%': '#e8c780',
                }}
                trailColor="#222226"
                className="custom-progress-gold"
              />
            </div>
          )}

          <div className="flex gap-4 mt-6">
            <Button
              type="primary"
              icon={<ReloadOutlined />}
              onClick={handleCheckUpdate}
              loading={loading}
              size="large"
              className="bg-gradient-to-r from-[#d4a852] to-[#b08d3e] border-0 text-[#0d0d0f] font-semibold hover:from-[#e8c780] hover:to-[#d4a852]"
            >
              检查更新
            </Button>
            <Button
              icon={<CloudUploadOutlined />}
              onClick={() => setMigrationModalVisible(true)}
              disabled={!versionInfo?.is_updated}
              size="large"
              className="bg-[#222226] border-white/8 text-[#d4a852] hover:border-[#d4a852] hover:text-[#e8c780] disabled:opacity-50"
            >
              执行迁移
            </Button>
            <Button
              onClick={loadVersionInfo}
              loading={loading}
              size="large"
              className="bg-[#222226] border-white/8 text-[#a0a0a8] hover:border-white/20 hover:text-[#f0f0f2]"
            >
              刷新状态
            </Button>
            <Popconfirm
              title="确定要强制保存当前版本信息吗？"
              onConfirm={handleForceSave}
              okText="确定"
              cancelText="取消"
            >
              <Button
                size="large"
                className="bg-[#222226] border-white/8 text-[#a0a0a8] hover:border-white/20 hover:text-[#f0f0f2]"
              >
                强制保存版本
              </Button>
            </Popconfirm>
          </div>
        </div>
      </div>

      {/* 版本详细信息和系统建议 */}
      <Row gutter={16} className="mb-6">
        <Col span={12}>
          <div className="bg-[#1a1a1d] rounded-2xl border border-white/8 shadow-2xl overflow-hidden h-full">
            <div className="px-6 py-4 border-b border-white/8 bg-gradient-to-r from-[#141416] to-[#1a1a1d]">
              <h3 className="text-lg font-bold text-[#e8c780] flex items-center gap-2">
                <span className="w-1 h-5 bg-[#d4a852] rounded-full"></span>
                版本详细信息
              </h3>
            </div>
            <div className="p-6">
              <Descriptions column={1} size="small" className="version-descriptions">
                <Descriptions.Item label={<span className="text-[#6a6a72]">当前版本</span>}>
                  <span className="text-[#f0f0f2]">{versionInfo?.current_version}</span>
                </Descriptions.Item>
                <Descriptions.Item label={<span className="text-[#6a6a72]">存储版本</span>}>
                  <span className="text-[#f0f0f2]">{versionInfo?.stored_version || '未记录'}</span>
                </Descriptions.Item>
                <Descriptions.Item label={<span className="text-[#6a6a72]">最后更新</span>}>
                  <span className="text-[#f0f0f2]">
                    {versionInfo?.last_updated ? 
                      new Date(versionInfo.last_updated).toLocaleString() : 
                      '未记录'
                    }
                  </span>
                </Descriptions.Item>
                <Descriptions.Item label={<span className="text-[#6a6a72]">迁移状态</span>}>
                  <Tag color={versionInfo?.migration_success ? 'success' : 'error'} className="border-0">
                    {versionInfo?.migration_success ? '成功' : '失败'}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label={<span className="text-[#6a6a72]">备注</span>}>
                  <span className="text-[#f0f0f2]">{versionInfo?.notes || '无'}</span>
                </Descriptions.Item>
              </Descriptions>
            </div>
          </div>
        </Col>

        <Col span={12}>
          <div className="bg-[#1a1a1d] rounded-2xl border border-white/8 shadow-2xl overflow-hidden h-full">
            <div className="px-6 py-4 border-b border-white/8 bg-gradient-to-r from-[#141416] to-[#1a1a1d]">
              <h3 className="text-lg font-bold text-[#e8c780] flex items-center gap-2">
                <span className="w-1 h-5 bg-[#d4a852] rounded-full"></span>
                系统建议
              </h3>
            </div>
            <div className="p-6">
              {versionStatus?.recommendations && (
                <List
                  size="small"
                  dataSource={versionStatus.recommendations}
                  renderItem={(item: string, index: number) => (
                    <List.Item className="border-0 py-2">
                      <div className="flex items-start gap-2">
                        <span className="text-[#d4a852] font-bold">{index + 1}.</span>
                        <span className="text-[#a0a0a8]">{item}</span>
                      </div>
                    </List.Item>
                  )}
                />
              )}
            </div>
          </div>
        </Col>
      </Row>

      {/* 版本历史 */}
      <div className="bg-[#1a1a1d] rounded-2xl border border-white/8 shadow-2xl overflow-hidden mb-6">
        <div className="px-8 py-6 border-b border-white/8 bg-gradient-to-r from-[#141416] to-[#1a1a1d]">
          <h2 className="text-2xl font-bold text-[#d4a852] flex items-center gap-3">
            <span className="w-1.5 h-8 bg-gradient-to-b from-[#d4a852] to-[#b08d3e] rounded-full"></span>
            版本历史
          </h2>
        </div>
        <div className="p-8">
          <Table
            columns={historyColumns}
            dataSource={versionHistory}
            rowKey="version"
            size="small"
            pagination={{ pageSize: 10 }}
            className="version-history-table"
          />
        </div>
      </div>

      {/* 警告信息 */}
      {versionInfo?.is_updated && (
        <Alert
          message={<span className="text-[#f0f0f2] font-semibold">检测到版本更新</span>}
          description={<span className="text-[#a0a0a8]">当前版本与存储版本不一致，建议执行数据库迁移以确保功能正常运行。</span>}
          type="warning"
          showIcon
          className="bg-[#1a1a1d] border-[#faad14]/30"
          action={
            <Button
              size="small"
              onClick={() => setMigrationModalVisible(true)}
              className="bg-[#d4a852] border-0 text-[#0d0d0f] hover:bg-[#e8c780]"
            >
              立即迁移
            </Button>
          }
        />
      )}

      {/* 迁移执行对话框 */}
      <Modal
        title={<span className="text-[#d4a852]">执行数据库迁移</span>}
        open={migrationModalVisible}
        onCancel={() => setMigrationModalVisible(false)}
        footer={null}
        width={600}
        className="dark-modal"
      >
        <div className="bg-[#1a1a1d] p-6 rounded-lg">
          <Alert
            message="重要提示"
            description="数据库迁移是一个重要操作，建议在执行前备份数据库。"
            type="info"
            showIcon
            className="mb-6 bg-[#141416] border-[#d4a852]/20"
          />

          <div className="text-[#e8c780] font-semibold mb-4">迁移选项</div>

          <div className="space-y-4">
            <div className="bg-[#141416] rounded-lg p-4 border border-white/8">
              <Button
                type="primary"
                size="large"
                block
                loading={migrationLoading}
                onClick={() => handleMigration(true, false)}
                className="bg-gradient-to-r from-[#d4a852] to-[#b08d3e] border-0 text-[#0d0d0f] font-semibold hover:from-[#e8c780] hover:to-[#d4a852]"
              >
                标准迁移（推荐）
              </Button>
              <div className="text-[#6a6a72] text-sm mt-2">自动备份 + 条件检查 + 安全迁移</div>
            </div>

            <div className="bg-[#141416] rounded-lg p-4 border border-white/8">
              <Button
                size="large"
                block
                loading={migrationLoading}
                onClick={() => handleMigration(false, false)}
                className="bg-[#222226] border-white/8 text-[#d4a852] hover:border-[#d4a852] hover:text-[#e8c780]"
              >
                快速迁移
              </Button>
              <div className="text-[#6a6a72] text-sm mt-2">跳过备份 + 条件检查 + 快速迁移</div>
            </div>

            <div className="bg-[#141416] rounded-lg p-4 border border-white/8">
              <Button
                danger
                size="large"
                block
                loading={migrationLoading}
                onClick={() => handleMigration(true, true)}
                className="bg-red-500/10 border-red-500/30 text-red-400 hover:bg-red-500/20 hover:border-red-500/50"
              >
                强制迁移
              </Button>
              <div className="text-[#6a6a72] text-sm mt-2">忽略所有检查 + 强制执行（谨慎使用）</div>
            </div>
          </div>
        </div>
      </Modal>
    </div>
  )
}

export default VersionManagement
