from fastapi import FastAPI
from .routes import get, post, user

__doc__ = """backend backoffice"""

app = FastAPI()

app.include_router(router=get.router)
app.include_router(router=post.router)
app.include_router(router=user.router)

