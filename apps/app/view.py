from apps.trait import *
from fastapi import APIRouter, Response, Request, Depends
from fastapi.routing import APIRoute
from apps.app.model import *
from utils.db import mark
from utils.db.db import DB
from fastapi.security import OAuth2PasswordBearer
from utils.jwt import Token
from utils.extension import Cache,get_env,LRUKCache
import apps.app.control as control

db_url = get_env().value.get("DATABASE_URL")
app_db = DB[mark.User](db_url=db_url)
cache = Cache()

lru_cache = LRUKCache(k=2,cap=2<<10, history_cap=2<<10)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def use_lru_cache():
    return lru_cache

async def use_db():
    return app_db

async def use_cache():
    return cache


class UserView(View):
    @classmethod
    def as_route(self) -> APIRouter:
        class UserRoute(APIRoute):
            def get_route_handler(self) -> Callable:
                original_route_handler = super().get_route_handler()
                async def custom_route_handler(request: Request) -> Response:
                    return await original_route_handler(request)
                return custom_route_handler

        router = APIRouter(route_class=UserRoute)
        return router

user_view = UserView.as_route()

@user_view.post("/login")
async def login(req: Login, db: DB[mark.User] = Depends(use_db), cache: Cache = Depends(use_cache)):
    return await control.login(req,db,cache)


@user_view.get("/get_user_info")
async def get_user_info(token: str=Depends(oauth2_scheme)):
    return Token.decode_token_into(target=User,token=token)

@user_view.post("/refresh_token")
async def refresh_token(req: RefreshToken,cache: Cache=Depends(use_cache)):
    return await control.refresh_token(req,cache)

@user_view.get("/test_lru2")
async def get_lru2_cache(req:GetLruKCacheReq, cache: LRUKCache=Depends(use_lru_cache)):
    return await control.get_lru2_cache(req,cache)

@user_view.post("/test_lru2")
async def put_lru2_cache(req: PutLruKCacheReq, cache: LRUKCache=Depends(use_lru_cache)):
    # cache.put(**req.dict())
    return await control.put_lru2_cache(req,cache)

