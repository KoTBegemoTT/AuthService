from pydantic import BaseModel, ConfigDict


class UserSchemaBase(BaseModel):
    name: str
    password: str


class CreateUserSchema(UserSchemaBase):
    pass


class LoginUserSchema(UserSchemaBase):
    pass


class UserSchema(UserSchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class TokenSchema(BaseModel):
    token: str | None
