import typing as t

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from piccolo.engine import engine_finder
from piccolo_api.crud.serializers import create_pydantic_model
from home.tables import Post, BaseUser


async def open_database_connection_pool():
    try:
        engine = engine_finder()
        await engine.start_connection_pool()
    except Exception:
        print("Unable to connect to the database")


async def close_database_connection_pool():
    try:
        engine = engine_finder()
        await engine.close_connection_pool()
    except Exception:
        print("Unable to connect to the database")


@asynccontextmanager
async def lifespan(_: FastAPI):
    await open_database_connection_pool()
    yield
    await close_database_connection_pool()


app = FastAPI(lifespan=lifespan)

UserModelIn: t.Any = create_pydantic_model(
    table=BaseUser,
    model_name="UserModelIn",
)
UserModelOut: t.Any = create_pydantic_model(
    table=BaseUser,
    include_default_columns=True,
    model_name="UserModelOut",
)

PostModelIn: t.Any = create_pydantic_model(
    table=Post,
    model_name="PostModelIn",
)
PostModelOut: t.Any = create_pydantic_model(
    table=Post,
    include_default_columns=True,
    model_name="PostModelOut",
)


@app.get("/users/", response_model=t.List[UserModelOut])
async def users():
    return await BaseUser.select()


@app.post("/users/", response_model=UserModelOut)
async def create_user(user_model: UserModelOut):
    user = BaseUser(**user_model.dict())
    await user.save()
    return user.to_dict()


@app.get("/posts/", response_model=t.List[PostModelOut])
async def users():
    return await Post.select(Post.all_columns(), Post.post_user.all_columns())


@app.post("/posts/", response_model=PostModelOut)
async def create_user(post_model: PostModelOut):
    post = Post(**post_model.dict())
    await post.save()
    return post.to_dict()
