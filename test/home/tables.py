import uuid
from piccolo.table import Table
from piccolo.columns import Array, Text, ForeignKey, Varchar, UUID


def generate_uuid():
    return str(uuid.uuid4())


class BaseUser(Table):
    uuid = UUID(primary_key=True, default=generate_uuid)
    username = Varchar()


class Post(Table):
    uuid = UUID(primary_key=True, default=generate_uuid)
    post_user = ForeignKey(BaseUser, null=False)
    description = Text()
    users_mentioned = Array(base_column=UUID(default=generate_uuid))
