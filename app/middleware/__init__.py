import types

from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from . import requestvars


def init(app: FastAPI):
    @app.middleware('http')
    async def init_request_vars(request: Request, call_next):
        initial_g = types.SimpleNamespace()
        # 初始化一些默认属性，避免AttributeError
        initial_g.current_user_id = None
        initial_g.transaction_started = False
        requestvars.request_global.set(initial_g)
        
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # 确保异常处理期间上下文依然可用
            raise

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
