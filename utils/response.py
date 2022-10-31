from pydantic import BaseModel
from enum import Enum
from typing import TypeVar, Generic, Union

T = TypeVar("T", bound=BaseModel)


class StatusCode(Enum):
    Ok = 200
    BadRequest = 400
    UnAuthorized = 401
    NotFound = 404
    Forbiden = 403
    MethodNotAllowed = 405
    InternalServerError = 500


class Meta(BaseModel):
    err_code: StatusCode
    err_message: str
    @classmethod
    def default(cls):
        m = Meta(err_code=StatusCode.Ok, err_message='')
        return m
    @classmethod
    def build_from(cls,err_code, err_message):
        m = Meta(err_code=err_code, err_message=err_message)
        return m


class Response(BaseModel,Generic[T]):
    meta: Meta
    body: Union[T,None]
