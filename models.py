import datetime
from typing import Optional
from .database import Database

class UnitModel:
    def __init__(self, db: Database):
        self.db = db

    def all(self):
        return self.db.query("SELECT * FROM units ORDER BY unit_type, unit_code")

    def filter_by_status(self, status=None):
        if status == "Vacant":
            return self.db.query("SELECT * FROM units WHERE status='Vacant' ORDER BY unit_type, unit_code")
        elif status == "Occupied":
            return self.db.query("SELECT * FROM units WHERE status='Occupied' ORDER BY unit_type, unit_code")
        else:
            return self.all()

    def by_type(self, unit_type):
        return self.db.query("SELECT * FROM units WHERE unit_type=? ORDER BY unit_code", (unit_type,))

    def available_by_type(self, unit_type):
        return self.db.query(
            "SELECT * FROM units WHERE unit_type=? AND status='Vacant' ORDER BY unit_code",
            (unit_type,)
        )

    def get(self, unit_id):
        rows = self.db.query("SELECT * FROM units WHERE unit_id=?", (unit_id,))
        return rows[0] if rows else None

    def update_status(self, unit_id, status):
        self.db.execute("UPDATE units SET status=? WHERE unit_id=?", (status, unit_id))

    def update_capacity(self, unit_id, capacity):
        self.db.execute("UPDATE units SET capacity=? WHERE unit_id=?", (capacity, unit_id))

class TenantModel:
    def __init__(self, db: Database):
        self.db = db

    def all(self):
        return self.db.query("""
        SELECT t.*, u.unit_code, u.unit_type, u.price AS room_price
        FROM tenants t
        LEFT JOIN units u ON t.unit_id = u.unit_id
        ORDER BY t.tenant_id
        """)

    def active(self):
        return self.db.query("""
        SELECT t.*, u.unit_code, u.unit_type, u.price AS room_price
        FROM tenants t
        LEFT JOIN units u ON t.unit_id = u.unit_id
        WHERE t.status='Active'
        ORDER BY t.tenant_id
        """)

    def terminated(self):
        return self.db.query("""
        SELECT t.*, u.unit_code, u.unit_type, u.price AS room_price
        FROM tenants t
        LEFT JOIN units u ON t.unit_id = u.unit_id
        WHERE t.status='Terminated'
        ORDER BY t.tenant_id
        """)

    def tenants_in_unit(self, unit_id):
        return self.db.query("""
        SELECT * FROM tenants
        WHERE unit_id=? AND status='Active'
        ORDER BY name
        """, (unit_id,))

    def get(self, tenant_id):
        rows = self.db.query("""
        SELECT t.*, u.unit_code, u.unit_type, u.price AS room_price
        FROM tenants t
        LEFT JOIN units u ON t.unit_id = u.unit_id
        WHERE t.tenant_id=?
        """, (tenant_id,))
        return rows[0] if rows else None

    def create(self, **data):
        fields = [
            "name", "contact", "unit_id", "tenant_type",
            "move_in", "move_out", "status",
            "guardian_name", "guardian_contact", "guardian_relation",
            "emergency_contact", "advance_paid", "deposit_paid", "move_out_reason"
        ]
        cols = ",".join(fields)
        placeholders = ",".join(["?"] * len(fields))
        values = [data.get(f) for f in fields]
        self.db.execute(f"INSERT INTO tenants ({cols}) VALUES ({placeholders})", values)

    def update(self, tenant_id, **data):
        if not data:
            return
        fields = ", ".join([f"{k}=?" for k in data.keys()])
        values = list(data.values()) + [tenant_id]
        self.db.execute(f"UPDATE tenants SET {fields} WHERE tenant_id=?", values)

    def terminate(self, tenant_id, move_out_date, reason):
        self.update(tenant_id, status="Terminated", move_out=move_out_date, move_out_reason=reason)

    def restore(self, tenant_id):
        self.update(tenant_id, status="Active", move_out=None, move_out_reason="")

    def search_active(self, query):
        like = f"%{query}%"
        return self.db.query("""
        SELECT t.*, u.unit_code, u.unit_type, u.price AS room_price
        FROM tenants t
        LEFT JOIN units u ON t.unit_id = u.unit_id
        WHERE t.status='Active'
          AND (
              t.name LIKE ?
              OR t.contact LIKE ?
              OR u.unit_code LIKE ?
              OR CAST(t.tenant_id AS TEXT) LIKE ?
          )
        ORDER BY t.tenant_id
        """, (like, like, like, like))

