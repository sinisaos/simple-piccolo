from piccolo.columns import ForeignKey, Varchar
from piccolo.columns.readable import Readable

from piccolo_conf import DB
from tables.base import BaseTable


class Manager(BaseTable, db=DB):
    name = Varchar(length=100)

    @classmethod
    def get_readable(cls) -> Readable:
        return Readable(template="%s", columns=[cls.name])


class Band(BaseTable, db=DB):
    name = Varchar(length=100)
    manager = ForeignKey(references=Manager)

    @classmethod
    def get_readable(cls) -> Readable:
        return Readable(template="%s", columns=[cls.name])


class Concert(BaseTable, db=DB):
    band_1 = ForeignKey(references=Band)
    band_2 = ForeignKey(references=Band)
