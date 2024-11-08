import time

from piccolo.table import Table

from tables.monitor_table import MonitorLog


class BaseTable(Table):
    """
    Base class with overriding methods.
    All other tables inherit from this parent class
    """

    # override save method for create and update objects
    def save(self, columns=None):
        table = self.__class__
        pk = self.id
        save_ = super().save

        class Save:
            async def run(self, *args, **kwargs):
                # create
                try:
                    start_time = time.time()
                    new_row = await save_(columns=columns).run(*args, **kwargs)
                    end_time = time.time() - start_time

                    await MonitorLog.record_save_action(
                        table,
                        new_row_id=new_row[0]["id"],
                        execution_time=end_time,
                    )
                # update
                except IndexError:
                    start_time = time.time()
                    await save_(columns=columns).run(*args, **kwargs)
                    end_time = time.time() - start_time

                    await MonitorLog.record_patch_action(
                        table,
                        row_id=pk,
                        execution_time=end_time,
                    )

            def __await__(self):
                return self.run().__await__()

        return Save()

    # override remove method for delete objects
    def remove(self):
        table = self.__class__
        pk = self.id
        remove_ = super().remove

        class Remove:
            async def run(self, *args, **kwargs):
                start_time = time.time()
                await remove_().run(*args, **kwargs)
                end_time = time.time() - start_time

                await MonitorLog.record_delete_action(
                    table,
                    row_id=pk,
                    execution_time=end_time,
                )

            def __await__(self):
                return self.run().__await__()

        return Remove()
