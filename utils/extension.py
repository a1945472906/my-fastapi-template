import asyncio
from asyncio import Queue
from functools import wraps
from typing import List, TypeVar, Generic, Union
import time
from dotenv import dotenv_values
T = TypeVar("T")


class Job:
    async def execute(self):
        pass


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

class ExecutorPool:
    def __init__(self, executor_num: int):
        self.queue = Queue(executor_num)

        # self.loop = loop
        for _ in range(0, executor_num):
            loop.create_task(self.executor())

    async def executor(self):
        while True:
            job = await self.queue.get()
            await job.execute()

    async def put(self, job: Job):
        await self.queue.put(job)


def singleton(cls):
    instances = {}

    @wraps(cls)
    def wrapper(*args, **kwargs):
        name = cls.__name__
        if instances.__contains__(name):
            return instances.get(name)
        else:
            obj = cls(*args, **kwargs)
            instances[name] = obj
            return obj
    return wrapper


class Observer:
    def __init__(self, func):
        self.func = func

    def run(self, old_value, new_value):
        self.func(old_value, new_value)


class Observable:
    def get_observers(self) -> List:
        pass

    def watch(self, func):
        self.get_observers().append(Observer(func))

    def notify(self):
        for observe in self.get_observers():
            observe.run(self.old_value, self.value)


class Global(Generic[T], Observable):

    def __init__(self, value: T):
        self.__old_value = value
        self.__new_value = value
        self.observers = []

    def get_observers(self) -> List:
        return self.observers

    @property
    def value(self):
        return self.__new_value or self.__old_value

    @value.setter
    def value(self, value: T):
        self.__old_value, self.__new_value = self.__new_value, value
        self.notify()

    @property
    def old_value(self):
        return self.__old_value

class CacheValue:
    def __init__(self, expire: int, value):
        self.expire = time.time() + expire
        self.value = value

    def is_expired(self) -> bool:
        return time.time() > self.expire

    def get_value(self):
        return self.value

@singleton
class Cache:
    '''no lock'''

    def __init__(self, clean_tick=24 * 3600):
        self.map = dict()
        self.clean_tick = clean_tick
        r = loop.create_task(self.clean())
    # def expire(self, *_args,**_kwargs): #接口缓存
    #     map = self.map
    #
    #     def _wrap(func):
    #         @wraps(func)
    #         def wrapper(*args, **kwargs):
    #             key = func.__name__
    #             cache_value = map.get(key)
    #             if cache_value:
    #                 if cache_value.is_expired():
    #                     map.pop(key)
    #                 else:
    #                     return cache_value.get_value()
    #             expire = _kwargs.get("expire") or 3600
    #             result = func(*args, **kwargs)
    #             value = CacheValue(expire, result)
    #             map[func.__name__] = value
    #             return result
    #         return wrapper
    #     return _wrap

    def set(self, key: str, value: T, expire=24*3600):
        self.map[key] = CacheValue(expire=expire, value=value)

    def get(self, key: str) -> Union[T, None]:
        # print(self.map)
        value = self.map.get(key)
        if value and not value.is_expired():
            return value.get_value()
        else:
            return None

    def pop(self, key: str) -> Union[T, None]:
        try:
            value = self.map.pop(key)
        except:
            return None
        if value.is_expired():
            v = value.get_value()
            return v
        else:
            return None

    async def clean(self):
        while True:
            await asyncio.sleep(self.clean_tick)
            clean_keys = []
            for k,v in self.map.items():
                if v.is_expired():
                    clean_keys.append(k)
            for k in clean_keys:
                self.map.pop(k)




env = Global(dotenv_values(".env"))

def get_env() -> Global:
    return env

def test_global():

    func = lambda old_value,new_value: print("{old} -> {new}".format(old=old_value, new=new_value))

    g = Global(2)
    g.watch(func)
    g.value = 4

    g2 = Global("foo")
    g2.watch(func)
    g2.value = "bar"


# def test_cache():
#     cache1 = Cache()
#     cache2 = Cache()
#
#     @cache1.expire(3600)
#     def test_func():
#         return 'foo'
#     test_func()
#     print(cache1.map)
#     print(cache2.map)
#     for k, v in cache1.map.items():
#         print(k, v.value)


async def test_executor_pool():
    executor_pool = ExecutorPool(3)
    class TestJob(Job):
        def __init__(self, name):
            self.name = name
        async def execute(self):
            print("正在执行任务:{name}".format(name=self.name))
            await asyncio.sleep(5)

            print("任务:{name} 执行完毕".format(name=self.name))
    j1 = TestJob(1)
    j2 = TestJob(2)
    j3 = TestJob(3)
    # print(j1,j2,j3)
    await executor_pool.put(j1)
    await executor_pool.put(j2)
    await executor_pool.put(j3)

# if __name__ == '__main__':
#     test_global()
#     test_cache()
#     loop.run_until_complete(test_executor_pool())
#     loop.run_until_complete(asyncio.sleep(100))