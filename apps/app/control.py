from utils.db import mark
from utils.db.db import DB
from apps.app.model import *
from sqlalchemy import text
from utils.jwt import authorize
from utils.extension import Cache,LRUKCache
from utils.response import Response,Meta,StatusCode
from copy import copy

async def login(req: Login, db: DB[mark.User], cache:Cache) -> Response:
    async with db.async_sessoion() as session:
        result = await session.execute(
            text(
                '''
                select json_build_object(
                    'user_id',user_id, 
                    'username', username, 
                    'password', password, 
                    'realname', realname, 
                    'user_desc',user_desc, 
                    'avatar', avatar, 
                    'roles', roles, 
                    'sex',sex)
                from users_table 
                where username=:username and password=:password
                '''
            ), req.dict()
        )
        try:
            result = result.fetchone()
            user_info = result[0]
            # print(user_info)
            # u = User.from_dict(data=user_info)
            # print(u)
            encode_jwt, encode_refresh_jwt,exp = authorize(user_info)
            cache.set(encode_refresh_jwt, user_info, exp.timestamp() + 24 * 3600)
            body = LoginRes(info=User.from_dict(data=copy(user_info)), token=encode_jwt, refresh_token=encode_refresh_jwt)
            # print(cache.get(encode_refresh_jwt))
            return Response(meta=Meta.default(), body=body)

        except Exception as e:
            print(e)
            return Response(meta=Meta.build_from(
                err_code=StatusCode.BadRequest,
                err_message="用户账号或密码错误!"
            ))
    # Token.create_access_token()

async def refresh_token(req: RefreshToken, cache:Cache) -> Response:
    user_info = cache.pop(req.refresh_token)
    if user_info:
        # print(user_info)
        encode_jwt, encode_refresh_jwt, exp = authorize(user_info)
        cache.set(encode_refresh_jwt, user_info)
        body = LoginRes(info=User.from_dict(data=user_info), token=encode_jwt, refresh_token=encode_refresh_jwt)
        return Response(meta=Meta.default(), body=body)
    else:
        return Response(meta=Meta.build_from(
            err_code=StatusCode.BadRequest,
            err_message="refresh token 不存在或已过期!"
        ))

async def put_lru2_cache(req: PutLruKCacheReq, cache: LRUKCache) -> Response:
    cache.put(**req.dict())
    return Response(meta=Meta.default(), body=None)

async def get_lru2_cache(req: GetLruKCacheReq, cache: LRUKCache) -> Response:
    result = cache.get(**req.dict())
    res = GetLruCacheRes(key=req.key, value=result)
    return Response(meta=Meta.default(), body=res)