from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, status
from prometheus_client import make_asgi_app
from starlette.middleware.base import BaseHTTPMiddleware

from app.auth_service.urls import router as users_router
from app.external.kafka import producer
from app.middleware import metrics_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Настройка при запуске и остановке приложения."""
    await producer.start()
    yield
    await producer.stop()


app = FastAPI(lifespan=lifespan)
app.include_router(users_router)

metrics_app = make_asgi_app()
app.mount('/metrics/', metrics_app)

app.add_middleware(BaseHTTPMiddleware, dispatch=metrics_middleware)


@app.get('/')
async def root():
    """Стартовая страница."""
    return {'message': 'Hello World'}


@app.get('/ready', status_code=status.HTTP_200_OK)
async def ready_check():
    """Проверка состояния сервиса."""
    return {'message': 'Service is ready'}


@app.get('/live', status_code=status.HTTP_200_OK)
async def live_check():
    """Проверка состояния сервиса."""
    return {'message': 'Service is live'}


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        reload=True,
        host='0.0.0.0',  # noqa: S104
        port=8001,  # noqa: WPS432
    )
