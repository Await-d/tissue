#!/bin/bash

# Tissue项目启动脚本
# 自动检测环境并启动应用

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否在项目根目录
check_project_root() {
    if [ ! -f "alembic.ini" ] || [ ! -f "startup_check.py" ]; then
        log_error "请在项目根目录运行此脚本"
        exit 1
    fi
}

# 检查Python环境
check_python_env() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未找到，请安装Python3"
        exit 1
    fi
    
    if [ ! -d "venv" ]; then
        log_info "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    log_info "激活虚拟环境并安装依赖..."
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
}

# 运行启动检查
run_startup_check() {
    log_info "运行启动检查和修复..."
    
    if python startup_check.py; then
        log_success "启动检查完成，所有检查通过"
        return 0
    else
        log_warning "启动检查发现问题，已尝试自动修复"
        log_info "详细报告请查看 startup_check_report.txt"
        return 1
    fi
}

# 启动前端开发服务器
start_frontend_dev() {
    log_info "启动前端开发服务器..."
    cd frontend
    if [ ! -d "node_modules" ]; then
        log_info "安装前端依赖..."
        npm install
    fi
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    log_success "前端开发服务器已启动 (PID: $FRONTEND_PID)"
}

# 启动后端服务器
start_backend_dev() {
    log_info "启动后端开发服务器..."
    source venv/bin/activate
    uvicorn app.main:app --reload --host 0.0.0.0 --port 9193 &
    BACKEND_PID=$!
    log_success "后端开发服务器已启动 (PID: $BACKEND_PID)"
}

# 生产环境启动
start_production() {
    log_info "启动生产环境..."
    source venv/bin/activate
    
    # 构建前端
    log_info "构建前端资源..."
    cd frontend
    npm run build
    cd ..
    
    # 启动应用
    uvicorn app.main:app --host 0.0.0.0 --port 9193
}

# 停止服务
stop_services() {
    log_info "停止所有服务..."
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        log_info "前端服务器已停止"
    fi
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        log_info "后端服务器已停止"
    fi
}

# 信号处理
trap stop_services EXIT

# 显示帮助信息
show_help() {
    echo "Tissue项目启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  dev       开发模式 (启动前端和后端开发服务器)"
    echo "  prod      生产模式 (构建前端并启动生产服务器)"
    echo "  check     仅运行启动检查"
    echo "  help      显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 dev    # 启动开发环境"
    echo "  $0 prod   # 启动生产环境"
    echo "  $0 check  # 仅运行检查"
}

# 主函数
main() {
    log_info "🚀 Tissue项目启动脚本"
    
    # 检查项目根目录
    check_project_root
    
    # 解析命令行参数
    case "${1:-dev}" in
        "dev")
            log_info "启动开发环境..."
            check_python_env
            run_startup_check
            start_frontend_dev
            start_backend_dev
            log_success "开发环境启动完成！"
            log_info "前端地址: http://localhost:3000"
            log_info "后端地址: http://localhost:9193"
            log_info "按 Ctrl+C 停止服务"
            # 等待用户中断
            wait
            ;;
        "prod")
            log_info "启动生产环境..."
            check_python_env
            run_startup_check
            start_production
            ;;
        "check")
            log_info "运行启动检查..."
            check_python_env
            run_startup_check
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"