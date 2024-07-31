import pytest

from app.auth_service.views import user_tokens, users


@pytest.fixture(autouse=True)
def setup():
    users.clear()
    user_tokens.clear()
