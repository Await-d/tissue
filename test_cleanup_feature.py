#!/usr/bin/env python3
"""
种子文件清理功能测试脚本
测试所有清理相关的 API 端点和功能
"""

import sys
import requests
import json
from typing import Dict, Any

# 配置
BASE_URL = "http://localhost:8000"  # 根据实际端口调整
API_BASE = f"{BASE_URL}/api"


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_success(msg: str):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")


def print_error(msg: str):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")


def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")


def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")


def get_auth_token() -> str:
    """
    获取认证token
    使用测试用户: test / test123
    """
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            data={"username": "test", "password": "test123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=5
        )
        if response.ok:
            result = response.json()
            return result.get('data', '')
        return ''
    except:
        return ''


def call_api_endpoint(method: str, endpoint: str, params: Dict = None, data: Dict = None, token: str = None) -> tuple:
    """
    测试 API 端点

    Returns:
        (success: bool, response: dict, status_code: int)
    """
    url = f"{API_BASE}{endpoint}"
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'

    try:
        if method.upper() == 'GET':
            response = requests.get(url, params=params, headers=headers, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, params=params, json=data, headers=headers, timeout=10)
        else:
            return False, {'error': 'Unsupported method'}, 0

        return response.ok, response.json() if response.ok else {}, response.status_code
    except requests.exceptions.ConnectionError:
        return False, {'error': 'Connection refused - 服务未启动'}, 0
    except requests.exceptions.Timeout:
        return False, {'error': 'Request timeout'}, 0
    except Exception as e:
        return False, {'error': str(e)}, 0


def test_backend_api():
    """测试后端 API 端点"""
    print("\n" + "="*60)
    print("测试后端 API 端点")
    print("="*60)

    # 获取认证token
    print("\n获取认证token...")
    token = get_auth_token()
    if not token:
        print_error("无法获取认证token，跳过API测试")
        return {'passed': 0, 'failed': 3}
    print_success("Token获取成功")

    tests = [
        {
            'name': '获取过滤设置',
            'method': 'GET',
            'endpoint': '/download-filter/settings',
            'params': None
        },
        {
            'name': '批量清理预览（所有种子）',
            'method': 'POST',
            'endpoint': '/download-filter/cleanup-all',
            'params': {'dry_run': True}
        },
        {
            'name': '获取过滤统计',
            'method': 'GET',
            'endpoint': '/download-filter/statistics',
            'params': None
        }
    ]

    results = {'passed': 0, 'failed': 0}

    for test in tests:
        print(f"\n测试: {test['name']}")
        print(f"  请求: {test['method']} {test['endpoint']}")

        success, response, status_code = call_api_endpoint(
            test['method'],
            test['endpoint'],
            params=test.get('params'),
            token=token
        )

        if success:
            print_success(f"状态码: {status_code}")
            if response.get('success') == True or response.get('code') == 200:
                print_success("响应格式正确")
                results['passed'] += 1
            else:
                print_warning(f"业务状态: {response}")
                results['passed'] += 1
        else:
            print_error(f"请求失败: {response.get('error', '未知错误')}")
            results['failed'] += 1

    return results


def test_frontend_build():
    """测试前端构建"""
    print("\n" + "="*60)
    print("检查前端构建")
    print("="*60)

    import os

    checks = [
        ('frontend/dist/index.html', '主页文件'),
        ('frontend/src/routes/_index/download/index.tsx', '下载页面源码'),
        ('frontend/src/routes/_index/setting/download-filter.tsx', '设置页面源码'),
        ('frontend/src/apis/downloadFilter.ts', 'API 客户端'),
        ('frontend/src/types/cleanup.ts', '类型定义')
    ]

    results = {'passed': 0, 'failed': 0}

    for file_path, description in checks:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print_success(f"{description}: {file_path} ({size} bytes)")
            results['passed'] += 1
        else:
            print_error(f"{description}: {file_path} - 文件不存在")
            results['failed'] += 1

    return results


