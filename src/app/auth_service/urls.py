from fastapi import APIRouter, status

from app.auth_service.schemas import TokenSchema, UserSchema
from app.auth_service.views import login_view, register_view

router = APIRouter(tags=['users'])


@router.post(
    '/register/',
    response_model=TokenSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register(user_in: UserSchema) -> TokenSchema:
    """Регистрация пользователя."""
    token = await register_view(user_in)
    return TokenSchema(token=token)


@router.post(
    '/auth/',
    response_model=TokenSchema,
    status_code=status.HTTP_201_CREATED,
)
async def login(user_in: UserSchema) -> TokenSchema:
    """Авторизация пользователя."""
    token = await login_view(user_in)
    return TokenSchema(token=token)
