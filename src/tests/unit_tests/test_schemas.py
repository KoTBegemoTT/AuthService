import pytest
from pydantic_core import ValidationError

from src.app.auth_service.schemas import TokenSchema, UserSchema


@pytest.mark.parametrize(
    'pyload',
    [
        pytest.param(
            {'name': 'user_1', 'password': 'password'}, id='user_1'),
        pytest.param({'name': 'admin', 'password': 'admin'},
                     id='username_equals_password'),
        pytest.param({'name': '', 'password': ''},
                     id='empty_username_and_password'),
        pytest.param(
            {'name': '', 'password': 'password', 'extra': 'payload'},
            id='extra_payload',
        ),
    ],
)
def test_user_schema(pyload):
    user = UserSchema(**pyload)
    assert user.name == pyload.get('name')
    assert user.password == pyload.get('password')


@pytest.mark.parametrize(
    'pyload, bad_field, error_msg',
    [
        pytest.param({'password': 'password'}, 'name',
                     'Field required', id='no_name'),
        pytest.param({'name': 'user'}, 'password',
                     'Field required', id='no_password'),
        pytest.param({'name': None, 'password': 'password'},
                     'name', 'Input should be a valid string', id='name_none'),
        pytest.param({'name': 'user', 'password': None}, 'password',
                     'Input should be a valid string', id='password_none'),
    ],
)
def test_user_schema_fail(pyload, bad_field, error_msg):
    with pytest.raises(ValidationError) as ex:
        UserSchema(**pyload)

    assert ex.value.error_count() == 1
    ex_info = ex.value.errors()[0]
    assert ex_info['loc'] == (bad_field,)
    assert ex_info['msg'] == error_msg


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
def test_token_schema(pyload):
    token = TokenSchema(**pyload)
    assert token.token == pyload.get('token')


@pytest.mark.parametrize(
    'pyload, bad_field, error_msg',
    [
        pytest.param({}, 'token', 'Field required', id='no_token'),
        pytest.param({'token': True}, 'token',
                     'Input should be a valid string', id='token_wrong_type'),
    ],
)
def test_token_schema_fail(pyload, bad_field, error_msg):
    with pytest.raises(ValidationError) as ex:
        TokenSchema(**pyload)

    assert ex.value.error_count() == 1
    ex_info = ex.value.errors()[0]
    assert ex_info['loc'] == (bad_field,)
    assert ex_info['msg'] == error_msg
