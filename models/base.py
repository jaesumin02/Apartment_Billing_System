from abc import ABC, abstractmethod


class BaseModel(ABC):
    def __init__(self, db: "Database"):
        self._db = db

    def query(self, sql, params=()):
        return self._db.query(sql, params)

    def execute(self, sql, params=()):
        return self._db.execute(sql, params)


class Reportable(ABC):
    @abstractmethod
    def total_for_month(self, year, month):
        raise NotImplementedError()
