from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from sqlalchemy import text
from utils.db.mark import DBMark
from typing import TypeVar, Generic, Optional


T = TypeVar("T", bound=DBMark)


class DB(Generic[T]):
    def __init__(self, db_url, pool_size: Optional[int] = 5, max_overflow: Optional[int] = 10):
        self.__engine = create_async_engine(db_url, pool_size=pool_size, max_overflow=max_overflow)
        self.async_sessoion = async_sessionmaker(self.__engine, expire_on_commit=False)

    async def execute(self, sql: str):
        async with self.__engine.begin() as conn:
            result = await conn.execute(text(sql))
            return result
    async def conn(self):
        conn = await self.__engine.begin()
        return conn

# if __name__ == '__main__':
#     from utils.extension import get_env
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     from mark import User
#     env = get_env()
#     db_url = env.value.get("DATABASE_URL")
#
#     print(db_url)
#     db = DB[User](db_url)
#     async def test():
#         result = await db.execute('''
#         select json_build_object(
#             'users', array_agg(json_build_object(
#                 'user_id', user_id,
#                 'username',username,
#                 'realname', realname,
#                 'user_desc', user_desc,
#                 'avatar', avatar,
#                 'sex', sex,
#                 'roles', roles
#             ))
#         ) from users_table
#         ''')
#
#         value = result.fetchone()
#         print(value)
#     loop.run_until_complete(test())
