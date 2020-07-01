import typing

from .entity import Entity
from ..corpora_orm import DbDataset


class Dataset(Entity):
    tables = [
        DbDataset,
    ]

    def __init__(self, db_obj: DbDataset):
        self.db_obj = db_obj

    @classmethod
    def _query(cls, key: str) -> typing.List["Dataset"]:
        """
        Queries the database for required entity data
        :param key: dataset.id is the primary key.
        :return: list of query result rows
        """
        result = cls.db.query(table_args=[DbDataset], filter_args=[key == DbDataset.id])
        return result

    @classmethod
    def _load(cls, db_result: typing.List["Dataset"]) -> "Dataset":
        """
        Parses a database query result into an Entity instance
        :param db_result: list of query result rows
        :return: Entity
        """
        try:
            return cls(db_result[0])
        except IndexError:
            return None

    def __getattr__(self, name):
        return self.db_obj.__getattribute__(name)
