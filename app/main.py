'''
Author: Await
Date: 2025-05-24 17:05:38
LastEditors: Await
LastEditTime: 2025-05-26 18:33:25
Description: 请填写简介
'''
from fastapi import FastAPI

from app import middleware, db, exception
from app.scheduler import scheduler
from app.api import api_router, actor_subscribe
from version import APP_VERSION

app = FastAPI(
    title="Tissue-Plus",
    description="A tool for scraping and managing JAV metadata. Based on chris-2s/tissue project.",
    version=APP_VERSION
)

middleware.init(app)
exception.init(app)


@app.on_event("startup")
def on_startup():
    app.include_router(api_router)
    app.include_router(
        actor_subscribe.router,
        prefix="/actor-subscribe",
        tags=["actor-subscribe"],
    )
    db.init()
    scheduler.init()


if __name__ == '__main__':
    pass
