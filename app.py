import asyncio
import typing as t

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from piccolo.apps.user.tables import BaseUser
from piccolo.columns import ForeignKey, Varchar
from piccolo.columns.readable import Readable
from piccolo.engine.sqlite import SQLiteEngine
from piccolo.table import Table
from piccolo_admin.endpoints import create_admin
from piccolo_api.session_auth.tables import SessionsBase
from starlette.routing import Mount, Route

from piccolo_conf import DB

# Tables example
class Manager(Table, db=DB):
    name = Varchar(length=100)

    @classmethod
    def get_readable(cls) -> Readable:
        return Readable(template="%s", columns=[cls.name])


class Band(Table, db=DB):
    name = Varchar(length=100)
    manager = ForeignKey(references=Manager)

    @classmethod
    def get_readable(cls) -> Readable:
        return Readable(template="%s", columns=[cls.name])


class Concert(Table, db=DB):
    band_1 = ForeignKey(references=Band)
    band_2 = ForeignKey(references=Band)


# FastAPI app instantiation and mounting admin
app = FastAPI(
    routes=[
        Mount(
            "/admin/",
            create_admin(
                tables=[Manager, Band, Concert],
            ),
        )
    ],
)


# Routes example
@app.get("/")
async def root() -> t.Dict[str, t.Any]:
    data = await Concert.select(
        Concert.all_columns(),
        Concert.band_1.id,
        Concert.band_1.name,
        Concert.band_1.manager.id,
        Concert.band_1.manager.name,
        Concert.band_2.id,
        Concert.band_2.name,
        Concert.band_2.manager.id,
        Concert.band_2.manager.name,
    ).output(nested=True)

    return JSONResponse({"data": data})


async def main():
    # Tables creating
    await BaseUser.create_table(if_not_exists=True)
    await SessionsBase.create_table(if_not_exists=True)
    await Manager.create_table(if_not_exists=True)
    await Band.create_table(if_not_exists=True)
    await Concert.create_table(if_not_exists=True)

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
