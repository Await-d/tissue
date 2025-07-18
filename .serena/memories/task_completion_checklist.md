# 任务完成检查清单

## 代码质量检查
- [ ] **前端代码检查**: 运行 `npm run lint` 确保无 ESLint 错误
- [ ] **TypeScript 类型检查**: 运行 `npm run build` 确保无类型错误
- [ ] **Python 代码检查**: 确保符合 PEP 8 规范
- [ ] **导入检查**: 确保所有导入都是必要的且正确的

## 功能测试
- [ ] **API 接口测试**: 测试修改的 API 端点是否正常工作
- [ ] **前端功能测试**: 在浏览器中测试修改的功能
- [ ] **数据库操作测试**: 如果涉及数据库，测试 CRUD 操作
- [ ] **定时任务测试**: 如果涉及调度器，测试任务是否正常执行

## 构建和部署检查
- [ ] **前端构建**: 确保 `npm run build` 成功
- [ ] **Docker 构建**: 确保 `docker build` 成功
- [ ] **容器运行**: 确保容器可以正常启动和运行
- [ ] **端口访问**: 确保可以通过 9193 端口访问应用

## 数据库检查
- [ ] **迁移文件**: 如果有数据库变更，确保生成了正确的迁移文件
- [ ] **迁移执行**: 确保 `alembic upgrade head` 成功
- [ ] **数据完整性**: 确保数据库操作不会破坏现有数据

## 安全检查
- [ ] **认证检查**: 确保需要认证的接口有正确的权限控制
- [ ] **输入验证**: 确保用户输入得到适当的验证
- [ ] **SQL 注入防护**: 确保使用了参数化查询
- [ ] **XSS 防护**: 确保前端正确处理用户输入

## 性能检查
- [ ] **查询优化**: 确保数据库查询是高效的
- [ ] **内存使用**: 确保没有内存泄漏
- [ ] **响应时间**: 确保 API 响应时间在可接受范围内

## 文档和注释
- [ ] **代码注释**: 确保复杂逻辑有适当的注释
- [ ] **API 文档**: 如果添加了新的 API，确保文档已更新
- [ ] **变更日志**: 考虑是否需要更新 CHANGELOG.md

## 兼容性检查
- [ ] **浏览器兼容**: 确保前端在主流浏览器中正常工作
- [ ] **Python 版本**: 确保代码与 Python 3.11.8 兼容
- [ ] **依赖版本**: 确保新的依赖与现有版本兼容

## 提交前检查
- [ ] **Git 状态**: 确保只提交需要的文件
- [ ] **提交信息**: 使用清晰的提交信息
- [ ] **分支管理**: 确保在正确的分支上工作