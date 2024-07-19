import pytest
from pydantic_core import ValidationError

from app.schemas import (
    UserSchemaBase,
    CreateUserSchema,
    LoginUserSchema,
    UserSchema,
    TokenSchema,
)

payload_params = [
    pytest.param({'name': "user_1", 'password': "password"}, id="user_1"),
    pytest.param({'name': "admin", 'password': "admin"},
                 id="username_equals_password"),
    pytest.param({'name': "", 'password': ""},
                 id="empty_username_and_password"),
    pytest.param({'name': "", 'password': "password",
                 "extra": "payload"}, id="extra_payload"),
]

payload_params_fail = [
    pytest.param({'password': "password"}, id="no_name"),
    pytest.param({'name': "user"}, id="no_password"),
    pytest.param({'name': None, 'password': "password"}, id="name_none"),
    pytest.param({'name': "user", 'password': None,
                 "extra": "payload"}, id="password_none"),
]

schemas_params = [
    pytest.param(UserSchemaBase, id="user_schema_base"),
    pytest.param(CreateUserSchema, id="create_user_schema"),
    pytest.param(LoginUserSchema, id="login_user_schema"),
]


@pytest.mark.parametrize("data", payload_params)
@pytest.mark.parametrize("schema", schemas_params)
def test_user_schema_base(data, schema):
    user = schema(**data)
    assert user.name == data.get('name')
    assert user.password == data.get('password')


@pytest.mark.parametrize("data", payload_params_fail)
@pytest.mark.parametrize("schema", schemas_params)
def test_create_user_schema_base_fail(data, schema):
    with pytest.raises(ValidationError):
        schema(**data)


