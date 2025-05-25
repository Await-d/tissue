from fastapi import FastAPI

from app import middleware, db, exception
from app.scheduler import scheduler
from app.api import api_router, actor_subscribe

app = FastAPI()

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
