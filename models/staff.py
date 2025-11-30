from models.base import BaseModel

class StaffModel(BaseModel):
    def __init__(self, db):
        super().__init__(db)

    def all(self):
        return self.query("SELECT * FROM staff ORDER BY name")

    def active(self):
        return self.query("SELECT * FROM staff WHERE status='Active' ORDER BY name")

    def active_names(self):
        return [r["name"] for r in self.active()]

    def create(self, name, contact, role, status="Active"):
        self.execute("""
        INSERT INTO staff (name, contact, role, status)
        VALUES (?,?,?,?)
        """, (name, contact, role, status))

    def delete(self, staff_id):
        self.execute("DELETE FROM staff WHERE staff_id=?", (staff_id,))

    def archive(self, staff_id):
        self.execute("UPDATE staff SET status='Archived' WHERE staff_id=?", (staff_id,))

    def restore(self, staff_id):
        self.execute("UPDATE staff SET status='Active' WHERE staff_id=?", (staff_id,))

    def archived(self):
        return self.query("SELECT * FROM staff WHERE status='Archived' ORDER BY name")
