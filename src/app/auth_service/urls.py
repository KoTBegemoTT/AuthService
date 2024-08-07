from fastapi import APIRouter, Depends, status

from app.auth_service.schemas import UserSchema
from app.auth_service.views import (
    auth_view,
    register_view,
    validate_auth_user,
    validate_token,
)
from app.models import User

router = APIRouter(tags=['users'])


@router.get(
    '/healthz/ready/',
    status_code=status.HTTP_200_OK,
)
async def ready_check() -> None:
    """Проверка состояния сервиса."""
    return None


@router.post(
    '/register/',
    status_code=status.HTTP_201_CREATED,
)
async def register(user_in: UserSchema) -> str:
    """Регистрация пользователя."""
    return await register_view(user_in)


@router.post(
    '/auth/',
    status_code=status.HTTP_201_CREATED,
)
async def auth(
    user_in: User = Depends(validate_auth_user),
) -> str:
    """Авторизация пользователя."""
    return await auth_view(user_in)


@router.get(
    '/check_token/',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(validate_token)],
)
async def check_token(user_id: int) -> None:
    """Проверка токена."""
    return None
