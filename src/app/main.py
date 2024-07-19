from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.auth_service.urls import router as users_router


app = FastAPI()
app.include_router(users_router, prefix="/users")


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("main:app")
