from fastapi import APIRouter, Depends

from app.schemas import TokenSchema, CreateUserSchema, LoginUserSchema
from app.auth_service.views import register_view, login_view

router = APIRouter(tags=["users"])


@router.post("/register", response_model=TokenSchema, status_code=201)
def register(user_in: CreateUserSchema):
    token = register_view(user_in)
    return TokenSchema(token=token)


@router.post("/auth", status_code=201)
def login(user_in: LoginUserSchema):
    token = login_view(user_in)
    return TokenSchema(token=token)
