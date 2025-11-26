import datetime
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from .models import UnitModel, TenantModel, StaffModel

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

        body_fr = ctk.CTkFrame(frm, corner_radius=8, height=120)
        body_fr.pack(fill="x", padx=6, pady=(0, 6))
        body_fr.pack_propagate(False)

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

        self.accept_btn = ctk.CTkButton(btn_fr, text="Accept", width=110, command=self.on_accept, state="normal")
        self.accept_btn.pack(side="right", padx=6)

        ctk.CTkButton(btn_fr, text="Decline", width=110, fg_color="#883333", command=self.on_decline).pack(
            side="right", padx=6
        )

    def on_toggle(self):
        pass

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
        self.geometry("650x680")
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
        unit_label = self.unit_cmb.get()
        unit = self.unit_map.get(unit_label)
        ttype = self.type_cmb.get().strip().lower()
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
        if not guardian_name or len(guardian_name.split()) < 2:
            messagebox.showwarning("Input", "Guardian full name is required for all tenants.", parent=self)
            return
        if not guardian_contact or not guardian_contact.isdigit():
            messagebox.showwarning("Input", "Guardian contact is required and must contain digits only.", parent=self)
            return
        if tenant_type.lower() == "dorm":
            cap = unit["capacity"] or DORM_DEFAULT_CAPACITY
            cap = min(cap, DORM_DEFAULT_CAPACITY)
            existing = self.tenant_model.tenants_in_unit(unit_id)
            existing_count = len(existing)
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

