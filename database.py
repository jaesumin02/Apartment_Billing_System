import os
import sqlite3
from constants import DB_FILE, DORM_DEFAULT_CAPACITY


class Database:
    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file
        first_time = not os.path.exists(db_file)
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.setup(first_time)

    def _ensure_column(self, table, column, col_def):
        cur = self.conn.cursor()
        cur.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in cur.fetchall()]
        if column not in cols:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}")
            self.conn.commit()

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
            date_completed DATE,
            deleted INTEGER DEFAULT 0,
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

        c.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            action TEXT,
            details TEXT
        );
        """)

        self.conn.commit()

        self._ensure_column("units", "capacity", "INTEGER DEFAULT 1")
        self._ensure_column("tenants", "guardian_name", "TEXT DEFAULT ''")
        self._ensure_column("tenants", "guardian_contact", "TEXT DEFAULT ''")
        self._ensure_column("tenants", "guardian_relation", "TEXT DEFAULT ''")
        self._ensure_column("tenants", "emergency_contact", "TEXT DEFAULT ''")
        self._ensure_column("tenants", "advance_paid", "REAL DEFAULT 0")
        self._ensure_column("tenants", "deposit_paid", "REAL DEFAULT 0")
        self._ensure_column("tenants", "move_out_reason", "TEXT DEFAULT ''")
        self._ensure_column("payments", "note", "TEXT DEFAULT ''")
        self._ensure_column("maintenance", "fee", "REAL DEFAULT 0")
        self._ensure_column("maintenance", "staff", "TEXT DEFAULT ''")
        self._ensure_column("maintenance", "date_completed", "DATE DEFAULT NULL")
        self._ensure_column("maintenance", "deleted", "INTEGER DEFAULT 0")
        self._ensure_column("staff", "status", "TEXT DEFAULT 'Active'")

        self.seed_defaults()

    def seed_defaults(self):
        c = self.conn.cursor()

        c.execute("SELECT COUNT(*) as c FROM users")
        if c.fetchone()["c"] == 0:
            c.execute("INSERT INTO users (username,password) VALUES (?,?)", ("admin", "admin"))

        c.execute("SELECT COUNT(*) as c FROM units")
        if c.fetchone()["c"] == 0:

            for i in range(1, 21):
                code = f"S{i:02d}"
                c.execute(
                    "INSERT INTO units (unit_code, unit_type, price, status, capacity) VALUES (?,?,?,?,?)",
                    (code, "Solo", 4500.0, "Vacant", 1)
                )

            for i in range(1, 26):
                code = f"F{i:02d}"
                c.execute(
                    "INSERT INTO units (unit_code, unit_type, price, status, capacity) VALUES (?,?,?,?,?)",
                    (code, "Family", 9000.0, "Vacant", 1)
                )

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
