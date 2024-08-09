from contextlib import asynccontextmanager
import logging
from aiokafka import AIOKafkaProducer
import uvicorn
from fastapi import APIRouter, FastAPI, UploadFile
import brotli
from app.auth_service.urls import router as users_router
from app.external.kafka import producer


@asynccontextmanager
async def lifespan(app: FastAPI):
    await producer.start()
    yield
    await producer.stop()


app = FastAPI(lifespan=lifespan)
app.include_router(users_router)


@app.get('/')
async def root():
    """Стартовая страница."""
    return {'message': 'Hello World'}


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        reload=True,
        host='0.0.0.0',  # noqa: S104
        port=8001,  # noqa: WPS432
    )
