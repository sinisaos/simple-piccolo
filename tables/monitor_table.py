import typing as t
import uuid
from enum import Enum

from piccolo.columns import Real, Text, Timestamp, Varchar
from piccolo.table import Table

from piccolo_conf import DB


class MonitorLog(Table, db=DB):
    class ActionType(str, Enum):
        """An enumeration of MonitorLog table actions type."""

        creating = "creating"
        updating = "updating"
        deleting = "deleting"

    action_time = Timestamp()
    action_type = Varchar(choices=ActionType)
    table_name = Varchar()
    change_message = Text()
    execution_time = Real()

    @classmethod
    async def record_save_action(
        cls,
        table: t.Type[Table],
        execution_time: float,
        new_row_id=t.Union[str, uuid.UUID, int],
    ):
        result = cls(
            action_type=cls.ActionType.creating,
            table_name=table._meta.tablename.title(),
            change_message=f"Create row {new_row_id} in "
            f"{table._meta.tablename.title()} table",
            execution_time=execution_time,
        )
        await result.save().run()

    @classmethod
    async def record_patch_action(
        cls,
        table: t.Type[Table],
        execution_time: float,
        row_id: t.Union[str, uuid.UUID, int],
    ):
        result = cls(
            action_type=cls.ActionType.updating,
            table_name=table._meta.tablename.title(),
            change_message=f"Update row "
            f"{row_id} in {table._meta.tablename.title()} table",
            execution_time=execution_time,
        )
        await result.save().run()

    @classmethod
    async def record_delete_action(
        cls,
        table: t.Type[Table],
        execution_time: float,
        row_id: t.Union[str, uuid.UUID, int],
    ):
        result = cls(
            action_type=cls.ActionType.deleting,
            table_name=table._meta.tablename.title(),
            change_message=f"Delete row {row_id} "
            f"in {table._meta.tablename.title()} table",
            execution_time=execution_time,
        )
        await result.save().run()
