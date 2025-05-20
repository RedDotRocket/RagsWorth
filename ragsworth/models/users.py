from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    full_name: str | None = None
    disabled: bool | None = None
    password: str | None = Field(default=None, exclude=True)
    hashed_password: str | None = Field(default=None, exclude=True)
    # Add additional fields as needed




