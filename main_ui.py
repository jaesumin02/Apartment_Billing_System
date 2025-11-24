import datetime
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
from .database import Database
from .models import UnitModel, TenantModel, PaymentModel, MaintenanceModel, StaffModel
from .dialogs import (
    LoginDialog, ChangePasswordDialog, PolicyDialog, TenantDialog,
    MoveOutDialog, PaymentDialog, PaymentEditDialog, MaintenanceDialog, StaffDialog
)



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

        try:
            style = ttk.Style()
            style.configure("Treeview", font=("Segoe UI", 11))
            style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))
        except Exception:
            pass
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
            old_unit_id = tenant["unit_id"]
            new_unit_id = data["unit_id"]
            self.tenant_model.update(tid, **data)
            if old_unit_id != new_unit_id:
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

        if tenant["unit_id"]:
            if not self.tenant_model.tenants_in_unit(tenant["unit_id"]):
                self.unit_model.update_status(tenant["unit_id"], "Vacant")

        self.load_tenants()
        messagebox.showinfo("Terminated", "Tenant moved out / terminated.", parent=self)

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

    def show_policy(self):
        PolicyDialog(self)

    def change_password(self):
        dlg = ChangePasswordDialog(self, self.db)
        self.wait_window(dlg)

def main():
    db = Database()

    root = ctk.CTk()
    root.withdraw() 
    policy = PolicyDialog(root)
    root.wait_window(policy)
    if not policy.accepted:
        root.destroy()
        db.close()
        return

    login = LoginDialog(root, db)
    root.wait_window(login)
    if not login.success:
        root.destroy()
        db.close()
        return

    root.destroy()

    while True:
        app = MainApp(db)
        app.mainloop()
        if not app.logout_requested:
            break
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
