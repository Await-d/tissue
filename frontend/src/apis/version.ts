import { request } from '@/utils/requests'

// 类型定义
export interface VersionInfo {
  current_version: string
  stored_version?: string
  last_updated?: string
  migration_success: boolean
  notes: string
  is_updated: boolean
}

export interface VersionHistory {
  version: string
  updated_at: string
  migration_success: boolean
}

export interface MigrationRequirements {
  alembic_available: boolean
  config_exists: boolean
  database_accessible: boolean
  disk_space_sufficient: boolean
  errors: string[]
}

export interface VersionStatus {
  health_status: 'excellent' | 'good' | 'warning' | 'critical'
  health_score: number
  health_message: string
  health_checks: Record<string, boolean>
  version_info: VersionInfo
  requirements: MigrationRequirements
  recommendations: string[]
}

export interface ApiResponse<T = any> {
  success: boolean
  message: string
  data?: T
}

// 版本信息API
export const getVersionInfo = (): Promise<VersionInfo> => {
  return request.get('/api/version/info')
}

export const getVersionHistory = (): Promise<ApiResponse<{
  current_version: string
  history: VersionHistory[]
  total_count: number
}>> => {
  return request.get('/api/version/history')
}

export const checkVersionUpdate = (): Promise<ApiResponse<{
  is_updated: boolean
  current_version: string
  stored_version?: string
  needs_migration: boolean
}>> => {
  return request.get('/api/version/check')
}

// 迁移管理API
export const triggerMigration = (data: {
  force_backup?: boolean
  force_migration?: boolean
}): Promise<ApiResponse> => {
  return request.post('/api/version/migrate', data)
}

export const checkMigrationRequirements = (): Promise<ApiResponse<{
  all_satisfied: boolean
  details: MigrationRequirements
  recommendation: string
}>> => {
  return request.get('/api/version/requirements')
}

export const forceSaveVersion = (): Promise<ApiResponse<{
  version: string
  saved_at: string
}>> => {
  return request.post('/api/version/force-save')
}

export const getVersionStatus = (): Promise<ApiResponse<VersionStatus>> => {
  return request.get('/api/version/status')
}