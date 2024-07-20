from fastapi import APIRouter, status

from app.auth_service.views import login_view, register_view
from app.schemas import TokenSchema, UserSchema

router = APIRouter(tags=['users'])


@router.post(
    '/register',
    response_model=TokenSchema,
    status_code=status.HTTP_201_CREATED,
)
def register(user_in: UserSchema) -> TokenSchema:
    """Регистрация пользователя."""
    token = register_view(user_in)
    return TokenSchema(token=token)


@router.post(
    '/auth',
    response_model=TokenSchema,
    status_code=status.HTTP_201_CREATED,
)
def login(user_in: UserSchema) -> TokenSchema:
    """Авторизация пользователя."""
    token = login_view(user_in)
    return TokenSchema(token=token)
