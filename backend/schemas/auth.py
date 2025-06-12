from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: int
    email: str
    nickname: str | None = None
    is_admin: bool

    class Config:
        from_attributes = True
