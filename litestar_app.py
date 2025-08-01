import asyncio
from datetime import timedelta
from typing import Any

import uvicorn
from litestar import Litestar, asgi, delete, get, patch, post
from litestar.exceptions import NotFoundException
from litestar.types import Receive, Scope, Send
from piccolo.apps.user.tables import BaseUser
from piccolo.columns import Boolean, ForeignKey, Interval, Varchar
from piccolo.table import Table, create_db_tables
from piccolo_admin.endpoints import create_admin
from piccolo_api.session_auth.tables import SessionsBase
from pydantic import BaseModel

from piccolo_conf import DB


class Task(Table, db=DB):
    name = Varchar()
    completed = Boolean(default=False)
    duration = Interval()
    task_user = ForeignKey(references=BaseUser)


# Check if the record is None. Use for query callback
def check_record_not_found(result: dict[str, Any]) -> dict[str, Any]:
    if result is None:
        raise NotFoundException(detail="Record not found")
    return result


class User(BaseModel):
    id: int
    username: str


class TaskModelIn(BaseModel):
    name: str
    completed: bool = False
    duration: timedelta
    task_user: int


class TaskModelOut(BaseModel):
    id: int
    name: str
    completed: bool = False
    duration: timedelta
    task_user: User


class TaskModelPartial(BaseModel):
    name: str
    completed: bool = False
    duration: timedelta


# mounting Piccolo Admin
@asgi("/admin/", is_mount=True)
async def admin(scope: "Scope", receive: "Receive", send: "Send") -> None:
    await create_admin(tables=[Task])(scope, receive, send)


@get("/tasks", tags=["Task"])
async def tasks() -> list[TaskModelOut]:
    all_columns: Any = Task.all_columns()
    tasks = (
        await Task.select(
            all_columns,
            Task.task_user.id,
            Task.task_user.username,
        )
        .order_by(Task._meta.primary_key, ascending=False)
        .output(nested=True)
    )
    return [TaskModelOut(**task) for task in tasks]


@get("/tasks/{task_id:int}", tags=["Task"])
async def single_task(task_id: int) -> TaskModelOut:
    all_columns: Any = Task.all_columns()
    task = (
        await Task.select(
            all_columns,
            Task.task_user.id,
            Task.task_user.username,
        )
        .where(Task._meta.primary_key == task_id)
        .first()
        .output(nested=True)
        .callback(check_record_not_found)
    )
    return TaskModelOut(**task)


@post("/tasks", tags=["Task"])
async def create_task(data: TaskModelIn) -> TaskModelOut:
    task = Task(**data.model_dump())
    await task.save()

    all_columns: Any = Task.all_columns()
    task_out = (
        await Task.select(
            all_columns,
            Task.task_user.id,
            Task.task_user.username,
        )
        .where(Task._meta.primary_key == task.id)
        .first()
        .output(nested=True)
    )
    return TaskModelOut(**task_out)


@patch("/tasks/{task_id:int}", tags=["Task"])
async def update_task(task_id: int, data: TaskModelPartial) -> TaskModelOut:
    task = (
        await Task.objects()
        .get(Task._meta.primary_key == task_id)
        .callback(check_record_not_found)
    )
    for key, value in data.model_dump().items():
        setattr(task, key, value)

    await task.save()

    all_columns: Any = Task.all_columns()
    task_out = (
        await Task.select(
            all_columns,
            Task.task_user.id,
            Task.task_user.username,
        )
        .where(Task._meta.primary_key == task_id)
        .first()
        .output(nested=True)
    )
    return TaskModelOut(**task_out)


@delete("/tasks/{task_id:int}", tags=["Task"])
async def delete_task(task_id: int) -> None:
    task = (
        await Task.objects()
        .get(Task._meta.primary_key == task_id)
        .callback(check_record_not_found)
    )
    await task.remove()


async def main():
    # Tables creating
    await create_db_tables(
        BaseUser,
        SessionsBase,
        Task,
        if_not_exists=True,
    )

    # Creating admin users
    if not await BaseUser.exists().where(BaseUser.email == "admin@test.com"):
        user = BaseUser(
            username="piccolo",
            password="piccolo123",
            email="admin@test.com",
            admin=True,
            active=True,
            superuser=True,
        )
        await user.save()


# is used to serialize the Interval() column because
# datetime.timedelta is currently not supported in
# msgspec https://github.com/jcrist/msgspec/issues/260
TYPE_ENCODERS = {timedelta: str}


app = Litestar(
    debug=True,
    route_handlers=[
        admin,
        tasks,
        single_task,
        create_task,
        update_task,
        delete_task,
    ],
    type_encoders=TYPE_ENCODERS,
)

if __name__ == "__main__":
    asyncio.run(main())

    uvicorn.run(app, host="127.0.0.1", port=8000)
