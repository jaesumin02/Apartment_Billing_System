from models.base import BaseModel


class TenantModel(BaseModel):
    def __init__(self, db):
        super().__init__(db)

    def all(self):
        return self.query("""
        SELECT t.*, u.unit_code, u.unit_type, u.price AS room_price
        FROM tenants t
        LEFT JOIN units u ON t.unit_id = u.unit_id
        ORDER BY t.tenant_id
        """)

    def active(self):
        return self.query("""
        SELECT t.*, u.unit_code, u.unit_type, u.price AS room_price
        FROM tenants t
        LEFT JOIN units u ON t.unit_id = u.unit_id
        WHERE t.status='Active'
        ORDER BY t.tenant_id
        """)

    def terminated(self):
        return self.query("""
        SELECT t.*, u.unit_code, u.unit_type, u.price AS room_price
        FROM tenants t
        LEFT JOIN units u ON t.unit_id = u.unit_id
        WHERE t.status='Terminated'
        ORDER BY t.tenant_id
        """)

    def tenants_in_unit(self, unit_id):
        return self.query("""
        SELECT * FROM tenants
        WHERE unit_id=? AND status='Active'
        ORDER BY name
        """, (unit_id,))

    def get(self, tenant_id):
        rows = self.query("""
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
        self.execute(f"INSERT INTO tenants ({cols}) VALUES ({placeholders})", values)

    def update(self, tenant_id, **data):
        if not data:
            return
        fields = ", ".join([f"{k}=?" for k in data.keys()])
        values = list(data.values()) + [tenant_id]
        self.execute(f"UPDATE tenants SET {fields} WHERE tenant_id=?", values)

    def terminate(self, tenant_id, move_out_date, reason):
        self.update(tenant_id, status="Terminated", move_out=move_out_date, move_out_reason=reason)

    def restore(self, tenant_id):
        self.update(tenant_id, status="Active", move_out=None, move_out_reason="")

    def search_active(self, query):
        like = f"%{query}%"
        return self.query("""
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
