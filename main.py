from fastapi import FastAPI

import models
from api.api import api_router
from db import engine

app = FastAPI()


models.Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

app.include_router(api_router)