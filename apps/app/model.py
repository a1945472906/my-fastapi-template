from __future__ import annotations
from utils import jwt
from typing import List, Optional
from pydantic import BaseModel
from utils.extension import CacheValue
class Role(BaseModel, jwt.TokenInfo):
    role_name: str
    value: str

class User(BaseModel, jwt.TokenInfo):
    user_id: int
    username: str
    realname: str
    user_desc: Optional[str]
    avatar: Optional[str]
    roles: List[Role]
    sex: Optional[bool]
    def into_dict(self) -> dict:
        data = self.__dict__
        data["roles"] = [d.into_dict() for d in self.roles]
        return data
    @classmethod
    def from_dict(cls,data: dict) -> User:
        data["roles"] = [Role(**d) for d in data["roles"]]
        u = User(**data)
        return u

class Login(BaseModel):
    username: str
    password: str

class LoginRes(BaseModel):
    info: User
    token: str
    refresh_token: str

class RefreshToken(BaseModel):
    refresh_token: str

class PutLruKCacheReq(BaseModel):
    key: str
    value: str

class GetLruKCacheReq(BaseModel):
    key: str


class GetLruCacheRes(BaseModel):
    key: str
    value: Optional[str]