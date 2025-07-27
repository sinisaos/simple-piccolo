import asyncio
from typing import Annotated, Any

import uvicorn
from hypercorn.middleware import DispatcherMiddleware
from lihil import Empty, HTTPException, Lihil, Route
from msgspec import Struct
from piccolo.apps.user.tables import BaseUser
from piccolo.columns import Boolean, Varchar
from piccolo.table import Table, create_db_tables
from piccolo_admin.endpoints import create_admin
from piccolo_api.session_auth.tables import SessionsBase

from piccolo_conf import DB


# Piccolo table
class Task(Table, db=DB):
    name = Varchar()
    completed = Boolean(default=False)


# msgspec structs
class TaskModelIn(Struct):
    name: str
    completed: bool = False

    def dict_converter(self):
        return {f: getattr(self, f) for f in self.__struct_fields__}


class TaskModelOut(Struct):
    id: int
    name: str
    completed: bool = False


# Check if the record is None. Use for query callback
def check_record_not_found(result: dict[str, Any]) -> dict[str, Any]:
    if result is None:
        raise HTTPException(detail="Record not found", status=404)
    return result


# Service class
class TaskService:
    async def list_tasks(self, limit: int, offset: int) -> list[TaskModelOut]:
        results = (
            await Task.select()
            .limit(limit)
            .offset(offset)
            .order_by(Task._meta.primary_key, ascending=False)
        )
        return [TaskModelOut(**result) for result in results]

    async def single_task(self, task_id: int) -> TaskModelOut:
        task = (
            await Task.select()
            .where(Task._meta.primary_key == task_id)
            .first()
            .callback(check_record_not_found)
        )
        return TaskModelOut(**task)

    async def create_task(self, task_model: TaskModelIn) -> TaskModelOut:
        task = Task(**task_model.dict_converter())
        await task.save()
        return TaskModelOut(**task.to_dict())

    async def update_task(
        self, task_id: int, task_model: TaskModelIn
    ) -> TaskModelOut:
        task = (
            await Task.objects()
            .get(Task._meta.primary_key == task_id)
            .callback(check_record_not_found)
        )
        for key, value in task_model.dict_converter().items():
            setattr(task, key, value)

        await task.save()
        return TaskModelOut(**task.to_dict())

    async def delete_task(self, task_id: int) -> None:
        task = (
            await Task.objects()
            .get(Task._meta.primary_key == task_id)
            .callback(check_record_not_found)
        )
        await task.remove()


# service instantiation
service = TaskService()

# root router
root = Route()

# task router
task_route = Route("/tasks")


@task_route.get
async def tasks(limit: int = 15, offset: int = 0) -> list[TaskModelOut]:
    return await service.list_tasks(limit=limit, offset=offset)


@task_route.sub("{task_id}").get
async def task(task_id: int) -> TaskModelOut:
    return await service.single_task(task_id=task_id)


@task_route.post
async def task_create(task_model: TaskModelIn) -> TaskModelOut:
    return await service.create_task(task_model=task_model)


@task_route.sub("{task_id}").put
async def task_update(task_id: int, task_model: TaskModelIn) -> TaskModelOut:
    return await service.update_task(task_id=task_id, task_model=task_model)


@task_route.sub("{task_id}").delete
async def task_delete(task_id: int) -> Annotated[Empty, 204]:
    await service.delete_task(task_id=task_id)


# include task router
root.include_subroutes(task_route)

# Lihil app instantiation
app = Lihil(root)

# enable the admin application using DispatcherMiddleware
app = DispatcherMiddleware(
    {
        "/admin": create_admin(tables=[Task]),
        "": app,  # type: ignore
    }
)


async def main():
    # Tables creating
    await create_db_tables(
        BaseUser,
        SessionsBase,
        Task,
        if_not_exists=True,
    )

    # Creating admin user
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


if __name__ == "__main__":
    asyncio.run(main())

    uvicorn.run(app, host="127.0.0.1", port=8000)
