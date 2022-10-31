from typing import Callable
from fastapi import APIRouter, FastAPI, Response, Request
from fastapi.routing import APIRoute
class Route:
    def as_route(self) -> APIRouter:
        pass


class View(Route):
    pass