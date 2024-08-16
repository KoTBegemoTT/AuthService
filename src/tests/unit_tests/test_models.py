import pytest

from app.db.models import User
import sqlalchemy


@pytest.mark.parametrize(
    'pyload',
    [
        pytest.param(
            {'name': 'user_1', 'password': b'password'}, id='user_1'),
        pytest.param({'name': 'admin', 'password': b'admin'},
                     id='username_equals_password'),
        pytest.param({'name': '', 'password': b''},
                     id='empty_username_and_password'),
    ],
)
@pytest.mark.usefixtures('reset_db')
@pytest.mark.asyncio
async def test_user_model(pyload, db_helper):
    user = User(**pyload)
    assert user.name == pyload.get('name')
    assert user.password == pyload.get('password')

    async with db_helper.session_factory() as session:
        session.add(user)
        await session.commit()


@pytest.mark.parametrize(
    'pyload, error_msg',
    [
        pytest.param(
            {'password': b'password'},
            'значение NULL в столбце "name" отношения "users" нарушает ограничение NOT NULL',
            id='no_name'),
        pytest.param(
            {'name': 'user'},
            'значение NULL в столбце "password" отношения "users" нарушает ограничение NOT NULL',  # noqa: E501
            id='no_password'),
    ],
)
@pytest.mark.usefixtures('reset_db')
@pytest.mark.asyncio
async def test_user_model_fail(pyload, error_msg, db_helper):
    async with db_helper.session_factory() as session:
        with pytest.raises(sqlalchemy.exc.IntegrityError) as ex:
            user = User(**pyload)
            session.add(user)
            await session.commit()

    assert error_msg in str(ex.value)
