import os
import sqlite3
import datetime
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

# ===============================
# CONFIG / CONSTANTS
# ===============================

DB_FILE = "apartment_pro.db"
DORM_DEFAULT_CAPACITY = 6
NOTICE_PERIOD_DAYS = 30   # for future use (e.g., move-out notice)

# Fixed utility rates
SOLO_ELEC = 1500.0
SOLO_WATER = 150.0
FAMILY_ELEC = 2500.0
FAMILY_WATER = 300.0
DORM_ELEC = 150.0
DORM_WATER = 80.0

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


# ===============================
# DB HELPERS
# ===============================

def ensure_column(conn, table, column, col_def):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in cur.fetchall()]
    if column not in cols:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}")
        conn.commit()


# ===============================
# DATABASE + MODELS
# ===============================

class Database:
    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file
        first_time = not os.path.exists(db_file)
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.setup(first_time)

    def setup(self, first_time=False):
        c = self.conn.cursor()

        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        );
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS units (
            unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            unit_code TEXT,
            unit_type TEXT,
            price REAL,
            status TEXT,
            capacity INTEGER
        );
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            tenant_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            contact TEXT,
            unit_id INTEGER,
            tenant_type TEXT,
            move_in DATE,
            move_out DATE,
            status TEXT,
            guardian_name TEXT,
            guardian_contact TEXT,
            guardian_relation TEXT,
            emergency_contact TEXT,
            advance_paid REAL DEFAULT 0,
            deposit_paid REAL DEFAULT 0,
            move_out_reason TEXT,
            FOREIGN KEY(unit_id) REFERENCES units(unit_id)
        );
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id INTEGER,
            rent REAL,
            electricity REAL,
            water REAL,
            total REAL,
            date_paid DATE,
            status TEXT,
            note TEXT,
            FOREIGN KEY(tenant_id) REFERENCES tenants(tenant_id)
        );
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS maintenance (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id INTEGER,
            description TEXT,
            priority TEXT,
            date_requested DATE,
            status TEXT,
            fee REAL DEFAULT 0,
            staff TEXT,
            FOREIGN KEY(tenant_id) REFERENCES tenants(tenant_id)
        );
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            contact TEXT,
            role TEXT,
            status TEXT
        );
        """)

        self.conn.commit()

        # Defensive ensure columns exist
        ensure_column(self.conn, "units", "capacity", "INTEGER DEFAULT 1")
        ensure_column(self.conn, "tenants", "guardian_name", "TEXT DEFAULT ''")
        ensure_column(self.conn, "tenants", "guardian_contact", "TEXT DEFAULT ''")
        ensure_column(self.conn, "tenants", "guardian_relation", "TEXT DEFAULT ''")
        ensure_column(self.conn, "tenants", "emergency_contact", "TEXT DEFAULT ''")
        ensure_column(self.conn, "tenants", "advance_paid", "REAL DEFAULT 0")
        ensure_column(self.conn, "tenants", "deposit_paid", "REAL DEFAULT 0")
        ensure_column(self.conn, "tenants", "move_out_reason", "TEXT DEFAULT ''")
        ensure_column(self.conn, "payments", "note", "TEXT DEFAULT ''")
        ensure_column(self.conn, "maintenance", "fee", "REAL DEFAULT 0")
        ensure_column(self.conn, "maintenance", "staff", "TEXT DEFAULT ''")
        ensure_column(self.conn, "staff", "status", "TEXT DEFAULT 'Active'")

        self.seed_defaults()

    def seed_defaults(self):
        c = self.conn.cursor()

        # Default admin user
        c.execute("SELECT COUNT(*) as c FROM users")
        if c.fetchone()["c"] == 0:
            c.execute("INSERT INTO users (username,password) VALUES (?,?)", ("admin", "admin"))

        # Units: exactly 50 units
        c.execute("SELECT COUNT(*) as c FROM units")
        if c.fetchone()["c"] == 0:
            # 20 Solo S01–S20
            for i in range(1, 21):
                code = f"S{i:02d}"
                c.execute(
                    "INSERT INTO units (unit_code, unit_type, price, status, capacity) VALUES (?,?,?,?,?)",
                    (code, "Solo", 4500.0, "Vacant", 1)
                )
            # 25 Family F01–F25
            for i in range(1, 26):
                code = f"F{i:02d}"
                c.execute(
                    "INSERT INTO units (unit_code, unit_type, price, status, capacity) VALUES (?,?,?,?,?)",
                    (code, "Family", 9000.0, "Vacant", 1)
                )
            # 5 Dorm D01–D05
            for i in range(1, 6):
                code = f"D{i:02d}"
                c.execute(
                    "INSERT INTO units (unit_code, unit_type, price, status, capacity) VALUES (?,?,?,?,?)",
                    (code, "Dorm", 8000.0, "Vacant", DORM_DEFAULT_CAPACITY)
                )

        self.conn.commit()

    def query(self, sql, params=()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()

    def execute(self, sql, params=()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        self.conn.commit()
        return cur

    def close(self):
        self.conn.close()


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
        self.db.execute("""
        INSERT INTO payments (tenant_id, rent, electricity, water, total, date_paid, status, note)
        VALUES (?,?,?,?,?,?,?,?)
        """, (tenant_id, rent, electricity, water, total, date_paid, status, note))

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


# ===============================
# DIALOGS
# ===============================

class LoginDialog(ctk.CTkToplevel):
    def __init__(self, parent, db: Database):
        super().__init__(parent)
        self.db = db
        self.success = False
        self.title("Login")
        self.geometry("300x150")
        self.resizable(False, False)
        self.build_ui()
        self.transient(parent)
        self.grab_set()

    def build_ui(self):
        frm = ctk.CTkFrame(self, corner_radius=10)
        frm.pack(fill="both", expand=True, padx=8, pady=8)

        heading = ctk.CTkLabel(frm, text="Admin Login", font=ctk.CTkFont(size=14, weight="bold"))
        heading.grid(row=0, column=0, columnspan=2, pady=(0, 8))

        ctk.CTkLabel(frm, text="Username").grid(row=1, column=0, sticky="w", padx=4, pady=2)
        self.user_e = ctk.CTkEntry(frm, width=180)
        self.user_e.grid(row=1, column=1, padx=4, pady=2)

        ctk.CTkLabel(frm, text="Password").grid(row=2, column=0, sticky="w", padx=4, pady=2)
        self.pw_e = ctk.CTkEntry(frm, width=180, show="*")
        self.pw_e.grid(row=2, column=1, padx=4, pady=2)

        btn_fr = ctk.CTkFrame(frm, fg_color="transparent")
        btn_fr.grid(row=3, column=0, columnspan=2, pady=8)

        ctk.CTkButton(btn_fr, text="Login", width=80, command=self.on_login).pack(side="left", padx=4)
        ctk.CTkButton(btn_fr, text="Exit", width=80, fg_color="#883333", command=self.destroy).pack(side="left", padx=4)

    def on_login(self):
        u = self.user_e.get().strip()
        p = self.pw_e.get().strip()
        if not u or not p:
            messagebox.showwarning("Login", "Enter username and password.", parent=self)
            return
        rows = self.db.query("SELECT * FROM users WHERE username=? AND password=?", (u, p))
        if rows:
            self.success = True
            self.destroy()
        else:
            messagebox.showerror("Login", "Invalid credentials.", parent=self)


class ChangePasswordDialog(ctk.CTkToplevel):
    def __init__(self, parent, db: Database):
        super().__init__(parent)
        self.db = db
        self.saved = False
        self.title("Change Password")
        self.geometry("360x230")
        self.build_ui()
        self.transient(parent)
        self.grab_set()

    def build_ui(self):
        frm = ctk.CTkFrame(self, corner_radius=12)
        frm.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(frm, text="Username").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.user_e = ctk.CTkEntry(frm, width=220)
        self.user_e.grid(row=0, column=1, padx=6, pady=4)

        ctk.CTkLabel(frm, text="Current Password").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self.cur_e = ctk.CTkEntry(frm, width=220, show="*")
        self.cur_e.grid(row=1, column=1, padx=6, pady=4)

        ctk.CTkLabel(frm, text="New Password").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        self.new_e = ctk.CTkEntry(frm, width=220, show="*")
        self.new_e.grid(row=2, column=1, padx=6, pady=4)

        ctk.CTkLabel(frm, text="Confirm New").grid(row=3, column=0, sticky="w", padx=6, pady=4)
        self.confirm_e = ctk.CTkEntry(frm, width=220, show="*")
        self.confirm_e.grid(row=3, column=1, padx=6, pady=4)

        btn_fr = ctk.CTkFrame(frm, fg_color="transparent")
        btn_fr.grid(row=4, column=0, columnspan=2, pady=10)

        ctk.CTkButton(btn_fr, text="Change", width=110, command=self.on_change).pack(side="left", padx=6)
        ctk.CTkButton(btn_fr, text="Cancel", width=90, fg_color="#555555", command=self.destroy).pack(side="left", padx=6)

    def on_change(self):
        u = self.user_e.get().strip()
        cur = self.cur_e.get().strip()
        new = self.new_e.get().strip()
        conf = self.confirm_e.get().strip()

        if not u or not cur or not new:
            messagebox.showwarning("Input", "All fields are required.", parent=self)
            return
        if new != conf:
            messagebox.showwarning("Input", "New passwords do not match.", parent=self)
            return

        rows = self.db.query("SELECT * FROM users WHERE username=? AND password=?", (u, cur))
        if not rows:
            messagebox.showerror("User", "Invalid username or current password.", parent=self)
            return

        self.db.execute("UPDATE users SET password=? WHERE username=?", (new, u))
        messagebox.showinfo("Saved", "Password changed.", parent=self)
        self.saved = True
        self.destroy()


class PolicyDialog(ctk.CTkToplevel):
    def __init__(self, parent, text=""):
        super().__init__(parent)
        self.title("Apartment Policy - Accept to Continue")
        self.geometry("520x260")
        self.accepted = False
        self.transient(parent)
        self.grab_set()

        frm = ctk.CTkFrame(self, corner_radius=12)
        frm.pack(fill="both", expand=True, padx=12, pady=10)

        hdr = ctk.CTkLabel(frm, text="Apartment Rules & Policy", font=ctk.CTkFont(size=14, weight="bold"))
        hdr.pack(anchor="w", pady=(2, 6))

        body_fr = ctk.CTkFrame(frm, corner_radius=8)
        body_fr.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        policy_text = text or (
            "1. Rent is due every month.\n"
            "2. Utilities must be paid on time.\n"
            "3. No illegal activities inside the premises.\n"
            "4. Respect dormmates and neighbors.\n"
            "5. Damage to property may incur maintenance fees."
        )
        for line in [ln.strip() for ln in policy_text.splitlines() if ln.strip()]:
            ctk.CTkLabel(
                body_fr,
                text=f"• {line}",
                anchor="w",
                justify="left",
                wraplength=480,
                font=ctk.CTkFont(size=11),
            ).pack(fill="x", padx=8, pady=1)

        self.accept_var = tk.BooleanVar(value=False)
        chk = ctk.CTkCheckBox(
            frm,
            text="I have read and accept the Policy & Terms",
            variable=self.accept_var,
            command=self.on_toggle
        )
        chk.pack(pady=(6, 4), padx=6, anchor="w")

        btn_fr = ctk.CTkFrame(frm, fg_color="transparent")
        btn_fr.pack(pady=(2, 8))

        self.accept_btn = ctk.CTkButton(btn_fr, text="Accept", width=110, command=self.on_accept, state="disabled")
        self.accept_btn.pack(side="right", padx=6)

        ctk.CTkButton(btn_fr, text="Decline", width=110, fg_color="#883333", command=self.on_decline).pack(
            side="right", padx=6
        )

    def on_toggle(self):
        self.accept_btn.configure(state="normal" if self.accept_var.get() else "disabled")

    def on_accept(self):
        self.accepted = True
        self.destroy()

    def on_decline(self):
        self.accepted = False
        self.destroy()


class TenantDialog(ctk.CTkToplevel):
    def __init__(self, parent, unit_model: UnitModel, tenant_model: TenantModel, tenant=None):
        super().__init__(parent)
        self.parent = parent
        self.unit_model = unit_model
        self.tenant_model = tenant_model
        self.tenant = tenant
        self.saved = False
        self.result = {}

        self.title("Tenant")
        self.geometry("650x520")
        self.resizable(False, False)
        self.build_ui()
        if self.tenant:
            self.load_data()

        self.transient(parent)
        self.grab_set()

    def build_ui(self):
        frm = ctk.CTkFrame(self, corner_radius=12)
        frm.pack(fill="both", expand=True, padx=16, pady=16)

        font_label = ctk.CTkFont(size=13)
        row = 0

        ctk.CTkLabel(frm, text="Full Name", font=font_label).grid(row=row, column=0, sticky="w", padx=8, pady=4)
        self.name_e = ctk.CTkEntry(frm, width=260)
        self.name_e.grid(row=row, column=1, sticky="w", padx=8, pady=4)

        row += 1
        ctk.CTkLabel(frm, text="Contact No.", font=font_label).grid(row=row, column=0, sticky="w", padx=8, pady=4)
        self.contact_e = ctk.CTkEntry(frm, width=260)
        self.contact_e.grid(row=row, column=1, sticky="w", padx=8, pady=4)

        row += 1
        ctk.CTkLabel(frm, text="Unit", font=font_label).grid(row=row, column=0, sticky="w", padx=8, pady=4)
        units = self.unit_model.all()
        self.unit_map = {}
        unit_vals = []
        for u in units:
            label = f"{u['unit_code']} ({u['unit_type']}) - ₱{u['price']:.0f}"
            self.unit_map[label] = u
            unit_vals.append(label)
        self.unit_cmb = ctk.CTkComboBox(frm, values=unit_vals, width=260)
        if unit_vals:
            self.unit_cmb.set(unit_vals[0])
        self.unit_cmb.grid(row=row, column=1, sticky="w", padx=8, pady=4)
        self.unit_cmb.configure(command=lambda _v: self.update_dorm_info())

        row += 1
        ctk.CTkLabel(frm, text="Tenant Type", font=font_label).grid(row=row, column=0, sticky="w", padx=8, pady=4)
        self.type_cmb = ctk.CTkComboBox(frm, values=["Solo", "Family", "Dorm"], width=160)
        self.type_cmb.set("Solo")
        self.type_cmb.grid(row=row, column=1, sticky="w", padx=8, pady=4)
        self.type_cmb.configure(command=lambda _v: self.update_dorm_info())

        row += 1
        ctk.CTkLabel(frm, text="Move-in (YYYY-MM-DD)", font=font_label).grid(row=row, column=0, sticky="w", padx=8, pady=4)
        self.movein_e = ctk.CTkEntry(frm, width=160)
        self.movein_e.insert(0, datetime.date.today().isoformat())
        self.movein_e.grid(row=row, column=1, sticky="w", padx=8, pady=4)

        # Roommates label (for dorm)
        row += 1
        self.roommates_label = ctk.CTkLabel(
            frm,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray80",
            wraplength=420,
            justify="left"
        )
        self.roommates_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=8, pady=(2, 8))

        # Guardian block
        row += 1
        guardian_frame = ctk.CTkFrame(frm, corner_radius=8)
        guardian_frame.grid(row=row, column=0, columnspan=2, pady=(6, 6), padx=4, sticky="ew")

        ctk.CTkLabel(
            guardian_frame,
            text="Guardian (Required for ALL tenants)",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=6, pady=(4, 2))

        ctk.CTkLabel(guardian_frame, text="Guardian Name").grid(row=1, column=0, sticky="w", padx=6, pady=2)
        self.guardian_name_e = ctk.CTkEntry(guardian_frame, width=260)
        self.guardian_name_e.grid(row=1, column=1, sticky="w", padx=6, pady=2)

        ctk.CTkLabel(guardian_frame, text="Guardian Contact").grid(row=2, column=0, sticky="w", padx=6, pady=2)
        self.guardian_contact_e = ctk.CTkEntry(guardian_frame, width=260)
        self.guardian_contact_e.grid(row=2, column=1, sticky="w", padx=6, pady=2)

        ctk.CTkLabel(guardian_frame, text="Relation").grid(row=3, column=0, sticky="w", padx=6, pady=2)
        self.guardian_relation_e = ctk.CTkEntry(guardian_frame, width=260)
        self.guardian_relation_e.grid(row=3, column=1, sticky="w", padx=6, pady=2)

        ctk.CTkLabel(guardian_frame, text="Emergency Contact").grid(row=4, column=0, sticky="w", padx=6, pady=2)
        self.emer_e = ctk.CTkEntry(guardian_frame, width=260)
        self.emer_e.grid(row=4, column=1, sticky="w", padx=6, pady=2)

        # Advance / Deposit
        row += 1
        money_frame = ctk.CTkFrame(frm, corner_radius=8)
        money_frame.grid(row=row, column=0, columnspan=2, pady=(8, 10), padx=4, sticky="ew")

        ctk.CTkLabel(money_frame, text="Advance Paid").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.advance_e = ctk.CTkEntry(money_frame, width=120)
        self.advance_e.insert(0, "0")
        self.advance_e.grid(row=0, column=1, sticky="w", padx=6, pady=4)

        ctk.CTkLabel(money_frame, text="Deposit Paid").grid(row=0, column=2, sticky="w", padx=6, pady=4)
        self.deposit_e = ctk.CTkEntry(money_frame, width=120)
        self.deposit_e.insert(0, "0")
        self.deposit_e.grid(row=0, column=3, sticky="w", padx=6, pady=4)

        self.adv_hint = ctk.CTkLabel(money_frame, text="", font=ctk.CTkFont(size=11), text_color="gray80")
        self.adv_hint.grid(row=1, column=0, columnspan=2, sticky="w", padx=6, pady=(0, 4))

        self.dep_hint = ctk.CTkLabel(money_frame, text="", font=ctk.CTkFont(size=11), text_color="gray80")
        self.dep_hint.grid(row=1, column=2, columnspan=2, sticky="w", padx=6, pady=(0, 4))

        # Buttons
        row += 1
        btn_frame = ctk.CTkFrame(frm, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=2, pady=10)

        ctk.CTkButton(btn_frame, text="Save", width=140, command=self.on_save).pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Cancel", width=120, fg_color="#555555", command=self.destroy).pack(
            side="left", padx=4
        )

    def load_data(self):
        t = self.tenant
        self.name_e.insert(0, t["name"])
        if t["contact"]:
            self.contact_e.insert(0, t["contact"])
        if t["move_in"]:
            self.movein_e.delete(0, tk.END)
            self.movein_e.insert(0, t["move_in"])
        if t["tenant_type"]:
            self.type_cmb.set(t["tenant_type"])

        if t["guardian_name"]:
            self.guardian_name_e.insert(0, t["guardian_name"])
        if t["guardian_contact"]:
            self.guardian_contact_e.insert(0, t["guardian_contact"])
        if t["guardian_relation"]:
            self.guardian_relation_e.insert(0, t["guardian_relation"])
        if t["emergency_contact"]:
            self.emer_e.insert(0, t["emergency_contact"])

        self.advance_e.delete(0, tk.END)
        self.advance_e.insert(0, str(t["advance_paid"] or 0))
        self.deposit_e.delete(0, tk.END)
        self.deposit_e.insert(0, str(t["deposit_paid"] or 0))

        if t["unit_id"]:
            # try to set unit combo based on unit_id
            for label, u in self.unit_map.items():
                if u["unit_id"] == t["unit_id"]:
                    self.unit_cmb.set(label)
                    break

        self.update_dorm_info()

    def compute_dorm_share(self):
        unit_label = self.unit_cmb.get()
        unit = self.unit_map.get(unit_label)
        if not unit:
            return 0.0
        price = unit["price"] or 0.0
        cap = unit["capacity"] or DORM_DEFAULT_CAPACITY
        cap = min(cap, DORM_DEFAULT_CAPACITY)
        return (price / cap) if cap else 0.0

    def update_dorm_info(self):
        # roommates label + hints
        unit_label = self.unit_cmb.get()
        unit = self.unit_map.get(unit_label)
        ttype = self.type_cmb.get().strip().lower()

        # Roommates (only for dorm)
        if unit and unit["unit_type"].lower() == "dorm" and ttype == "dorm":
            tenants = self.tenant_model.tenants_in_unit(unit["unit_id"])
            names = []
            for t in tenants:
                if self.tenant and t["tenant_id"] == self.tenant["tenant_id"]:
                    continue
                names.append(f"[{t['tenant_id']}] {t['name']}")
            if names:
                self.roommates_label.configure(text="Current roommates: " + ", ".join(names))
            else:
                self.roommates_label.configure(text="Current roommates: (None)")
        else:
            self.roommates_label.configure(text="")

        # Advance / deposit suggestion for dorm
        if unit and unit["unit_type"].lower() == "dorm" and ttype == "dorm":
            share = self.compute_dorm_share()
            if share:
                txt = f"Suggested per-tenant advance/deposit: ₱{share:.2f}"
                self.adv_hint.configure(text=txt)
                self.dep_hint.configure(text=txt)
        else:
            self.adv_hint.configure(text="")
            self.dep_hint.configure(text="")

    def on_save(self):
        name = self.name_e.get().strip()
        contact = self.contact_e.get().strip()
        tenant_type = self.type_cmb.get().strip()
        move_in = self.movein_e.get().strip() or datetime.date.today().isoformat()

        if not name or len(name.split()) < 2:
            messagebox.showwarning("Input", "Please enter full name (first + last).", parent=self)
            return

        if contact and not any(ch.isdigit() for ch in contact):
            messagebox.showwarning("Input", "Contact number should contain digits.", parent=self)
            return

        try:
            advance = float(self.advance_e.get().strip() or 0)
            deposit = float(self.deposit_e.get().strip() or 0)
        except ValueError:
            messagebox.showwarning("Input", "Advance / Deposit must be numeric.", parent=self)
            return

        unit_label = self.unit_cmb.get()
        unit = self.unit_map.get(unit_label)
        if not unit:
            messagebox.showwarning("Unit", "Please select a unit.", parent=self)
            return

        unit_id = unit["unit_id"]

        guardian_name = self.guardian_name_e.get().strip()
        guardian_contact = self.guardian_contact_e.get().strip()
        guardian_rel = self.guardian_relation_e.get().strip()
        emer = self.emer_e.get().strip()

        # Guardian REQUIRED for ALL tenants
        if not guardian_name or len(guardian_name.split()) < 2:
            messagebox.showwarning("Input", "Guardian full name is required for all tenants.", parent=self)
            return
        if not guardian_contact or not guardian_contact.isdigit():
            messagebox.showwarning("Input", "Guardian contact is required and must contain digits only.", parent=self)
            return

        # Dorm capacity & 1 month advance rule
        if tenant_type.lower() == "dorm":
            cap = unit["capacity"] or DORM_DEFAULT_CAPACITY
            cap = min(cap, DORM_DEFAULT_CAPACITY)
            existing = self.tenant_model.tenants_in_unit(unit_id)
            existing_count = len(existing)

            # if editing and same unit, ignore self
            if self.tenant and self.tenant["unit_id"] == unit_id:
                existing_count -= 1

            if existing_count >= cap:
                messagebox.showwarning(
                    "Capacity",
                    f"This dorm room is already full ({existing_count}/{cap}).",
                    parent=self
                )
                return

            share = self.compute_dorm_share()
            if share and advance < share:
                messagebox.showwarning(
                    "Advance Required",
                    f"Dorm tenant must pay at least 1 month advance share.\n"
                    f"Per-tenant share: ₱{share:.2f}\n"
                    f"Advance entered: ₱{advance:.2f}",
                    parent=self
                )
                return

        self.result = {
            "name": name,
            "contact": contact,
            "unit_id": unit_id,
            "tenant_type": tenant_type,
            "move_in": move_in,
            "move_out": None,
            "status": "Active",
            "guardian_name": guardian_name,
            "guardian_contact": guardian_contact,
            "guardian_relation": guardian_rel,
            "emergency_contact": emer,
            "advance_paid": advance,
            "deposit_paid": deposit,
            "move_out_reason": "",
        }
        self.saved = True
        self.destroy()


class MoveOutDialog(ctk.CTkToplevel):
    def __init__(self, parent, tenant_name):
        super().__init__(parent)
        self.saved = False
        self.reason = ""
        self.date = datetime.date.today().isoformat()

        self.title("Terminate / Move-out Tenant")
        self.geometry("480x260")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        frm = ctk.CTkFrame(self, corner_radius=12)
        frm.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(
            frm,
            text=f"Move Out: {tenant_name}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(4, 10))

        ctk.CTkLabel(frm, text="Select Reason:").pack(anchor="w", padx=10, pady=(4, 2))

        reasons = [
            "Found cheaper accommodation",
            "Moving to another city",
            "Bought own house/condo",
            "Job relocation",
            "Family reasons",
            "Unsatisfied with facilities",
            "Financial difficulties",
            "End of contract",
            "Other (specify below)"
        ]

        self.reason_var = tk.StringVar(value=reasons[0])
        self.reason_cmb = ctk.CTkComboBox(frm, values=reasons, variable=self.reason_var, width=420, state="readonly")
        self.reason_cmb.pack(padx=10, pady=(0, 10))

        ctk.CTkLabel(frm, text="Additional Details (optional):").pack(anchor="w", padx=10, pady=(4, 2))
        self.details_e = ctk.CTkEntry(frm, width=420, placeholder_text="Enter additional details")
        self.details_e.pack(padx=10, pady=(0, 10))

        btn_frame = ctk.CTkFrame(frm, fg_color="transparent")
        btn_frame.pack(pady=6)

        ctk.CTkButton(btn_frame, text="Confirm Move Out", width=150, command=self.on_save).pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="Cancel", width=120, fg_color="#555555", command=self.destroy).pack(
            side="left", padx=6
        )

    def on_save(self):
        selected = self.reason_var.get()
        details = self.details_e.get().strip()

        if selected == "Other (specify below)" and not details:
            messagebox.showwarning("Input Required", "Please provide details for 'Other' reason.", parent=self)
            return

        self.reason = f"{selected} - {details}" if details else selected
        self.saved = True
        self.destroy()


class PaymentDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.saved = False
        self.result = {}
        self.title("New Payment")
        self.geometry("400x320")
        self.build_ui()
        self.transient(parent)
        self.grab_set()

    def build_ui(self):
        frm = ctk.CTkFrame(self, corner_radius=12)
        frm.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(frm, text="Tenant ID").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        self.tid_e = ctk.CTkEntry(frm, width=160)
        self.tid_e.grid(row=0, column=1, padx=8, pady=4)

        ctk.CTkLabel(frm, text="Rent").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        self.rent_e = ctk.CTkEntry(frm, width=160)
        self.rent_e.grid(row=1, column=1, padx=8, pady=4)

        ctk.CTkLabel(frm, text="Electricity").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        self.elec_e = ctk.CTkEntry(frm, width=160)
        self.elec_e.grid(row=2, column=1, padx=8, pady=4)

        ctk.CTkLabel(frm, text="Water").grid(row=3, column=0, sticky="w", padx=8, pady=4)
        self.water_e = ctk.CTkEntry(frm, width=160)
        self.water_e.grid(row=3, column=1, padx=8, pady=4)

        ctk.CTkLabel(frm, text="Status").grid(row=4, column=0, sticky="w", padx=8, pady=4)
        self.status_cmb = ctk.CTkComboBox(frm, values=["Paid", "Overdue", "Refund", "Due"], width=160)
        self.status_cmb.set("Paid")
        self.status_cmb.grid(row=4, column=1, padx=8, pady=4)

        ctk.CTkLabel(frm, text="Note").grid(row=5, column=0, sticky="w", padx=8, pady=4)
        self.note_e = ctk.CTkEntry(frm, width=200)
        self.note_e.grid(row=5, column=1, padx=8, pady=4)

        btn_frame = ctk.CTkFrame(frm, fg_color="transparent")
        btn_frame.grid(row=6, column=0, columnspan=2, pady=12)

        ctk.CTkButton(btn_frame, text="Save", width=120, command=self.on_save).pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="Cancel", width=100, fg_color="#555555", command=self.destroy).pack(
            side="left", padx=4
        )

    def on_save(self):
        try:
            tenant_id = int(self.tid_e.get().strip())
        except ValueError:
            messagebox.showwarning("Input", "Tenant ID must be numeric.", parent=self)
            return

        try:
            rent = float(self.rent_e.get().strip() or 0)
            elec = float(self.elec_e.get().strip() or 0)
            water = float(self.water_e.get().strip() or 0)
        except ValueError:
            messagebox.showwarning("Input", "Amounts must be numeric.", parent=self)
            return

        status = self.status_cmb.get()
        note = self.note_e.get().strip()

        self.result = {
            "tenant_id": tenant_id,
            "rent": rent,
            "electricity": elec,
            "water": water,
            "status": status,
            "note": note
        }
        self.saved = True
        self.destroy()


class PaymentEditDialog(ctk.CTkToplevel):
    def __init__(self, parent, payment_row):
        super().__init__(parent)
        self.saved = False
        self.result = {}
        self.payment_row = payment_row

        self.title(f"Edit Payment #{payment_row['payment_id']}")
        self.geometry("400x320")
        self.build_ui()
        self.transient(parent)
        self.grab_set()

    def build_ui(self):
        frm = ctk.CTkFrame(self, corner_radius=12)
        frm.pack(fill="both", expand=True, padx=16, pady=16)

        tenant_label = f"[{self.payment_row['tenant_id']}] {self.payment_row['name'] or 'Unknown'}"
        ctk.CTkLabel(frm, text="Tenant").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        ctk.CTkLabel(frm, text=tenant_label).grid(row=0, column=1, sticky="w", padx=8, pady=4)

        ctk.CTkLabel(frm, text="Rent").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        self.rent_e = ctk.CTkEntry(frm, width=160)
        self.rent_e.insert(0, str(self.payment_row["rent"] or 0))
        self.rent_e.grid(row=1, column=1, padx=8, pady=4)

        ctk.CTkLabel(frm, text="Electricity").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        self.elec_e = ctk.CTkEntry(frm, width=160)
        self.elec_e.insert(0, str(self.payment_row["electricity"] or 0))
        self.elec_e.grid(row=2, column=1, padx=8, pady=4)

        ctk.CTkLabel(frm, text="Water").grid(row=3, column=0, sticky="w", padx=8, pady=4)
        self.water_e = ctk.CTkEntry(frm, width=160)
        self.water_e.insert(0, str(self.payment_row["water"] or 0))
        self.water_e.grid(row=3, column=1, padx=8, pady=4)

        ctk.CTkLabel(frm, text="Status").grid(row=4, column=0, sticky="w", padx=8, pady=4)
        self.status_cmb = ctk.CTkComboBox(frm, values=["Paid", "Overdue", "Refund", "Due"], width=160)
        current_status = self.payment_row["status"] or "Paid"
        self.status_cmb.set(current_status)
        self.status_cmb.grid(row=4, column=1, padx=8, pady=4)

        ctk.CTkLabel(frm, text="Note").grid(row=5, column=0, sticky="w", padx=8, pady=4)
        self.note_e = ctk.CTkEntry(frm, width=220)
        if self.payment_row["note"]:
            self.note_e.insert(0, self.payment_row["note"])
        self.note_e.grid(row=5, column=1, padx=8, pady=4)

        btn_frame = ctk.CTkFrame(frm, fg_color="transparent")
        btn_frame.grid(row=6, column=0, columnspan=2, pady=12)

        ctk.CTkButton(btn_frame, text="Save", width=120, command=self.on_save).pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="Cancel", width=100, fg_color="#555555", command=self.destroy).pack(
            side="left", padx=4
        )

    def on_save(self):
        try:
            rent = float(self.rent_e.get().strip() or 0)
            elec = float(self.elec_e.get().strip() or 0)
            water = float(self.water_e.get().strip() or 0)
        except ValueError:
            messagebox.showwarning("Input", "Amounts must be numeric.", parent=self)
            return

        status = self.status_cmb.get()
        note = self.note_e.get().strip()

        self.result = {
            "rent": rent,
            "electricity": elec,
            "water": water,
            "status": status,
            "note": note
        }
        self.saved = True
        self.destroy()


class MaintenanceDialog(ctk.CTkToplevel):
    def __init__(self, parent, staff_model: StaffModel):
        super().__init__(parent)
        self.staff_model = staff_model
        self.saved = False
        self.result = {}

        self.title("Maintenance Request")
        self.geometry("460x320")
        self.build_ui()
        self.transient(parent)
        self.grab_set()

    def build_ui(self):
        frm = ctk.CTkFrame(self, corner_radius=12)
        frm.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(frm, text="Tenant ID (optional)").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        self.tid_e = ctk.CTkEntry(frm, width=160)
        self.tid_e.grid(row=0, column=1, padx=8, pady=4)

        ctk.CTkLabel(frm, text="Description").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        self.desc_e = ctk.CTkEntry(frm, width=260)
        self.desc_e.grid(row=1, column=1, padx=8, pady=4)

        ctk.CTkLabel(frm, text="Priority").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        self.prio_cmb = ctk.CTkComboBox(frm, values=["Low", "Medium", "High"], width=120)
        self.prio_cmb.set("Low")
        self.prio_cmb.grid(row=2, column=1, padx=8, pady=4, sticky="w")

        ctk.CTkLabel(frm, text="Fee").grid(row=3, column=0, sticky="w", padx=8, pady=4)
        self.fee_e = ctk.CTkEntry(frm, width=120)
        self.fee_e.insert(0, "0")
        self.fee_e.grid(row=3, column=1, padx=8, pady=4, sticky="w")

        ctk.CTkLabel(frm, text="Assigned Staff").grid(row=4, column=0, sticky="w", padx=8, pady=4)
        staff_names = self.staff_model.active_names() or [""]
        self.staff_cmb = ctk.CTkComboBox(frm, values=staff_names, width=200)
        self.staff_cmb.set(staff_names[0] if staff_names else "")
        self.staff_cmb.grid(row=4, column=1, padx=8, pady=4, sticky="w")

        btn_frame = ctk.CTkFrame(frm, fg_color="transparent")
        btn_frame.grid(row=5, column=0, columnspan=2, pady=12)

        ctk.CTkButton(btn_frame, text="Submit", width=120, command=self.on_save).pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="Cancel", width=100, fg_color="#555555", command=self.destroy).pack(
            side="left", padx=4
        )

    def on_save(self):
        tid_str = self.tid_e.get().strip()
        tenant_id = None
        if tid_str:
            if not tid_str.isdigit():
                messagebox.showwarning("Input", "Tenant ID must be numeric.", parent=self)
                return
            tenant_id = int(tid_str)

        desc = self.desc_e.get().strip()
        if not desc:
            messagebox.showwarning("Input", "Description is required.", parent=self)
            return

        try:
            fee = float(self.fee_e.get().strip() or 0)
        except ValueError:
            messagebox.showwarning("Input", "Fee must be numeric.", parent=self)
            return

        prio = self.prio_cmb.get()
        staff = self.staff_cmb.get().strip()

        self.result = {
            "tenant_id": tenant_id,
            "description": desc,
            "priority": prio,
            "fee": fee,
            "staff": staff
        }
        self.saved = True
        self.destroy()


class StaffDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.saved = False
        self.result = {}

        self.title("Staff")
        self.geometry("380x220")
        self.build_ui()
        self.transient(parent)
        self.grab_set()

    def build_ui(self):
        frm = ctk.CTkFrame(self, corner_radius=12)
        frm.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(frm, text="Name").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        self.name_e = ctk.CTkEntry(frm, width=220)
        self.name_e.grid(row=0, column=1, padx=8, pady=4)

        ctk.CTkLabel(frm, text="Contact").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        self.contact_e = ctk.CTkEntry(frm, width=220)
        self.contact_e.grid(row=1, column=1, padx=8, pady=4)

        ctk.CTkLabel(frm, text="Role").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        self.role_e = ctk.CTkEntry(frm, width=220)
        self.role_e.grid(row=2, column=1, padx=8, pady=4)

        btn_frame = ctk.CTkFrame(frm, fg_color="transparent")
        btn_frame.grid(row=3, column=0, columnspan=2, pady=12)

        ctk.CTkButton(btn_frame, text="Save", width=120, command=self.on_save).pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="Cancel", width=100, fg_color="#555555", command=self.destroy).pack(
            side="left", padx=4
        )

    def on_save(self):
        name = self.name_e.get().strip()
        if not name:
            messagebox.showwarning("Input", "Name is required.", parent=self)
            return

        contact = self.contact_e.get().strip()
        role = self.role_e.get().strip()

        self.result = {
            "name": name,
            "contact": contact,
            "role": role,
            "status": "Active"
        }
        self.saved = True
        self.destroy()


# ===============================
# MAIN APP
# ===============================

class MainApp(ctk.CTk):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.unit_model = UnitModel(db)
        self.tenant_model = TenantModel(db)
        self.payment_model = PaymentModel(db)
        self.maintenance_model = MaintenanceModel(db)
        self.staff_model = StaffModel(db)
        self.logout_requested = False
        self.current_view = None

        self.title("Apartment Billing System")
        self.geometry("1280x720")
        self.minsize(1100, 640)

        self.build_layout()
        self.show_dashboard()

    def build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ttk style for treeview
        try:
            style = ttk.Style()
            style.configure("Treeview", font=("Segoe UI", 11))
            style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))
        except Exception:
            pass

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(12, weight=1)

        title = ctk.CTkLabel(
            self.sidebar,
            text="APARTMENT BILLING SYSTEM",
            font=ctk.CTkFont(size=18, weight="bold"),
            wraplength=220,
            justify="left"
        )
        title.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="w")

        subt = ctk.CTkLabel(self.sidebar, text="Main Menu", text_color=("gray80", "gray70"))
        subt.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="w")

        btn_cfg = {
            "width": 210,
            "corner_radius": 8,
            "anchor": "w",
            "fg_color": "transparent",
            "border_width": 1,
            "border_color": "#2f6fff"
        }

        self.btn_dash = ctk.CTkButton(self.sidebar, text="Overview", command=self.show_dashboard, **btn_cfg)
        self.btn_dash.grid(row=2, column=0, padx=12, pady=3)

        self.btn_units = ctk.CTkButton(self.sidebar, text="Units", command=self.show_units, **btn_cfg)
        self.btn_units.grid(row=3, column=0, padx=12, pady=3)

        self.btn_tenants = ctk.CTkButton(self.sidebar, text="Tenants", command=self.show_tenants, **btn_cfg)
        self.btn_tenants.grid(row=4, column=0, padx=12, pady=3)

        self.btn_billing = ctk.CTkButton(self.sidebar, text="Billing", command=self.show_billing, **btn_cfg)
        self.btn_billing.grid(row=5, column=0, padx=12, pady=3)

        self.btn_maint = ctk.CTkButton(self.sidebar, text="Maintenance", command=self.show_maintenance, **btn_cfg)
        self.btn_maint.grid(row=6, column=0, padx=12, pady=3)

        self.btn_staff = ctk.CTkButton(self.sidebar, text="Staff", command=self.show_staff, **btn_cfg)
        self.btn_staff.grid(row=7, column=0, padx=12, pady=3)

        self.btn_recycle = ctk.CTkButton(self.sidebar, text="Recycle Bin", command=self.show_recycle_bin, **btn_cfg)
        self.btn_recycle.grid(row=8, column=0, padx=12, pady=3)

        self.btn_reports = ctk.CTkButton(self.sidebar, text="Reports", command=self.show_reports, **btn_cfg)
        self.btn_reports.grid(row=9, column=0, padx=12, pady=3)

        self.btn_policy = ctk.CTkButton(self.sidebar, text="Policy", command=self.show_policy, **btn_cfg)
        self.btn_policy.grid(row=10, column=0, padx=12, pady=3)

        self.btn_change_pw = ctk.CTkButton(self.sidebar, text="Change Password", command=self.change_password, **btn_cfg)
        self.btn_change_pw.grid(row=11, column=0, padx=12, pady=3)

        self.btn_logout = ctk.CTkButton(self.sidebar, text="Logout", command=self.logout, **btn_cfg)
        self.btn_logout.grid(row=13, column=0, padx=12, pady=8)

        footer = ctk.CTkLabel(
            self.sidebar,
            text="Default account:\nadmin / admin",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        footer.grid(row=12, column=0, padx=12, pady=8, sticky="sw")

        # Main content
        self.content = ctk.CTkFrame(self, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(1, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=0)

        self.header_label = ctk.CTkLabel(self.content, text="", font=ctk.CTkFont(size=18, weight="bold"))
        self.header_label.grid(row=0, column=0, sticky="w", padx=16, pady=(10, 0))

        self.refresh_btn = ctk.CTkButton(self.content, text="Refresh", width=110, command=self.refresh_current_view)
        self.refresh_btn.grid(row=0, column=1, sticky="e", padx=12, pady=(10, 0))

        self.body_frame = ctk.CTkFrame(self.content)
        self.body_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

    def clear_body(self, title):
        for w in self.body_frame.winfo_children():
            w.destroy()
        self.header_label.configure(text=title)

    def logout(self):
        if not messagebox.askyesno("Logout", "Are you sure you want to log out?", parent=self):
            return
        self.logout_requested = True
        self.destroy()

    def refresh_current_view(self):
        if self.current_view == "dashboard":
            self.show_dashboard()
        elif self.current_view == "units":
            self.show_units()
        elif self.current_view == "tenants":
            self.show_tenants()
        elif self.current_view == "billing":
            self.show_billing()
        elif self.current_view == "maintenance":
            self.show_maintenance()
        elif self.current_view == "staff":
            self.show_staff()
        elif self.current_view == "recycle":
            self.show_recycle_bin()
        elif self.current_view == "reports":
            self.show_reports()

    # =======================
    # DASHBOARD
    # =======================

    def show_dashboard(self):
        self.current_view = "dashboard"
        self.clear_body("Overview")
        frame = self.body_frame
        frame.grid_columnconfigure((0, 1, 2), weight=1)

        total_units = len(self.unit_model.all())
        active_tenants = len(self.tenant_model.active())
        vacants = self.db.query("SELECT COUNT(*) as c FROM units WHERE status='Vacant'")[0]["c"]

        income_30 = self.db.query(
            "SELECT SUM(total) as s FROM payments WHERE date_paid>=?",
            ((datetime.date.today() - datetime.timedelta(days=30)).isoformat(),)
        )[0]["s"] or 0.0

        total_req, pending_req = self.maintenance_model.counts()

        card_font = ctk.CTkFont(size=14, weight="bold")

        def make_card(col, row, title_text, value_text):
            card = ctk.CTkFrame(frame, corner_radius=12)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            ctk.CTkLabel(card, text=title_text, font=card_font).pack(anchor="w", padx=12, pady=(10, 2))
            ctk.CTkLabel(card, text=value_text, font=ctk.CTkFont(size=24, weight="bold")).pack(
                anchor="w", padx=12, pady=(0, 10)
            )

        make_card(0, 0, "Total Units", str(total_units))
        make_card(1, 0, "Active Tenants", str(active_tenants))
        make_card(2, 0, "Vacant Units", str(vacants))

        make_card(0, 1, "Income (last 30 days)", f"₱{income_30:.2f}")

        card5 = ctk.CTkFrame(frame, corner_radius=12)
        card5.grid(row=1, column=1, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(card5, text="Maintenance Requests", font=card_font).pack(anchor="w", padx=12, pady=(10, 2))
        ctk.CTkLabel(card5, text=f"Total: {total_req}", font=ctk.CTkFont(size=16)).pack(
            anchor="w", padx=12, pady=(0, 2)
        )
        ctk.CTkLabel(card5, text=f"Pending: {pending_req}", font=ctk.CTkFont(size=16)).pack(
            anchor="w", padx=12, pady=(0, 10)
        )

    # =======================
    # UNITS
    # =======================

    def show_units(self):
        self.current_view = "units"
        self.clear_body("Units")
        frame = self.body_frame
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(top, text="Filter Status:").pack(side="left", padx=(4, 4))
        self.unit_status_var = tk.StringVar(value="All")
        status_cmb = ctk.CTkComboBox(
            top,
            values=["All", "Vacant", "Occupied"],
            width=120,
            variable=self.unit_status_var,
            command=lambda _v=None: self.load_units()
        )
        status_cmb.pack(side="left", padx=(0, 8))

        self.units_tree = ttk.Treeview(
            frame,
            columns=("unit_id", "unit_code", "unit_type", "price", "status", "capacity", "tenants"),
            show="headings"
        )
        for col in ("unit_id", "unit_code", "unit_type", "price", "status", "capacity", "tenants"):
            self.units_tree.heading(col, text=col.title())
            self.units_tree.column(col, width=110)
        self.units_tree.grid(row=1, column=0, sticky="nsew")
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.units_tree.yview)
        self.units_tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=1, column=1, sticky="ns")

        self.load_units()

    def load_units(self):
        if not hasattr(self, "units_tree"):
            return
        for r in self.units_tree.get_children():
            self.units_tree.delete(r)

        status = getattr(self, "unit_status_var", None)
        status = status.get() if status is not None else "All"

        rows = self.unit_model.filter_by_status(status if status in ("Vacant", "Occupied") else None)
        for u in rows:
            tenant_list = ""
            if u["unit_type"].lower() == "dorm":
                # list tenants in dorm
                tenants = self.tenant_model.tenants_in_unit(u["unit_id"])
                if tenants:
                    tenant_list = ", ".join(f"[{t['tenant_id']}] {t['name']}" for t in tenants)
            self.units_tree.insert(
                "",
                tk.END,
                values=(
                    u["unit_id"],
                    u["unit_code"],
                    u["unit_type"],
                    f"₱{u['price']:.2f}",
                    u["status"],
                    u["capacity"],
                    tenant_list
                )
            )

    # =======================
    # TENANTS
    # =======================

    def show_tenants(self):
        self.current_view = "tenants"
        self.clear_body("Tenants")
        frame = self.body_frame
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew")

        ctk.CTkButton(top, text="Add Tenant", width=120, command=self.add_tenant).pack(side="left", padx=4)
        ctk.CTkButton(top, text="Edit Tenant", width=120, command=self.edit_tenant).pack(side="left", padx=4)
        ctk.CTkButton(top, text="Terminate Tenant", width=150, command=self.terminate_tenant).pack(
            side="left", padx=4
        )

        ctk.CTkLabel(top, text="Search:").pack(side="left", padx=(16, 4))
        self.tenant_search_var = tk.StringVar()
        search_e = ctk.CTkEntry(top, width=180, textvariable=self.tenant_search_var)
        search_e.pack(side="left", padx=4)
        ctk.CTkButton(top, text="Go", width=60, command=self.load_tenants).pack(side="left", padx=4)

        cols = (
            "tenant_id",
            "name",
            "contact",
            "unit_code",
            "tenant_type",
            "move_in",
            "status",
            "guardian_name",
            "advance_paid",
            "deposit_paid",
        )
        self.tenants_tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            self.tenants_tree.heading(c, text=c.replace("_", " ").title())
            self.tenants_tree.column(c, width=110)
        self.tenants_tree.grid(row=1, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tenants_tree.yview)
        self.tenants_tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=1, column=1, sticky="ns")

        self.load_tenants()

    def load_tenants(self):
        if not hasattr(self, "tenants_tree"):
            return
        for r in self.tenants_tree.get_children():
            self.tenants_tree.delete(r)

        query = self.tenant_search_var.get().strip() if hasattr(self, "tenant_search_var") else ""
        if query:
            rows = self.tenant_model.search_active(query)
        else:
            rows = self.tenant_model.active()

        for t in rows:
            self.tenants_tree.insert(
                "",
                tk.END,
                values=(
                    t["tenant_id"],
                    t["name"],
                    t["contact"] or "",
                    t["unit_code"] or "",
                    t["tenant_type"] or "",
                    t["move_in"] or "",
                    t["status"] or "",
                    t["guardian_name"] or "",
                    t["advance_paid"] or 0,
                    t["deposit_paid"] or 0,
                )
            )

    def get_selected_tenant_id(self):
        if not hasattr(self, "tenants_tree"):
            return None
        sel = self.tenants_tree.selection()
        if not sel:
            return None
        item = self.tenants_tree.item(sel[0])
        vals = item["values"]
        if not vals:
            return None
        try:
            return int(vals[0])
        except (TypeError, ValueError):
            return None

    def add_tenant(self):
        dlg = TenantDialog(self, self.unit_model, self.tenant_model)
        self.wait_window(dlg)
        if dlg.saved:
            data = dlg.result
            self.tenant_model.create(**data)
            # mark unit as occupied
            self.unit_model.update_status(data["unit_id"], "Occupied")
            self.load_tenants()
            messagebox.showinfo("Saved", "Tenant added.", parent=self)

    def edit_tenant(self):
        tid = self.get_selected_tenant_id()
        if not tid:
            messagebox.showwarning("Select", "Please select a tenant to edit.", parent=self)
            return

        tenant = self.tenant_model.get(tid)
        if not tenant:
            messagebox.showwarning("Not Found", "Tenant not found.", parent=self)
            return

        dlg = TenantDialog(self, self.unit_model, self.tenant_model, tenant=tenant)
        self.wait_window(dlg)
        if dlg.saved:
            data = dlg.result
            # if unit changed, update statuses
            old_unit_id = tenant["unit_id"]
            new_unit_id = data["unit_id"]
            self.tenant_model.update(tid, **data)
            if old_unit_id != new_unit_id:
                # old unit might become vacant
                if not self.tenant_model.tenants_in_unit(old_unit_id):
                    self.unit_model.update_status(old_unit_id, "Vacant")
                self.unit_model.update_status(new_unit_id, "Occupied")
            self.load_tenants()
            messagebox.showinfo("Saved", "Tenant updated.", parent=self)

    def terminate_tenant(self):
        tid = self.get_selected_tenant_id()
        if not tid:
            messagebox.showwarning("Select", "Please select a tenant to terminate.", parent=self)
            return

        tenant = self.tenant_model.get(tid)
        if not tenant:
            messagebox.showwarning("Not Found", "Tenant not found.", parent=self)
            return

        if tenant["status"] == "Terminated":
            messagebox.showinfo("Info", "Tenant is already terminated.", parent=self)
            return

        dlg = MoveOutDialog(self, tenant_name=tenant["name"])
        self.wait_window(dlg)
        if not dlg.saved:
            return

        move_out_date = datetime.date.today().isoformat()
        self.tenant_model.terminate(tid, move_out_date, dlg.reason)

        # free unit if no more active tenants
        if tenant["unit_id"]:
            if not self.tenant_model.tenants_in_unit(tenant["unit_id"]):
                self.unit_model.update_status(tenant["unit_id"], "Vacant")

        self.load_tenants()
        messagebox.showinfo("Terminated", "Tenant moved out / terminated.", parent=self)

    # =======================
    # BILLING
    # =======================

    def show_billing(self):
        self.current_view = "billing"
        self.clear_body("Billing")
        frame = self.body_frame
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew")

        ctk.CTkButton(top, text="New Payment", width=120, command=self.new_payment).pack(side="left", padx=4)
        ctk.CTkButton(top, text="Edit Payment", width=120, command=self.edit_payment).pack(side="left", padx=4)
        ctk.CTkButton(top, text="Generate Auto-Bills", width=160, command=self.generate_auto_bills).pack(
            side="left", padx=8
        )
        ctk.CTkButton(top, text="Export CSV", width=120, command=self.export_payments_csv).pack(side="left", padx=4)

        ctk.CTkLabel(top, text="Filter Type:").pack(side="left", padx=(16, 4))
        self.pay_type_var = tk.StringVar(value="All")
        self.pay_type_cmb = ctk.CTkComboBox(
            top,
            values=["All", "Solo", "Family", "Dorm"],
            width=120,
            variable=self.pay_type_var,
            command=lambda _v=None: self.load_payments()
        )
        self.pay_type_cmb.pack(side="left", padx=4)

        cols = ("payment_id", "tenant", "tenant_type", "rent", "electricity", "water", "total", "date_paid", "status", "note")
        self.pay_tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            self.pay_tree.heading(c, text=c.replace("_", " ").title())
            self.pay_tree.column(c, width=110)
        self.pay_tree.grid(row=1, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.pay_tree.yview)
        self.pay_tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=1, column=1, sticky="ns")

        try:
            self.pay_tree.tag_configure("overdue", foreground="red")
        except Exception:
            pass

        self.load_payments()

    def load_payments(self):
        if not hasattr(self, "pay_tree"):
            return
        for r in self.pay_tree.get_children():
            self.pay_tree.delete(r)

        selected_type = self.pay_type_var.get() if hasattr(self, "pay_type_var") else "All"
        for row in self.payment_model.all():
            ttype = (row["tenant_type"] or "").title()
            if selected_type != "All" and ttype.lower() != selected_type.lower():
                continue

            tags = ()
            st = (row["status"] or "").lower()
            if st in ("overdue", "due"):
                tags = ("overdue",)

            self.pay_tree.insert(
                "",
                tk.END,
                values=(
                    row["payment_id"],
                    row["name"] or "",
                    ttype,
                    row["rent"] or 0.0,
                    row["electricity"] or 0.0,
                    row["water"] or 0.0,
                    row["total"] or 0.0,
                    row["date_paid"] or "",
                    row["status"] or "",
                    row["note"] or "",
                ),
                tags=tags
            )

    def new_payment(self):
        dlg = PaymentDialog(self)
        self.wait_window(dlg)
        if dlg.saved:
            r = dlg.result
            self.payment_model.create(
                r["tenant_id"], r["rent"], r["electricity"], r["water"], r["status"], r["note"]
            )
            self.load_payments()
            messagebox.showinfo("Saved", "Payment recorded.", parent=self)

    def get_selected_payment_id(self):
        if not hasattr(self, "pay_tree"):
            return None
        sel = self.pay_tree.selection()
        if not sel:
            return None
        item = self.pay_tree.item(sel[0])
        vals = item["values"]
        if not vals:
            return None
        try:
            return int(vals[0])
        except (TypeError, ValueError):
            return None

    def edit_payment(self):
        payment_id = self.get_selected_payment_id()
        if not payment_id:
            messagebox.showwarning("Select", "Please select a payment to edit.", parent=self)
            return

        row = self.payment_model.get(payment_id)
        if not row:
            messagebox.showwarning("Not Found", "Payment record not found.", parent=self)
            return

        dlg = PaymentEditDialog(self, row)
        self.wait_window(dlg)
        if dlg.saved:
            r = dlg.result
            self.payment_model.update(
                payment_id,
                r["rent"],
                r["electricity"],
                r["water"],
                r["status"],
                r["note"],
            )
            self.load_payments()
            messagebox.showinfo("Updated", "Payment updated.", parent=self)

    def generate_auto_bills(self):
        today = datetime.date.today()
        month_label = today.strftime("%B %Y")
        note = f"Auto-bill {month_label}"

        active_tenants = self.tenant_model.active()
        created_count = 0

        for t in active_tenants:
            tenant_id = t["tenant_id"]
            if self.payment_model.invoice_exists_with_note(tenant_id, note):
                continue

            rent = t["room_price"] or 0.0
            ut = (t["tenant_type"] or "").strip().lower()
            if ut == "solo":
                elec, water = SOLO_ELEC, SOLO_WATER
            elif ut == "family":
                elec, water = FAMILY_ELEC, FAMILY_WATER
            elif ut == "dorm":
                elec, water = DORM_ELEC, DORM_WATER
            else:
                elec = water = 0.0

            self.payment_model.create_due(tenant_id, rent, elec, water, note=note)
            created_count += 1

        self.load_payments()
        messagebox.showinfo("Auto-Billing", f"Generated {created_count} new invoice(s).", parent=self)

    def export_payments_csv(self):
        rows = self.payment_model.all()
        if not rows:
            messagebox.showwarning("No Data", "No payments to export.", parent=self)
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Save payments CSV"
        )
        if not path:
            return

        import csv
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["payment_id", "tenant", "tenant_type", "rent", "electricity", "water",
                        "total", "date_paid", "status", "note"])
            for r in rows:
                w.writerow([
                    r["payment_id"],
                    r["name"] or "",
                    r["tenant_type"] or "",
                    r["rent"] or 0.0,
                    r["electricity"] or 0.0,
                    r["water"] or 0.0,
                    r["total"] or 0.0,
                    r["date_paid"] or "",
                    r["status"] or "",
                    r["note"] or "",
                ])
        messagebox.showinfo("Exported", f"Saved to {path}", parent=self)

    # =======================
    # MAINTENANCE
    # =======================

    def show_maintenance(self):
        self.current_view = "maintenance"
        self.clear_body("Maintenance")
        frame = self.body_frame
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew")

        ctk.CTkButton(top, text="New Request", width=120, command=self.new_maintenance).pack(side="left", padx=4)

        cols = ("request_id", "tenant_id", "tenant_name", "description", "priority", "date_requested", "status", "fee", "staff")
        self.maint_tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            self.maint_tree.heading(c, text=c.replace("_", " ").title())
            self.maint_tree.column(c, width=120)
        self.maint_tree.grid(row=1, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.maint_tree.yview)
        self.maint_tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=1, column=1, sticky="ns")

        self.load_maintenance()

    def load_maintenance(self):
        if not hasattr(self, "maint_tree"):
            return
        for r in self.maint_tree.get_children():
            self.maint_tree.delete(r)
        for m in self.maintenance_model.all():
            self.maint_tree.insert(
                "",
                tk.END,
                values=(
                    m["request_id"],
                    m["tenant_id"] or "",
                    m["tenant_name"] or "",
                    m["description"] or "",
                    m["priority"] or "",
                    m["date_requested"] or "",
                    m["status"] or "",
                    m["fee"] or 0.0,
                    m["staff"] or "",
                )
            )

    def new_maintenance(self):
        dlg = MaintenanceDialog(self, self.staff_model)
        self.wait_window(dlg)
        if dlg.saved:
            r = dlg.result
            self.maintenance_model.create(
                r["tenant_id"], r["description"], r["priority"], fee=r["fee"], staff=r["staff"]
            )
            self.load_maintenance()
            messagebox.showinfo("Saved", "Maintenance request added.", parent=self)

    # =======================
    # STAFF
    # =======================

    def show_staff(self):
        self.current_view = "staff"
        self.clear_body("Staff")
        frame = self.body_frame
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew")

        ctk.CTkButton(top, text="Add Staff", width=120, command=self.add_staff).pack(side="left", padx=4)
        ctk.CTkButton(top, text="Remove Staff", width=140, command=self.remove_staff).pack(side="left", padx=4)

        cols = ("staff_id", "name", "contact", "role", "status")
        self.staff_tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            self.staff_tree.heading(c, text=c.title())
            self.staff_tree.column(c, width=120)
        self.staff_tree.grid(row=1, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.staff_tree.yview)
        self.staff_tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=1, column=1, sticky="ns")

        self.load_staff()

    def load_staff(self):
        if not hasattr(self, "staff_tree"):
            return
        for r in self.staff_tree.get_children():
            self.staff_tree.delete(r)
        for s in self.staff_model.all():
            self.staff_tree.insert(
                "",
                tk.END,
                values=(s["staff_id"], s["name"], s["contact"], s["role"], s["status"])
            )

    def get_selected_staff_id(self):
        if not hasattr(self, "staff_tree"):
            return None
        sel = self.staff_tree.selection()
        if not sel:
            return None
        item = self.staff_tree.item(sel[0])
        vals = item["values"]
        if not vals:
            return None
        try:
            return int(vals[0])
        except (TypeError, ValueError):
            return None

    def add_staff(self):
        dlg = StaffDialog(self)
        self.wait_window(dlg)
        if dlg.saved:
            self.staff_model.create(**dlg.result)
            self.load_staff()
            messagebox.showinfo("Saved", "Staff added.", parent=self)

    def remove_staff(self):
        sid = self.get_selected_staff_id()
        if not sid:
            messagebox.showwarning("Select", "Please select staff to remove.", parent=self)
            return
        if not messagebox.askyesno("Confirm", "Remove selected staff?", parent=self):
            return
        self.staff_model.delete(sid)
        self.load_staff()
        messagebox.showinfo("Removed", "Staff removed.", parent=self)

    # =======================
    # RECYCLE BIN (TERMINATED TENANTS)
    # =======================

    def show_recycle_bin(self):
        self.current_view = "recycle"
        self.clear_body("Recycle Bin - Terminated Tenants")
        frame = self.body_frame
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew")

        ctk.CTkButton(top, text="Restore Tenant", width=130, command=self.restore_tenant).pack(side="left", padx=4)

        cols = (
            "tenant_id",
            "name",
            "contact",
            "unit_code",
            "tenant_type",
            "move_in",
            "move_out",
            "move_out_reason",
        )
        self.recycle_tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            self.recycle_tree.heading(c, text=c.replace("_", " ").title())
            self.recycle_tree.column(c, width=120)
        self.recycle_tree.grid(row=1, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.recycle_tree.yview)
        self.recycle_tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=1, column=1, sticky="ns")

        self.load_recycle()

    def load_recycle(self):
        if not hasattr(self, "recycle_tree"):
            return
        for r in self.recycle_tree.get_children():
            self.recycle_tree.delete(r)
        for t in self.tenant_model.terminated():
            self.recycle_tree.insert(
                "",
                tk.END,
                values=(
                    t["tenant_id"],
                    t["name"],
                    t["contact"] or "",
                    t["unit_code"] or "",
                    t["tenant_type"] or "",
                    t["move_in"] or "",
                    t["move_out"] or "",
                    t["move_out_reason"] or "",
                )
            )

    def get_selected_recycle_tenant_id(self):
        if not hasattr(self, "recycle_tree"):
            return None
        sel = self.recycle_tree.selection()
        if not sel:
            return None
        item = self.recycle_tree.item(sel[0])
        vals = item["values"]
        if not vals:
            return None
        try:
            return int(vals[0])
        except (TypeError, ValueError):
            return None

    def restore_tenant(self):
        tid = self.get_selected_recycle_tenant_id()
        if not tid:
            messagebox.showwarning("Select", "Please select a terminated tenant to restore.", parent=self)
            return

        t = self.tenant_model.get(tid)
        if not t:
            messagebox.showwarning("Not Found", "Tenant not found.", parent=self)
            return

        self.tenant_model.restore(tid)
        if t["unit_id"]:
            self.unit_model.update_status(t["unit_id"], "Occupied")

        self.load_recycle()
        messagebox.showinfo("Restored", "Tenant restored to Active status.", parent=self)

    # =======================
    # REPORTS
    # =======================

    def show_reports(self):
        self.current_view = "reports"
        self.clear_body("Reports")
        frame = self.body_frame
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew")

        today = datetime.date.today()
        self.rep_year_var = tk.IntVar(value=today.year)
        self.rep_month_var = tk.IntVar(value=today.month)

        ctk.CTkLabel(top, text="Year:").pack(side="left", padx=(4, 2))
        year_e = ctk.CTkEntry(top, width=80, textvariable=self.rep_year_var)
        year_e.pack(side="left", padx=2)

        ctk.CTkLabel(top, text="Month (1-12):").pack(side="left", padx=(10, 2))
        month_e = ctk.CTkEntry(top, width=50, textvariable=self.rep_month_var)
        month_e.pack(side="left", padx=2)

        ctk.CTkButton(top, text="Generate", width=120, command=self.load_reports).pack(side="left", padx=10)

        self.reports_text = tk.Text(frame, height=15, wrap="word")
        self.reports_text.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)

        self.load_reports()

    def load_reports(self):
        year = self.rep_year_var.get() if hasattr(self, "rep_year_var") else datetime.date.today().year
        month = self.rep_month_var.get() if hasattr(self, "rep_month_var") else datetime.date.today().month

        income = self.payment_model.total_for_month(year, month)
        maint_cost = self.maintenance_model.total_fee_for_month(year, month)

        lines = []
        lines.append(f"REPORTS FOR {year}-{month:02d}")
        lines.append("=" * 40)
        lines.append("")
        lines.append(f"Total Billing Collected (Paid) This Month: ₱{income:.2f}")
        lines.append(f"Total Maintenance Fees This Month: ₱{maint_cost:.2f}")
        lines.append("")
        lines.append("Active Tenants by Type:")
        counts = {"Solo": 0, "Family": 0, "Dorm": 0, "Other": 0}
        for t in self.tenant_model.active():
            tt = (t["tenant_type"] or "").title()
            if tt not in counts:
                counts["Other"] += 1
            else:
                counts[tt] += 1
        for k, v in counts.items():
            lines.append(f"  {k}: {v}")

        if hasattr(self, "reports_text"):
            self.reports_text.delete("1.0", "end")
            self.reports_text.insert("1.0", "\n".join(lines))

    # =======================
    # POLICY / CHANGE PASSWORD
    # =======================

    def show_policy(self):
        PolicyDialog(self)

    def change_password(self):
        dlg = ChangePasswordDialog(self, self.db)
        self.wait_window(dlg)

# ===============================
# MAIN ENTRY
# ===============================

def main():
    db = Database()

    root = ctk.CTk()
    root.withdraw()  # hide placeholder

    # Policy dialog
    policy = PolicyDialog(root)
    root.wait_window(policy)
    if not policy.accepted:
        root.destroy()
        db.close()
        return

    # Login
    login = LoginDialog(root, db)
    root.wait_window(login)
    if not login.success:
        root.destroy()
        db.close()
        return

    root.destroy()

    # Main app
    while True:
        app = MainApp(db)
        app.mainloop()
        if not app.logout_requested:
            break

        # after logout, show login again
        new_root = ctk.CTk()
        new_root.withdraw()
        login = LoginDialog(new_root, db)
        new_root.wait_window(login)
        if not login.success:
            new_root.destroy()
            break
        new_root.destroy()

    db.close()


if __name__ == "__main__":
    main()