class PaymentModel:
    def __init__(self, db: Database):
        self.db = db

    def create(self, tenant_id, rent, electricity, water, status="Paid", note=""):
        total = (rent or 0) + (electricity or 0) + (water or 0)
        date_paid = datetime.date.today().isoformat() if status == "Paid" else None
        cur = self.db.execute("""
        INSERT INTO payments (tenant_id, rent, electricity, water, total, date_paid, status, note)
        VALUES (?,?,?,?,?,?,?,?)
        """, (tenant_id, rent, electricity, water, total, date_paid, status, note))
        return cur.lastrowid

    def create_due(self, tenant_id, rent, electricity, water, note=""):
        total = (rent or 0) + (electricity or 0) + (water or 0)
        self.db.execute("""
        INSERT INTO payments (tenant_id, rent, electricity, water, total, date_paid, status, note)
        VALUES (?,?,?,?,?,?,?,?)
        """, (tenant_id, rent, electricity, water, total, None, "Due", note))

    def invoice_exists_with_note(self, tenant_id, note):
        if not note:
            return False
        row = self.db.query("""
        SELECT COUNT(*) as c FROM payments
        WHERE tenant_id=? AND note=?
        """, (tenant_id, note))[0]
        return (row["c"] or 0) > 0

    def all(self):
        return self.db.query("""
        SELECT p.*, t.name, t.tenant_type
        FROM payments p
        LEFT JOIN tenants t ON p.tenant_id = t.tenant_id
        ORDER BY p.payment_id DESC
        """)

    def get(self, payment_id):
        rows = self.db.query("""
        SELECT p.*, t.name, t.tenant_type
        FROM payments p
        LEFT JOIN tenants t ON p.tenant_id = t.tenant_id
        WHERE p.payment_id=?
        """, (payment_id,))
        return rows[0] if rows else None

    def update(self, payment_id, rent, electricity, water, status, note):
        total = (rent or 0) + (electricity or 0) + (water or 0)
        date_paid = datetime.date.today().isoformat() if status == "Paid" else None
        self.db.execute("""
        UPDATE payments
        SET rent=?, electricity=?, water=?, total=?, date_paid=?, status=?, note=?
        WHERE payment_id=?
        """, (rent, electricity, water, total, date_paid, status, note, payment_id))

    def total_for_month(self, year, month):
        start = datetime.date(year, month, 1)
        if month == 12:
            end = datetime.date(year + 1, 1, 1)
        else:
            end = datetime.date(year, month + 1, 1)
        row = self.db.query("""
        SELECT SUM(total) AS s
        FROM payments
        WHERE date_paid >= ? AND date_paid < ?
        """, (start.isoformat(), end.isoformat()))[0]
        return row["s"] or 0.0

class MaintenanceModel:
    def __init__(self, db: Database):
        self.db = db

    def create(self, tenant_id, description, priority, fee=0.0, staff=""):
        date_req = datetime.date.today().isoformat()
        self.db.execute("""
        INSERT INTO maintenance (tenant_id, description, priority, date_requested, status, fee, staff)
        VALUES (?,?,?,?,?,?,?)
        """, (tenant_id, description, priority, date_req, "Pending", fee, staff))

    def all(self):
        return self.db.query("""
        SELECT m.*, t.name AS tenant_name
        FROM maintenance m
        LEFT JOIN tenants t ON m.tenant_id = t.tenant_id
        ORDER BY m.request_id DESC
        """)

    def counts(self):
        total = self.db.query("SELECT COUNT(*) as c FROM maintenance")[0]["c"]
        pending = self.db.query("SELECT COUNT(*) as c FROM maintenance WHERE status='Pending'")[0]["c"]
        return total, pending

    def total_fee_for_month(self, year, month):
        start = datetime.date(year, month, 1)
        if month == 12:
            end = datetime.date(year + 1, 1, 1)
        else:
            end = datetime.date(year, month + 1, 1)
        row = self.db.query("""
        SELECT SUM(fee) AS s
        FROM maintenance
        WHERE date_requested >= ? AND date_requested < ?
        """, (start.isoformat(), end.isoformat()))[0]
        return row["s"] or 0.0

class StaffModel:
    def __init__(self, db: Database):
        self.db = db

    def all(self):
        return self.db.query("SELECT * FROM staff ORDER BY name")

    def active(self):
        return self.db.query("SELECT * FROM staff WHERE status='Active' ORDER BY name")

    def active_names(self):
        return [r["name"] for r in self.active()]

    def create(self, name, contact, role, status="Active"):
        self.db.execute("""
        INSERT INTO staff (name, contact, role, status)
        VALUES (?,?,?,?)
        """, (name, contact, role, status))

    def delete(self, staff_id):
        self.db.execute("DELETE FROM staff WHERE staff_id=?", (staff_id,))

    def archive(self, staff_id):
        """Soft-delete: mark staff as Archived."""
        self.db.execute("UPDATE staff SET status='Archived' WHERE staff_id=?", (staff_id,))

    def restore(self, staff_id):
        """Restore archived staff to Active."""
        self.db.execute("UPDATE staff SET status='Active' WHERE staff_id=?", (staff_id,))

    def archived(self):
        """Return archived staff rows."""
        return self.db.query("SELECT * FROM staff WHERE status='Archived' ORDER BY name")

class ActivityLogModel:
    def __init__(self, db: Database):
        self.db = db

    def log(self, action, details=""):
        ts = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
        self.db.execute(
            "INSERT INTO activity_log (timestamp, action, details) VALUES (?,?,?)",
            (ts, action, details),
        )

    def all(self):
        return self.db.query("SELECT * FROM activity_log ORDER BY log_id DESC")

    def clear(self):
        self.db.execute("DELETE FROM activity_log", ())

