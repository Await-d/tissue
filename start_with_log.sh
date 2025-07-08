#!/bin/bash

# 设置环境变量
export PYTHONUNBUFFERED=1
export PYTHONFAULTHANDLER=1

# 激活虚拟环境
source venv/bin/activate

# 创建日志目录
mkdir -p logs

# 获取当前时间戳
timestamp=$(date +"%Y%m%d_%H%M%S")
log_file="logs/app_${timestamp}.log"

echo "启动应用，日志将保存到 ${log_file}"
echo "启动时间: $(date)" > "${log_file}"
echo "Python 版本: $(python --version)" >> "${log_file}"
echo "虚拟环境: $VIRTUAL_ENV" >> "${log_file}"
echo "-----------------------------------" >> "${log_file}"

# 启动应用并将所有输出重定向到日志文件
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 9193 >> "${log_file}" 2>&1 