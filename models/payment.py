import datetime
from models.base import BaseModel, Reportable

class PaymentModel(BaseModel, Reportable):
    def __init__(self, db):
        super().__init__(db)

    def create(self, tenant_id, rent, electricity, water, status="Paid", note=""):
        total = (rent or 0) + (electricity or 0) + (water or 0)
        date_paid = datetime.date.today().isoformat() if status == "Paid" else None
        cur = self.execute("""
        INSERT INTO payments (tenant_id, rent, electricity, water, total, date_paid, status, note)
        VALUES (?,?,?,?,?,?,?,?)
        """, (tenant_id, rent, electricity, water, total, date_paid, status, note))
        return cur.lastrowid

    def create_due(self, tenant_id, rent, electricity, water, note=""):
        total = (rent or 0) + (electricity or 0) + (water or 0)
        self.execute("""
        INSERT INTO payments (tenant_id, rent, electricity, water, total, date_paid, status, note)
        VALUES (?,?,?,?,?,?,?,?)
        """, (tenant_id, rent, electricity, water, total, None, "Due", note))

    def invoice_exists_with_note(self, tenant_id, note):
        if not note:
            return False
        row = self.query("""
        SELECT COUNT(*) as c FROM payments
        WHERE tenant_id=? AND note=?
        """, (tenant_id, note))[0]
        return (row["c"] or 0) > 0

    def all(self):
        return self.query("""
        SELECT p.*, t.name, t.tenant_type
        FROM payments p
        LEFT JOIN tenants t ON p.tenant_id = t.tenant_id
        ORDER BY p.payment_id DESC
        """)

    def get(self, payment_id):
        rows = self.query("""
        SELECT p.*, t.name, t.tenant_type
        FROM payments p
        LEFT JOIN tenants t ON p.tenant_id = t.tenant_id
        WHERE p.payment_id=?
        """, (payment_id,))
        return rows[0] if rows else None

    def update(self, payment_id, rent, electricity, water, status, note):
        total = (rent or 0) + (electricity or 0) + (water or 0)
        date_paid = datetime.date.today().isoformat() if status == "Paid" else None
        self.execute("""
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
        row = self.query("""
        SELECT SUM(total) AS s
        FROM payments
        WHERE date_paid >= ? AND date_paid < ?
        """, (start.isoformat(), end.isoformat()))[0]
        return row["s"] or 0.0