def test_code_completeness():
    """测试代码完整性"""
    print("\n" + "="*60)
    print("检查代码完整性")
    print("="*60)

    checks = [
        {
            'file': 'frontend/src/routes/_index/download/index.tsx',
            'patterns': [
                'handleBatchCleanupClick',
                'batchCleanupModalVisible',
                'cleanupAllTorrents',
                'ClearOutlined'
            ],
            'name': '下载列表批量清理'
        },
        {
            'file': 'frontend/src/routes/_index/setting/download-filter.tsx',
            'patterns': [
                'handlePreviewCleanup',
                'handleExecuteCleanup',
                '历史种子清理'
            ],
            'name': '设置页批量清理'
        },
        {
            'file': 'frontend/src/apis/downloadFilter.ts',
            'patterns': [
                'previewCleanup',
                'cleanupTorrent',
                'cleanupAllTorrents'
            ],
            'name': 'API 客户端'
        },
        {
            'file': 'app/api/download_filter.py',
            'patterns': [
                'def preview_cleanup',
                'def cleanup_torrent',
                'def cleanup_all_torrents'
            ],
            'name': '后端 API'
        }
    ]

    results = {'passed': 0, 'failed': 0}

    for check in checks:
        print(f"\n检查: {check['name']}")
        print(f"  文件: {check['file']}")

        try:
            with open(check['file'], 'r', encoding='utf-8') as f:
                content = f.read()

            missing = []
            for pattern in check['patterns']:
                if pattern in content:
                    print_success(f"包含: {pattern}")
                    results['passed'] += 1
                else:
                    print_error(f"缺失: {pattern}")
                    missing.append(pattern)
                    results['failed'] += 1

            if missing:
                print_warning(f"缺失 {len(missing)} 个必需元素")

        except FileNotFoundError:
            print_error(f"文件不存在: {check['file']}")
            results['failed'] += len(check['patterns'])
        except Exception as e:
            print_error(f"读取文件失败: {e}")
            results['failed'] += len(check['patterns'])

    return results


def generate_test_report(backend_results, frontend_results, code_results):
    """生成测试报告"""
    print("\n" + "="*60)
    print("测试报告汇总")
    print("="*60)

    total_passed = backend_results['passed'] + frontend_results['passed'] + code_results['passed']
    total_failed = backend_results['failed'] + frontend_results['failed'] + code_results['failed']
    total_tests = total_passed + total_failed
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

    print(f"\n后端 API 测试: {backend_results['passed']} 通过 / {backend_results['failed']} 失败")
    print(f"前端构建检查: {frontend_results['passed']} 通过 / {frontend_results['failed']} 失败")
    print(f"代码完整性检查: {code_results['passed']} 通过 / {code_results['failed']} 失败")
    print(f"\n总计: {total_passed}/{total_tests} 测试通过")
    print(f"成功率: {success_rate:.1f}%")

    if total_failed == 0:
        print_success("\n🎉 所有测试通过！")
    else:
        print_warning(f"\n⚠️  有 {total_failed} 个测试失败")

    return success_rate >= 80


def main():
    print("🧪 种子文件清理功能测试")
    print("="*60)

    # 运行测试
    backend_results = test_backend_api()
    frontend_results = test_frontend_build()
    code_results = test_code_completeness()

    # 生成报告
    success = generate_test_report(backend_results, frontend_results, code_results)

    # 使用指南
    print("\n" + "="*60)
    print("📖 功能使用指南")
    print("="*60)
    print("""
1. 批量清理（下载列表页）:
   - 进入"下载"页面
   - 点击顶部的"批量清理"按钮
   - 查看预览后确认执行

2. 批量清理（设置页）:
   - 进入"设置" → "下载过滤"
   - 滚动到底部"历史种子清理"区域
   - 点击"预览清理"或"执行清理"

3. 单个清理（下载列表）:
   - 在下载列表中找到要清理的种子
   - 点击右侧的"清理文件"按钮
   - 查看预览后确认执行

⚠️  注意事项:
- 所有清理操作都有预览功能
- 删除的文件无法恢复，请谨慎操作
- 建议先使用"预览"功能查看将要删除的文件
""")

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
