import pytest
from pydantic_core import ValidationError

from app.schemas import TokenSchema, UserSchema

payload_params = [
    pytest.param({'name': 'user_1', 'password': 'password'}, id='user_1'),
    pytest.param({'name': 'admin', 'password': 'admin'},
                 id='username_equals_password'),
    pytest.param({'name': '', 'password': ''},
                 id='empty_username_and_password'),
    pytest.param(
        {'name': '', 'password': 'password', 'extra': 'payload'},
        id='extra_payload',
    ),
]

payload_params_fail = [
    pytest.param({'password': 'password'}, id='no_name'),
    pytest.param({'name': 'user'}, id='no_password'),
    pytest.param({'name': None, 'password': 'password'}, id='name_none'),
    pytest.param(
        {'name': 'user', 'password': None, 'extra': 'payload'},
        id='password_none',
    ),
]


@pytest.mark.parametrize('pyload', payload_params)
def test_user_schema_base(pyload):
    user = UserSchema(**pyload)
    assert user.name == pyload.get('name')
    assert user.password == pyload.get('password')


@pytest.mark.parametrize('pyload', payload_params_fail)
def test_create_user_schema_base_fail(pyload):
    with pytest.raises(ValidationError):
        UserSchema(**pyload)


@pytest.mark.parametrize(
    'pyload',
    [
        pytest.param(
            {'name': 'user_1', 'password': 'password', 'token': 'token'},
            id='user_1',
        ),
        pytest.param(
            {'token': 'token'},
            id='only_token',
        ),
        pytest.param(
            {'token': ''},
            id='empty_token',
        ),
    ],
)
def test_token_schema_base(pyload):
    token = TokenSchema(**pyload)
    assert token.token == pyload.get('token')
