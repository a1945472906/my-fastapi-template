from fastapi import FastAPI
from apps.app.view import user_view
app = FastAPI()
app.include_router(user_view,prefix="/user")
