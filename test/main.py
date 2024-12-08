import uvicorn
from home.tables import BaseUser, Post
import asyncio


# async def main():
#     # user = BaseUser(username="piccolo")
#     # user_2 = BaseUser(username="user2")
#     # await user.save()
#     # await user_2.save()

#     # user_id = (
#     #     await BaseUser.select(BaseUser.uuid)
#     #     .where(BaseUser.uuid == "e98ba2da-565b-4023-8d5a-503a2c269349")
#     #     .first()
#     # )

#     # second_post = Post(
#     #     post_user=user_id["uuid"],
#     #     description="description",
#     #     users_mentioned=[user_id["uuid"]],
#     # )
#     # await second_post.save()


if __name__ == "__main__":
    # asyncio.run(main())
    uvicorn.run("app:app", reload=True)
