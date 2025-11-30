import datetime
from models.base import BaseModel


class ActivityLogModel(BaseModel):
    def __init__(self, db):
        super().__init__(db)

    def log(self, action, details=""):
        ts = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
        self.execute(
            "INSERT INTO activity_log (timestamp, action, details) VALUES (?,?,?)",
            (ts, action, details),
        )

    def all(self):
        return self.query("SELECT * FROM activity_log ORDER BY log_id DESC")

    def clear(self):
        self.execute("DELETE FROM activity_log", ())
