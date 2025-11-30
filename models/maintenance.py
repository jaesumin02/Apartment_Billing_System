import datetime
from models.base import BaseModel, Reportable

class MaintenanceModel(BaseModel, Reportable):
    def __init__(self, db):
        super().__init__(db)

    def create(self, tenant_id, description, priority, fee=0.0, staff=""):
        date_req = datetime.date.today().isoformat()
        self.execute("""
        INSERT INTO maintenance (tenant_id, description, priority, date_requested, status, fee, staff)
        VALUES (?,?,?,?,?,?,?)
        """, (tenant_id, description, priority, date_req, "Pending", fee, staff))

    def all(self):
        return self.query("""
        SELECT m.*, t.name AS tenant_name
        FROM maintenance m
        LEFT JOIN tenants t ON m.tenant_id = t.tenant_id
        WHERE m.deleted = 0
        ORDER BY m.request_id DESC
        """)

    def all_including_deleted(self):
        return self.query("""
        SELECT m.*, t.name AS tenant_name
        FROM maintenance m
        LEFT JOIN tenants t ON m.tenant_id = t.tenant_id
        ORDER BY m.request_id DESC
        """)

    def counts(self):
        total = self.query("SELECT COUNT(*) as c FROM maintenance WHERE deleted=0")[0]["c"]
        pending = self.query("SELECT COUNT(*) as c FROM maintenance WHERE status='Pending' AND deleted=0")[0]["c"]
        return total, pending

    def total_fee_for_month(self, year, month):
        start = datetime.date(year, month, 1)
        if month == 12:
            end = datetime.date(year + 1, 1, 1)
        else:
            end = datetime.date(year, month + 1, 1)
        row = self.query("""
        SELECT SUM(fee) AS s
        FROM maintenance
        WHERE date_requested >= ? AND date_requested < ? AND deleted=0
        """, (start.isoformat(), end.isoformat()))[0]
        return row["s"] or 0.0

    def total_for_month(self, year, month):
        return self.total_fee_for_month(year, month)

    def get(self, request_id):
        rows = self.query("""
        SELECT m.*, t.name AS tenant_name
        FROM maintenance m
        LEFT JOIN tenants t ON m.tenant_id = t.tenant_id
        WHERE m.request_id=?
        """, (request_id,))
        return rows[0] if rows else None

    def get_deleted(self, request_id):
        rows = self.query("""
        SELECT m.*, t.name AS tenant_name
        FROM maintenance m
        LEFT JOIN tenants t ON m.tenant_id = t.tenant_id
        WHERE m.request_id=? AND m.deleted=1
        """, (request_id,))
        return rows[0] if rows else None

    def update_status(self, request_id, status):
        self.execute("UPDATE maintenance SET status=? WHERE request_id=?", (status, request_id))

    def delete(self, request_id):
        self.execute("UPDATE maintenance SET deleted=1 WHERE request_id=?", (request_id,))

    def restore(self, request_id):
        self.execute("UPDATE maintenance SET deleted=0 WHERE request_id=?", (request_id,))

    def update(self, request_id, tenant_id, description, priority, fee=0.0, staff=""):
        self.execute("""
        UPDATE maintenance
        SET tenant_id=?, description=?, priority=?, fee=?, staff=?
        WHERE request_id=?
        """, (tenant_id, description, priority, fee, staff, request_id))
