import asyncio

import uvicorn
from fastapi import FastAPI
from piccolo.apps.user.tables import BaseUser
from piccolo_api.session_auth.tables import SessionsBase
from starlette.routing import Mount

from custom_piccolo_admin import create_admin
from tables.monitor_table import MonitorLog
from tables.user_tables import Band, Concert, Manager

# FastAPI app instantiation and mounting admin
app = FastAPI(
    routes=[
        Mount(
            "/admin/",
            create_admin(
                tables=[Manager, MonitorLog, Band, Concert],
            ),
        )
    ],
)


async def main():
    # Tables creating
    await BaseUser.create_table(if_not_exists=True)
    await SessionsBase.create_table(if_not_exists=True)
    await Manager.create_table(if_not_exists=True)
    await Band.create_table(if_not_exists=True)
    await Concert.create_table(if_not_exists=True)
    await MonitorLog.create_table(if_not_exists=True)

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
