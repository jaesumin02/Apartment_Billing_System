from models.base import BaseModel


class UnitModel(BaseModel):
    def __init__(self, db):
        super().__init__(db)

    def all(self):
        return self.query("SELECT * FROM units ORDER BY unit_type, unit_code")

    def filter_by_status(self, status=None):
        if status == "Vacant":
            return self.query("SELECT * FROM units WHERE status='Vacant' ORDER BY unit_type, unit_code")
        elif status == "Occupied":
            return self.query("SELECT * FROM units WHERE status='Occupied' ORDER BY unit_type, unit_code")
        else:
            return self.all()

    def get(self, unit_id):
        rows = self.query("SELECT * FROM units WHERE unit_id=?", (unit_id,))
        return rows[0] if rows else None

    def update_status(self, unit_id, status):
        self.execute("UPDATE units SET status=? WHERE unit_id=?", (status, unit_id))

    def update_capacity(self, unit_id, capacity):
        self.execute("UPDATE units SET capacity=? WHERE unit_id=?", (capacity, unit_id))
