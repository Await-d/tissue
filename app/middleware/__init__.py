import types
import time
import sys

from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from . import requestvars
from app.utils.logger import logger

print("[MIDDLEWARE] 模块加载", flush=True)


def init(app: FastAPI):
    print("[MIDDLEWARE] init() 被调用", flush=True)
    
    @app.middleware('http')
    async def request_logging_middleware(request: Request, call_next):
        """请求日志中间件"""
        # 调试：确认中间件被调用
        print(f"[MIDDLEWARE] 收到请求: {request.method} {request.url.path}", file=sys.stderr, flush=True)
        
        start_time = time.time()
        
        # 初始化请求上下文
        initial_g = types.SimpleNamespace()
        initial_g.current_user_id = None
        initial_g.transaction_started = False
        requestvars.request_global.set(initial_g)
        
        try:
            response = await call_next(request)
            
            # 计算请求耗时
            process_time = (time.time() - start_time) * 1000
            
            # 记录请求日志（排除静态资源和健康检查）
            path = request.url.path
            if not path.startswith(('/static', '/favicon', '/health')):
                # 同时用 print 和 logger 输出，确保能看到
                log_msg = f"{request.method} {path} - {response.status_code} - {process_time:.2f}ms"
                print(f"[REQUEST] {log_msg}", flush=True)
                logger.info(log_msg)
            
            return response
        except Exception as e:
            # 记录错误请求
            process_time = (time.time() - start_time) * 1000
            log_msg = f"{request.method} {request.url.path} - ERROR - {process_time:.2f}ms - {str(e)}"
            print(f"[REQUEST ERROR] {log_msg}", flush=True)
            logger.error(log_msg)
            raise

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
