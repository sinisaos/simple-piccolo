import asyncio
import datetime
import typing as t

import uvicorn
from litestar import Litestar, asgi, delete, get, patch, post
from litestar.exceptions import NotFoundException
from litestar.types import Receive, Scope, Send
from piccolo.apps.user.tables import BaseUser
from piccolo.columns import Boolean, ForeignKey, Interval, Varchar
from piccolo.table import Table, create_db_tables
from piccolo.utils.pydantic import create_pydantic_model
from piccolo_admin.endpoints import create_admin
from piccolo_api.session_auth.tables import SessionsBase

from piccolo_conf import DB


class Task(Table, db=DB):
    name = Varchar()
    completed = Boolean(default=False)
    duration = Interval()
    task_user = ForeignKey(references=BaseUser)


TaskModelIn: t.Any = create_pydantic_model(
    table=Task,
    model_name="TaskModelIn",
)
TaskModelOut: t.Any = create_pydantic_model(
    table=Task,
    include_default_columns=True,
    model_name="TaskModelOut",
    nested=True,
)


# mounting Piccolo Admin
@asgi("/admin/", is_mount=True)
async def admin(scope: "Scope", receive: "Receive", send: "Send") -> None:
    await create_admin(tables=[Task])(scope, receive, send)


@get("/tasks", tags=["Task"])
async def tasks() -> t.List[TaskModelOut]:
    tasks = (
        await Task.select(
            Task.all_columns(),
            Task.task_user.id,
            Task.task_user.username,
        )
        .order_by(Task.id, ascending=False)
        .output(nested=True)
    )
    return tasks


@post("/tasks", tags=["Task"])
async def create_task(data: TaskModelIn) -> TaskModelOut:
    task = Task(**data.dict())
    await task.save()
    return task.to_dict()


@patch("/tasks/{task_id:int}", tags=["Task"])
async def update_task(task_id: int, data: TaskModelIn) -> TaskModelOut:
    task = await Task.objects().get(Task.id == task_id)
    if not task:
        raise NotFoundException("Task does not exist")
    for key, value in data.dict().items():
        setattr(task, key, value)

    await task.save()
    return task.to_dict()


@delete("/tasks/{task_id:int}", tags=["Task"])
async def delete_task(task_id: int) -> None:
    task = await Task.objects().get(Task.id == task_id)
    if not task:
        raise NotFoundException("Task does not exist")
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
TYPE_ENCODERS = {datetime.timedelta: str}


app = Litestar(
    route_handlers=[
        admin,
        tasks,
        create_task,
        update_task,
        delete_task,
    ],
    type_encoders=TYPE_ENCODERS,
)

if __name__ == "__main__":
    asyncio.run(main())

    uvicorn.run(app, host="127.0.0.1", port=8000)
