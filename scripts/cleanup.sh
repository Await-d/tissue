#!/bin/bash
# 文件清理脚本
# 用于在测试完成后清理临时文件

echo "================================"
echo "文件清理脚本"
echo "================================"
echo ""

# 列出将要删除的文件
echo "以下文件将被删除:"
echo "  - scripts/test_fixes.py (功能测试脚本)"
echo "  - docs/DEPLOYMENT_GUIDE.md (详细部署文档)"
echo "  - QUICK_START.md (快速开始指南)"
echo ""

# 询问确认
read -p "确定要删除这些文件吗? (y/N): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "取消删除"
    exit 0
fi

# 删除文件
echo ""
echo "开始删除文件..."

if [ -f "scripts/test_fixes.py" ]; then
    rm scripts/test_fixes.py
    echo "✓ 已删除 scripts/test_fixes.py"
fi

if [ -f "docs/DEPLOYMENT_GUIDE.md" ]; then
    rm docs/DEPLOYMENT_GUIDE.md
    echo "✓ 已删除 docs/DEPLOYMENT_GUIDE.md"
fi

if [ -f "QUICK_START.md" ]; then
    rm QUICK_START.md
    echo "✓ 已删除 QUICK_START.md"
fi

echo ""
echo "================================"
echo "清理完成！"
echo "================================"
echo ""
echo "保留的文件（核心修复）:"
echo "  ✓ app/service/base_download.py"
echo "  ✓ app/service/subscribe.py (已修改)"
echo "  ✓ app/service/actor_subscribe.py (已修改)"
echo "  ✓ app/utils/data_converter.py"
echo "  ✓ app/utils/qbittorent.py (已修改)"
echo "  ✓ scripts/migrate_actor_subscribe_cache.py (数据库迁移)"
echo ""
