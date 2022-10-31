from __future__ import annotations
from jose import JWTError, jwt
from utils.extension import get_env
from typing import Generic, TypeVar, Type, ClassVar
from datetime import datetime, timedelta
from fastapi import HTTPException, status

KEY = get_env().value.get("JWT_SECRET")
KEY_FRESH = get_env().value.get("JWT_FRESH_SECRET")

REFRESH_EXP = timedelta(minutes=24*60)
credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
)

def watch_env(_:dict, new_value:dict):
    global KEY
    global KEY_FRESH
    KEY = new_value.get("JWT_SECRET")
    KEY_FRESH = new_value.get("JWT_FRESH_SECRET")

get_env().watch(watch_env)

class TokenInfo:
    def into_dict(self) -> dict:
        pass
    @classmethod
    def from_dict(cls,data: dict) -> TokenInfo:
        pass

T = TypeVar("T", bound=TokenInfo)

class Token(Generic[T]):
    def __init__(self, obj: T, expires_delta: timedelta=timedelta(minutes=24*60)):
        self.token_info = obj
        self.exp = datetime.utcnow() + expires_delta
    @classmethod
    def decode_token_into(cls, target: T, token: str) -> T:
        try:
            data = jwt.decode(token,KEY, algorithms=["HS256"])
        except JWTError:
            raise
        # return ClassVar[T].from_dict(data.get("token_info"))
        return target.from_dict(data.get("token_info"))

def authorize(data: dict, expires_delta: timedelta=timedelta(minutes=24*60)):
    exp = datetime.utcnow() + expires_delta
    to_encode = {
        "token_info": data,
        "exp": exp
    }
    encode_jwt = jwt.encode(to_encode, KEY, algorithm="HS256")
    encode_refresh_jwt = jwt.encode(to_encode, KEY_FRESH, algorithm="HS256")
    return encode_jwt, encode_refresh_jwt, exp
