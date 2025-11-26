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
        self.activity_model = ActivityLogModel(db)
        self.logout_requested = False
        self.current_view = None

        self.title("Apartment Billing System")
        self.geometry("1280x720")
        self.minsize(1100, 640)
        self.state('zoomed')  # Keep window maximized

        self.build_layout()
        self.show_dashboard()

    def build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        try:
            style = ttk.Style()
            try:
                style.theme_use('default')
            except Exception:
                pass
            style.configure("Treeview", font=("Segoe UI", 11), rowheight=30,
                            background="white", fieldbackground="white", foreground="black")
            style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))
            style.map("Treeview.Heading", background=[('active', '#e6e6e6')])
        except Exception:
            pass
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(13, weight=1)

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
            "width": 220,
            "height": 46,
            "corner_radius": 10,
            "anchor": "w",
            "fg_color": "#1f2933",
            "hover_color": "#2d3f52",
            "border_width": 1,
            "border_color": "#2f6fff",
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

        self.btn_theme = ctk.CTkButton(self.sidebar, text="Toggle Theme", command=self.toggle_theme, **btn_cfg)
        self.btn_theme.grid(row=11, column=0, padx=12, pady=3)

        self.btn_change_pw = ctk.CTkButton(self.sidebar, text="Change Password", command=self.change_password, **btn_cfg)
        self.btn_change_pw.grid(row=12, column=0, padx=12, pady=3)

        

        self.btn_logout = ctk.CTkButton(self.sidebar, text="Logout", command=self.logout, **btn_cfg)
        self.btn_logout.grid(row=14, column=0, padx=12, pady=8)

        footer = ctk.CTkLabel(
            self.sidebar,
            text="Default account:\nadmin / admin",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        footer.grid(row=13, column=0, padx=12, pady=8, sticky="sw")

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

        # Sidebar toggle button (show/hide)
        self.toggle_sidebar_btn = ctk.CTkButton(self.content, text="Hide Sidebar", width=120, command=self.toggle_sidebar)
        self.toggle_sidebar_btn.grid(row=0, column=2, sticky="e", padx=(0,12), pady=(10,0))

        self.body_frame = ctk.CTkFrame(self.content)
        # occupy the entire content area so tables can extend across the gray background
        self.body_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=0, pady=0)

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
    def toggle_sidebar(self):
        """Show/hide the sidebar."""
        if self.sidebar.winfo_viewable():
            self.sidebar.grid_remove()
            self.toggle_sidebar_btn.configure(text="Show Sidebar")
        else:
            self.sidebar.grid()
            self.toggle_sidebar_btn.configure(text="Hide Sidebar")

    def toggle_theme(self):
        # Simple dark/light toggle for wow effect
        if not hasattr(self, "theme_mode"):
            self.theme_mode = "Dark"
        self.theme_mode = "Light" if self.theme_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(self.theme_mode)

    def log_action(self, action, details=""):
        try:
            self.activity_model.log(action, details)
        except Exception:
            pass

    def show_dashboard(self):
        self.current_view = "dashboard"
        self.clear_body("Overview")
        frame = self.body_frame
        # Top: four summary cards
        for i in range(4):
            frame.grid_columnconfigure(i, weight=1)

        total_units = len(self.unit_model.all())
        active_tenants = len(self.tenant_model.active())
        vacants = self.db.query("SELECT COUNT(*) as c FROM units WHERE status='Vacant'")[0]["c"]

        income_30 = self.db.query(
            "SELECT SUM(total) as s FROM payments WHERE date_paid>=?",
            ((datetime.date.today() - datetime.timedelta(days=30)).isoformat(),)
        )[0]["s"] or 0.0

        total_req, pending_req = self.maintenance_model.counts()

        title_font = ctk.CTkFont(size=12, weight="bold")
        value_font = ctk.CTkFont(size=26, weight="bold")
        sub_font = ctk.CTkFont(size=10)

        def make_card(col, title_text, value_text, accent="#2f6fff", subtitle="", on_click=None):
            card = ctk.CTkFrame(frame, corner_radius=12, border_width=2, border_color=accent, fg_color="#051327")
            card.grid(row=0, column=col, padx=10, pady=10, sticky="nsew")
            top_lbl = ctk.CTkLabel(card, text=title_text.upper(), font=title_font, text_color="#9fc5ff")
            top_lbl.pack(anchor="w", padx=14, pady=(12, 2))
            val_lbl = ctk.CTkLabel(card, text=value_text, font=value_font)
            val_lbl.pack(anchor="w", padx=14, pady=(0, 6))
            if subtitle:
                sub_lbl = ctk.CTkLabel(card, text=subtitle, font=sub_font, text_color="#9fb7d6")
                sub_lbl.pack(anchor="w", padx=14, pady=(0, 10))
            # make the card clickable if callback provided
            if callable(on_click):
                try:
                    # store original colors to restore later
                    orig_bg = card.cget('fg_color') if hasattr(card, 'cget') else "#051327"
                    pressed_bg = "#03202b"

                    def on_enter(e):
                        try:
                            card.configure(cursor="hand2")
                        except Exception:
                            pass

                    def on_leave(e):
                        try:
                            card.configure(cursor="")
                            card.configure(fg_color=orig_bg)
                        except Exception:
                            pass

                    def on_press(e):
                        try:
                            card._pressed = True
                            card.configure(fg_color=pressed_bg)
                        except Exception:
                            pass

                    def on_release(e, fn=on_click):
                        try:
                            was_pressed = getattr(card, '_pressed', False)
                            card._pressed = False
                            card.configure(fg_color=orig_bg)
                            if was_pressed:
                                fn()
                        except Exception:
                            pass

                    # bind events to card and inner labels
                    card.bind("<Enter>", on_enter)
                    card.bind("<Leave>", on_leave)
                    card.bind("<ButtonPress-1>", on_press)
                    card.bind("<ButtonRelease-1>", on_release)

                    top_lbl.bind("<Enter>", on_enter)
                    top_lbl.bind("<Leave>", on_leave)
                    top_lbl.bind("<ButtonPress-1>", on_press)
                    top_lbl.bind("<ButtonRelease-1>", on_release)

                    val_lbl.bind("<Enter>", on_enter)
                    val_lbl.bind("<Leave>", on_leave)
                    val_lbl.bind("<ButtonPress-1>", on_press)
                    val_lbl.bind("<ButtonRelease-1>", on_release)

                    if subtitle:
                        sub_lbl.bind("<Enter>", on_enter)
                        sub_lbl.bind("<Leave>", on_leave)
                        sub_lbl.bind("<ButtonPress-1>", on_press)
                        sub_lbl.bind("<ButtonRelease-1>", on_release)
                except Exception:
                    pass
            return card

        # four cards across (clickable)
        make_card(0, "TOTAL TENANTS", str(active_tenants), accent="#2f6fff", subtitle="+ demo data", on_click=lambda: self.show_tenants())
        make_card(1, "VACANT UNITS", str(vacants), accent="#2fe6c1", subtitle=f"out of {total_units} units", on_click=lambda: self.show_units())
        make_card(2, "BILLING SUMMARY", f"₱{income_30:,.2f}", accent="#3ad65a", subtitle="Collected this month", on_click=lambda: self.show_billing())
        make_card(3, "MAINTENANCE COUNT", str(pending_req), accent="#ff9a33", subtitle="Pending requests", on_click=lambda: self.show_maintenance())

        # Bottom: two panels (Recent Payments | Pending Maintenance)
        bottom_frame = ctk.CTkFrame(frame, fg_color="transparent")
        bottom_frame.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=6, pady=(8, 0))
        bottom_frame.grid_columnconfigure(0, weight=3)
        bottom_frame.grid_columnconfigure(1, weight=2)

        # Left: Recent Payments card
        pay_card = ctk.CTkFrame(bottom_frame, corner_radius=8, border_width=1, border_color="#2f6fff", fg_color="#061428")
        pay_card.grid(row=0, column=0, sticky="nsew", padx=(6, 4), pady=6)
        ctk.CTkLabel(pay_card, text="Recent Payments", font=ctk.CTkFont(size=14, weight="bold"), text_color="#9fc5ff").pack(anchor="w", padx=12, pady=(12, 6))

        cols_pay = ("tenant", "unit", "amount", "date", "status")
        # remove old if exists
        if hasattr(self, 'dashboard_pay_tree'):
            try:
                for r in self.dashboard_pay_tree.get_children():
                    self.dashboard_pay_tree.delete(r)
            except Exception:
                pass
        self.dashboard_pay_tree = ttk.Treeview(pay_card, columns=cols_pay, show="headings", height=10)
        for c in cols_pay:
            self.dashboard_pay_tree.heading(c, text=c.title())
            self.dashboard_pay_tree.column(c, width=110, anchor="w")
        self.dashboard_pay_tree.pack(fill="both", expand=True, padx=8, pady=(0,8))

        # populate all payments
        def row_get(r, k, default=''):
            try:
                # try mapping access (sqlite3.Row supports indexing by key)
                return r[k] if (r is not None and k in getattr(r, 'keys', lambda: [])()) else default
            except Exception:
                try:
                    return r.get(k, default) if hasattr(r, 'get') else default
                except Exception:
                    return default

        payments = list(self.payment_model.all())
        for p in reversed(payments):
            tname = row_get(p, 'name', '')
            tenant_id = row_get(p, 'tenant_id', '')
            # fetch unit code from tenant's unit
            unit_code = ''
            if tenant_id:
                try:
                    tenant_row = self.db.query("SELECT u.unit_code FROM tenants t LEFT JOIN units u ON t.unit_id = u.unit_id WHERE t.tenant_id=?", (tenant_id,))[0]
                    unit_code = row_get(tenant_row, 'unit_code', '')
                except Exception:
                    unit_code = ''
            amount = f"₱{(row_get(p, 'total', 0) or 0):,.2f}"
            date_paid = row_get(p, 'date_paid', '')
            status = row_get(p, 'status', '')
            self.dashboard_pay_tree.insert('', tk.END, values=(tname, unit_code, amount, date_paid, status))

        # Right: Pending Maintenance card
        maint_card = ctk.CTkFrame(bottom_frame, corner_radius=8, border_width=1, border_color="#2f6fff", fg_color="#061428")
        maint_card.grid(row=0, column=1, sticky="nsew", padx=(4, 6), pady=6)
        ctk.CTkLabel(maint_card, text="Pending Maintenance", font=ctk.CTkFont(size=14, weight="bold"), text_color="#9fc5ff").pack(anchor="w", padx=12, pady=(12, 6))

        cols_maint = ("unit", "issue", "priority", "status")
        if hasattr(self, 'dashboard_maint_tree'):
            try:
                for r in self.dashboard_maint_tree.get_children():
                    self.dashboard_maint_tree.delete(r)
            except Exception:
                pass
        self.dashboard_maint_tree = ttk.Treeview(maint_card, columns=cols_maint, show="headings", height=10)
        for c in cols_maint:
            self.dashboard_maint_tree.heading(c, text=c.title())
            self.dashboard_maint_tree.column(c, width=140, anchor="w")
        self.dashboard_maint_tree.pack(fill="both", expand=True, padx=8, pady=(0,8))

        # populate maintenance
        maints = self.maintenance_model.all()
        for m in maints[-10:]:
            # fetch unit code from tenant's unit
            tenant_id = row_get(m, 'tenant_id', '')
            unit_code = ''
            if tenant_id:
                try:
                    tenant_row = self.db.query("SELECT u.unit_code FROM tenants t LEFT JOIN units u ON t.unit_id = u.unit_id WHERE t.tenant_id=?", (tenant_id,))[0]
                    unit_code = row_get(tenant_row, 'unit_code', '')
                except Exception:
                    unit_code = ''
            issue = row_get(m, 'description') or row_get(m, 'issue') or ''
            pr = row_get(m, 'priority', '')
            st = row_get(m, 'status', '')
            self.dashboard_maint_tree.insert('', tk.END, values=(unit_code, issue, pr, st))

    def show_units(self):
        self.current_view = "units"
        self.clear_body("Units")
        frame = self.body_frame
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        filter_box = ctk.CTkFrame(frame, corner_radius=8, border_width=1, border_color="#2f6fff", fg_color="#061428")
        filter_box.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 12))
        filter_box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(filter_box, text="FILTERS & SEARCH", font=ctk.CTkFont(size=12, weight="bold"), text_color="#9fc5ff").grid(row=0, column=0, sticky="w", padx=12, pady=(8, 4))

        filters_row = ctk.CTkFrame(filter_box, fg_color="transparent")
        filters_row.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))

        # Search entry
        ctk.CTkLabel(filters_row, text="Search Unit:", width=100).pack(side="left", padx=(0, 6))
        self.unit_search_var = tk.StringVar()
        search_e = ctk.CTkEntry(filters_row, width=220, textvariable=self.unit_search_var, placeholder_text="Unit number...")
        search_e.pack(side="left", padx=(0, 12))
        ctk.CTkButton(filters_row, text="Go", width=70, command=self.load_units).pack(side="left", padx=(0, 12))

        # Floor / Status controls
        ctk.CTkLabel(filters_row, text="Floor:", width=60).pack(side="left", padx=(0, 6))
        self.unit_floor_var = tk.StringVar(value="All Floors")
        floor_cmb = ctk.CTkComboBox(filters_row, values=["All Floors"], width=140, variable=self.unit_floor_var)
        floor_cmb.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(filters_row, text="Status:", width=60).pack(side="left", padx=(0, 6))
        self.unit_status_var = tk.StringVar(value="All Status")
        status_cmb = ctk.CTkComboBox(
            filters_row,
            values=["All Status", "Vacant", "Occupied"],
            width=140,
            variable=self.unit_status_var,
            command=lambda _v=None: self.load_units()
        )
        status_cmb.pack(side="left", padx=(0, 12))

        # Action buttons on the right
        actions = ctk.CTkFrame(filter_box, fg_color="transparent")
        actions.grid(row=0, column=1, rowspan=2, sticky="e", padx=12, pady=6)
        ctk.CTkButton(actions, text="Export Excel", width=120, command=self.export_units_excel).pack(side="top", pady=4)
        ctk.CTkButton(actions, text="Add Unit", width=120, command=self.add_unit).pack(side="top", pady=4)
        ctk.CTkButton(actions, text="Edit Unit", width=120, command=self.edit_unit).pack(side="top", pady=4)
        ctk.CTkButton(actions, text="Set Dorm Capacity", width=140, command=self.set_dorm_capacity).pack(side="top", pady=4)

        # Table container with border to match blueprint card
        table_box = ctk.CTkFrame(frame, corner_radius=8, border_width=1, border_color="#2f6fff", fg_color="#061428")
        table_box.grid(row=1, column=0, sticky="nsew", padx=8, pady=0)
        table_box.grid_rowconfigure(0, weight=1)
        table_box.grid_columnconfigure(0, weight=1)

        # style treeview headings for a cleaner blueprint look
        try:
            style = ttk.Style()
            style.theme_use('default')
            style.configure("Blueprint.Treeview", background="#061428", fieldbackground="#061428", foreground="#cfe6ff")
            style.configure("Blueprint.Treeview.Heading", background="#0b2a59", foreground="#9fc5ff", relief="flat", font=(None, 10, 'bold'))
            style.configure("White.Treeview", background="white", fieldbackground="white", foreground="black")
            style.configure("White.Treeview.Heading", background="#0b2a59", foreground="#9fc5ff", relief="flat", font=(None, 10, 'bold'))
            style.configure("WhiteBlueprint.Treeview", background="white", fieldbackground="white", foreground="black")
            style.configure("WhiteBlueprint.Treeview.Heading", background="#0b2a59", foreground="#9fc5ff", relief="flat", font=(None, 10, 'bold'))
        except Exception:
            pass

        self.units_tree = ttk.Treeview(
            table_box,
            columns=("unit_id", "unit_code", "unit_type", "price", "status", "capacity", "tenants"),
            show="headings",
            style="White.Treeview"
        )
        for col in ("unit_id", "unit_code", "unit_type", "price", "status", "capacity", "tenants"):
            self.units_tree.heading(col, text=col.title())
            self.units_tree.column(col, minwidth=120, stretch=True, anchor="w")
        self.units_tree.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        vsb = ttk.Scrollbar(table_box, orient="vertical", command=self.units_tree.yview)
        self.units_tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns", padx=(0,8), pady=8)

        self.load_units()

    def load_units(self):
        if not hasattr(self, "units_tree"):
            return
        for r in self.units_tree.get_children():
            self.units_tree.delete(r)

        status = getattr(self, "unit_status_var", None)
        status = status.get() if status is not None else "All"
        
        search = self.unit_search_var.get().strip().lower() if hasattr(self, "unit_search_var") else ""

        rows = self.unit_model.filter_by_status(status if status in ("Vacant", "Occupied") else None)
        for u in rows:
            # Apply search filter
            if search:
                unit_code = (u["unit_code"] or "").lower()
                unit_type = (u["unit_type"] or "").lower()
                if search not in unit_code and search not in unit_type:
                    continue
            
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

    def get_selected_unit_id(self):
        if not hasattr(self, "units_tree"):
            return None
        sel = self.units_tree.selection()
        if not sel:
            return None
        item = self.units_tree.item(sel[0])
        vals = item.get("values") or []
        if not vals:
            return None
        try:
            return int(vals[0])
        except (TypeError, ValueError):
            return None

    def add_unit(self):
        dlg = UnitEditDialog(self, None)
        self.wait_window(dlg)
        if not dlg.saved:
            return
        data = dlg.result
        status = 'Vacant'
        try:
            self.db.execute("INSERT INTO units (unit_code, unit_type, price, status, capacity) VALUES (?,?,?,?,?)",
                            (data['unit_code'], data['unit_type'], data['price'], status, data['capacity']))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add unit: {e}", parent=self)
            return
        self.load_units()
        messagebox.showinfo("Saved", "Unit added.", parent=self)

    def edit_unit(self):
        uid = self.get_selected_unit_id()
        if not uid:
            messagebox.showwarning("Select", "Please select a unit to edit.", parent=self)
            return
        unit = self.unit_model.get(uid)
        if not unit:
            messagebox.showwarning("Not Found", "Unit not found.", parent=self)
            return
        dlg = UnitEditDialog(self, unit)
        self.wait_window(dlg)
        if not dlg.saved:
            return
        data = dlg.result
        tenants = self.tenant_model.tenants_in_unit(uid)
        current = len(tenants)
        new_cap = data.get('capacity') or 0
        if new_cap < current:
            if not messagebox.askyesno("Capacity Reduction", f"New capacity ({new_cap}) is less than current occupants ({current}).\nDo you want to proceed?", parent=self):
                return
        try:
            self.db.execute("UPDATE units SET unit_type=?, price=?, capacity=? WHERE unit_id=?",
                            (data['unit_type'], data['price'], data['capacity'], uid))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update unit: {e}", parent=self)
            return
        if data['unit_type'].lower() == 'dorm':
            if current >= data['capacity']:
                new_status = 'Full'
            elif current > 0:
                new_status = 'Occupied'
            else:
                new_status = 'Vacant'
        else:
            new_status = 'Occupied' if current > 0 else 'Vacant'
        try:
            self.unit_model.update_status(uid, new_status)
        except Exception:
            pass
        self.load_units()
        messagebox.showinfo("Saved", "Unit updated.", parent=self)

    def set_dorm_capacity(self):
        uid = self.get_selected_unit_id()
        if not uid:
            messagebox.showwarning("Select", "Please select a unit to set capacity.", parent=self)
            return
        unit = self.unit_model.get(uid)
        if not unit:
            messagebox.showwarning("Not Found", "Unit not found.", parent=self)
            return
        if unit['unit_type'].lower() != 'dorm':
            messagebox.showwarning("Invalid", "Only dorm units can have capacity set.", parent=self)
            return
        cap_str = simpledialog.askstring("Set Dorm Capacity", f"Enter capacity for {unit['unit_code']}:", parent=self)
        if cap_str is None:
            return
        try:
            new_cap = int(cap_str.strip())
        except ValueError:
            messagebox.showwarning("Input", "Capacity must be a whole number.", parent=self)
            return
        if new_cap < 0:
            messagebox.showwarning("Input", "Capacity cannot be negative.", parent=self)
            return
        tenants = self.tenant_model.tenants_in_unit(uid)
        current = len(tenants)
        if new_cap < current:
            if not messagebox.askyesno("Capacity Reduction", f"New capacity ({new_cap}) is less than current occupants ({current}).\nDo you want to proceed?", parent=self):
                return
        try:
            self.unit_model.update_capacity(uid, new_cap)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update capacity: {e}", parent=self)
            return
        if current >= new_cap:
            new_status = 'Full'
        elif current > 0:
            new_status = 'Occupied'
        else:
            new_status = 'Vacant'
        try:
            self.unit_model.update_status(uid, new_status)
        except Exception:
            pass
        self.load_units()
        messagebox.showinfo("Saved", f"Capacity for {unit['unit_code']} set to {new_cap}.", parent=self)

    def show_tenants(self):
        self.current_view = "tenants"
        self.clear_body("Tenants")
        frame = self.body_frame
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Filters & actions (blueprint-style)
        filter_box = ctk.CTkFrame(frame, corner_radius=8, border_width=1, border_color="#2f6fff", fg_color="#061428")
        filter_box.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 12))
        filter_box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(filter_box, text="SEARCH & FILTER", font=ctk.CTkFont(size=12, weight="bold"), text_color="#9fc5ff").grid(row=0, column=0, sticky="w", padx=12, pady=(8,4))

        filters_row = ctk.CTkFrame(filter_box, fg_color="transparent")
        filters_row.grid(row=1, column=0, sticky="ew", padx=12, pady=(0,12))

        # Left: search box
        ctk.CTkLabel(filters_row, text="Search Tenants:", width=120).pack(side="left", padx=(0,6))
        self.tenant_search_var = tk.StringVar()
        search_e = ctk.CTkEntry(filters_row, width=420, textvariable=self.tenant_search_var, placeholder_text="Search by name, email, phone, or unit")
        search_e.pack(side="left", padx=(0,12))
        ctk.CTkButton(filters_row, text="Go", width=70, command=self.load_tenants).pack(side="left", padx=(0,12))

        # Right: status filter
        ctk.CTkLabel(filters_row, text="Status Filter:", width=110).pack(side="left", padx=(0,6))
        self.tenant_status_var = tk.StringVar(value="All Tenants")
        status_cmb = ctk.CTkComboBox(filters_row, values=["All Tenants", "Active", "Terminated"], width=180, variable=self.tenant_status_var, command=lambda _v=None: self.load_tenants())
        status_cmb.pack(side="left", padx=(0,6))

        # action buttons on filter box
        actions = ctk.CTkFrame(filter_box, fg_color="transparent")
        actions.grid(row=0, column=1, rowspan=2, sticky="e", padx=12, pady=6)
        ctk.CTkButton(actions, text="Add Tenant", width=120, command=self.add_tenant).pack(side="top", pady=4)
        ctk.CTkButton(actions, text="Edit Tenant", width=120, command=self.edit_tenant).pack(side="top", pady=4)
        ctk.CTkButton(actions, text="Terminate Tenant", width=150, command=self.terminate_tenant).pack(side="top", pady=4)

        # Table container
        table_box = ctk.CTkFrame(frame, corner_radius=8, border_width=1, border_color="#2f6fff", fg_color="#061428")
        table_box.grid(row=1, column=0, sticky="nsew", padx=8, pady=0)
        table_box.grid_rowconfigure(0, weight=1)
        table_box.grid_columnconfigure(0, weight=1)

        cols = (
            "tenant_id",
            "name",
            "contact",
            "unit_code",
            "tenant_type",
            "move_in",
            "status",
        )
        self.tenants_tree = ttk.Treeview(table_box, columns=cols, show="headings", style="WhiteBlueprint.Treeview")
        for c in cols:
            self.tenants_tree.heading(c, text=c.replace("_", " ").title())
            self.tenants_tree.column(c, minwidth=140, stretch=True, anchor="w")
        self.tenants_tree.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        vsb = ttk.Scrollbar(table_box, orient="vertical", command=self.tenants_tree.yview)
        self.tenants_tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns", padx=(0,8), pady=8)

        self.load_tenants()

    def load_tenants(self):
        if not hasattr(self, "tenants_tree"):
            return
        for r in self.tenants_tree.get_children():
            self.tenants_tree.delete(r)

        query = self.tenant_search_var.get().strip().lower() if hasattr(self, "tenant_search_var") else ""
        rows = self.tenant_model.active()
        
        for t in rows:
            if query:
                name = (t["name"] or "").lower()
                contact = (t["contact"] or "").lower()
                tid_str = str(t["tenant_id"] or "")
                if query not in name and query not in contact and query not in tid_str:
                    continue

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
            self.log_action("Add Tenant", f"{data['name']} (unit_id={data['unit_id']})")
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
            self.log_action("Edit Tenant", f"{data['name']} (tenant_id={tid})")
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
        self.log_action("Terminate Tenant", f"{tenant['name']} (tenant_id={tid}) - {dlg.reason}")
        messagebox.showinfo("Terminated", "Tenant moved out / terminated.", parent=self)

    def show_billing(self):
        self.current_view = "billing"
        self.clear_body("Billing")
        frame = self.body_frame
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Filter box
        filter_box = ctk.CTkFrame(frame, corner_radius=8, border_width=1, border_color="#2f6fff", fg_color="#061428")
        filter_box.grid(row=0, column=0, sticky="ew", padx=8, pady=(6,12))
        filter_box.grid_columnconfigure(0, weight=1)

        filters_row = ctk.CTkFrame(filter_box, fg_color="transparent")
        filters_row.grid(row=0, column=0, sticky="ew", padx=12, pady=12)

        ctk.CTkLabel(filters_row, text="Filter Type:", width=100).pack(side="left", padx=(0,6))
        self.pay_type_var = tk.StringVar(value="All")
        self.pay_type_cmb = ctk.CTkComboBox(
            filters_row,
            values=["All", "Solo", "Family", "Dorm"],
            width=140,
            variable=self.pay_type_var,
            command=lambda _v=None: self.load_payments()
        )
        self.pay_type_cmb.pack(side="left", padx=(0,12))

        ctk.CTkLabel(filters_row, text="Search:", width=80).pack(side="left", padx=(0,6))
        self.pay_search_var = tk.StringVar()
        pay_search_e = ctk.CTkEntry(filters_row, width=220, textvariable=self.pay_search_var, placeholder_text="Name / Tenant ID")
        pay_search_e.pack(side="left", padx=(0,12))
        ctk.CTkButton(filters_row, text="Go", width=70, command=self.load_payments).pack(side="left", padx=(0,12))

        # action buttons on right
        actions = ctk.CTkFrame(filter_box, fg_color="transparent")
        actions.grid(row=0, column=1, sticky="e", padx=12, pady=12)
        ctk.CTkButton(actions, text="New Payment", width=130, command=self.new_payment).pack(side="left", padx=4)
        ctk.CTkButton(actions, text="Edit Payment", width=130, command=self.edit_payment).pack(side="left", padx=4)
        ctk.CTkButton(actions, text="Mark as Paid", width=130, command=self.mark_payment_paid).pack(side="left", padx=4)
        ctk.CTkButton(actions, text="Generate Auto-Bills", width=160, command=self.generate_auto_bills).pack(side="left", padx=4)

        # Table container
        table_box = ctk.CTkFrame(frame, corner_radius=8, border_width=1, border_color="#2f6fff", fg_color="#061428")
        table_box.grid(row=1, column=0, sticky="nsew", padx=8, pady=0)
        table_box.grid_rowconfigure(0, weight=1)
        table_box.grid_columnconfigure(0, weight=1)

        cols = ("payment_id", "tenant", "tenant_type", "rent", "electricity", "water", "total", "date_paid", "status")
        self.pay_tree = ttk.Treeview(table_box, columns=cols, show="headings", style="WhiteBlueprint.Treeview")
        for c in cols:
            self.pay_tree.heading(c, text=c.replace("_", " ").title())
            self.pay_tree.column(c, minwidth=130, stretch=True, anchor="w")
        self.pay_tree.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        vsb = ttk.Scrollbar(table_box, orient="vertical", command=self.pay_tree.yview)
        self.pay_tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns", padx=(0,8), pady=8)

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
        search = self.pay_search_var.get().strip().lower() if hasattr(self, "pay_search_var") else ""
        for row in self.payment_model.all():
            ttype = (row["tenant_type"] or "").title()
            if selected_type != "All" and ttype.lower() != selected_type.lower():
                continue

            if search:
                name = (row["name"] or "").lower()
                note = (row["note"] or "").lower()
                tid_str = str(row["tenant_id"] or "")
                if search not in name and search not in note and search not in tid_str:
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
            payment_id = self.payment_model.create(
                r["tenant_id"], r["rent"], r["electricity"], r["water"], r["status"], r["note"]
            )
            self.load_payments()
            self.log_action("New Payment", f"tenant_id={r['tenant_id']}, total={r['rent'] + r['electricity'] + r['water']}")
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

    def mark_payment_paid(self):
        payment_id = self.get_selected_payment_id()
        if not payment_id:
            messagebox.showwarning("Select", "Please select a payment to mark as paid.", parent=self)
            return
        row = self.payment_model.get(payment_id)
        if not row:
            messagebox.showwarning("Not Found", "Payment not found.", parent=self)
            return
        if (row["status"] or "").lower() == "paid":
            messagebox.showinfo("Status", "This payment is already marked as Paid.", parent=self)
            return
        # keep existing amounts, change status to Paid
        self.payment_model.update(
            payment_id,
            row["rent"] or 0.0,
            row["electricity"] or 0.0,
            row["water"] or 0.0,
            "Paid",
            row["note"] or "",
        )
        self.load_payments()
        self.log_action("Mark as Paid", f"payment_id={payment_id}")
        messagebox.showinfo("Success", "Payment marked as paid.", parent=self)

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
        if not hasattr(self, "pay_tree"):
            return
        sel = self.pay_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a payment to edit.", parent=self)
            return

        item = self.pay_tree.item(sel[0])
        vals = item["values"]
        if not vals:
            return
        payment_id = vals[0]
        try:
            payment_id = int(payment_id)
        except (TypeError, ValueError):
            messagebox.showwarning("Error", "Invalid payment ID.", parent=self)
            return

        row = self.payment_model.get(payment_id)
        if not row:
            messagebox.showwarning("Not Found", "Payment not found.", parent=self)
            return

        dlg = PaymentEditDialog(self, row)
        self.wait_window(dlg)
        if dlg.saved:
            data = dlg.result
            self.payment_model.update(
                payment_id,
                data["rent"],
                data["electricity"],
                data["water"],
                data["status"],
                data["note"]
            )
            self.load_payments()
            self.log_action("Edit Payment", f"payment_id={payment_id}")
            updated = self.payment_model.get(payment_id)
            if updated and (updated["status"] or "").lower() == "paid":
                try:
                    ReceiptDialog(self, updated)
                except Exception as e:
                    pass

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

    def export_payments_excel(self):
        rows = self.payment_model.all()
        if not rows:
            messagebox.showwarning("No Data", "No payments to export.", parent=self)
            return
        if Workbook is None:
            messagebox.showwarning("Missing Library", "openpyxl is required for Excel export. Install it with 'pip install openpyxl'.", parent=self)
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            title="Save payments Excel"
        )
        if not path:
            return

        wb = Workbook()
        ws = wb.active
        ws.title = "Payments"
        headers = ["Payment ID", "Tenant", "Tenant Type", "Rent", "Electricity", "Water", "Total", "Date Paid", "Status", "Note"]
        ws.append(headers)
        for r in rows:
            ws.append([
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
        wb.save(path)
        messagebox.showinfo("Exported", f"Saved to {path}", parent=self)

    def export_tenants_excel(self):
        rows = self.tenant_model.all()
        if not rows:
            messagebox.showwarning("No Data", "No tenants to export.", parent=self)
            return
        if Workbook is None:
            messagebox.showwarning("Missing Library", "openpyxl is required for Excel export. Install it with 'pip install openpyxl'.", parent=self)
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            title="Save tenants Excel"
        )
        if not path:
            return

        wb = Workbook()
        ws = wb.active
        ws.title = "Tenants"
        headers = ["Tenant ID", "Name", "Contact", "Unit Code", "Tenant Type", "Move In", "Status", "Advance Paid", "Deposit Paid"]
        ws.append(headers)
        rows_all = self.tenant_model.all()
        for t in rows_all:
            ws.append([
                t["tenant_id"],
                t["name"] or "",
                t["contact"] or "",
                t["unit_code"] or "",
                t["tenant_type"] or "",
                t["move_in"] or "",
                t["status"] or "",
                t["advance_paid"] or 0.0,
                t["deposit_paid"] or 0.0,
            ])
        wb.save(path)
        messagebox.showinfo("Exported", f"Saved to {path}", parent=self)

    def export_units_excel(self):
        rows = self.unit_model.all()
        if not rows:
            messagebox.showwarning("No Data", "No units to export.", parent=self)
            return
        if Workbook is None:
            messagebox.showwarning("Missing Library", "openpyxl is required for Excel export. Install it with 'pip install openpyxl'.", parent=self)
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            title="Save units Excel"
        )
        if not path:
            return

        wb = Workbook()
        ws = wb.active
        ws.title = "Units"
        headers = ["Unit ID", "Unit Code", "Unit Type", "Price", "Status", "Capacity"]
        ws.append(headers)
        for u in rows:
            ws.append([
                u["unit_id"],
                u["unit_code"],
                u["unit_type"],
                u["price"] or 0.0,
                u["status"] or "",
                u["capacity"] or 0,
            ])
        wb.save(path)
        messagebox.showinfo("Exported", f"Saved to {path}", parent=self)

    def show_maintenance(self):
        self.current_view = "maintenance"
        self.clear_body("Maintenance")
        frame = self.body_frame
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Filter box
        filter_box = ctk.CTkFrame(frame, corner_radius=8, border_width=1, border_color="#2f6fff", fg_color="#061428")
        filter_box.grid(row=0, column=0, sticky="ew", padx=8, pady=(6,12))

        ctk.CTkButton(filter_box, text="New Request", width=120, command=self.new_maintenance).pack(side="left", padx=12, pady=12)

        # Table container
        table_box = ctk.CTkFrame(frame, corner_radius=8, border_width=1, border_color="#2f6fff", fg_color="#061428")
        table_box.grid(row=1, column=0, sticky="nsew", padx=8, pady=0)
        table_box.grid_rowconfigure(0, weight=1)
        table_box.grid_columnconfigure(0, weight=1)

        cols = ("request_id", "tenant_id", "tenant_name", "description", "priority", "date_requested", "status", "fee", "staff")
        self.maint_tree = ttk.Treeview(table_box, columns=cols, show="headings", style="WhiteBlueprint.Treeview")
        for c in cols:
            self.maint_tree.heading(c, text=c.replace("_", " ").title())
            self.maint_tree.column(c, minwidth=100, stretch=True, anchor="w")
        self.maint_tree.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        vsb = ttk.Scrollbar(table_box, orient="vertical", command=self.maint_tree.yview)
        self.maint_tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns", padx=(0,8), pady=8)

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
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Filter box
        filter_box = ctk.CTkFrame(frame, corner_radius=8, border_width=1, border_color="#2f6fff", fg_color="#061428")
        filter_box.grid(row=0, column=0, sticky="ew", padx=8, pady=(6,12))
        filter_box.grid_columnconfigure(0, weight=1)

        filters_row = ctk.CTkFrame(filter_box, fg_color="transparent")
        filters_row.grid(row=0, column=0, sticky="ew", padx=12, pady=12)

        ctk.CTkLabel(filters_row, text="Show:", width=100).pack(side="left", padx=(0,6))
        self.staff_view_var = tk.StringVar(value="Active")
        staff_view_cmb = ctk.CTkComboBox(filters_row, values=["Active", "Archived", "All"], width=140, variable=self.staff_view_var, command=lambda _v=None: self.load_staff())
        staff_view_cmb.pack(side="left", padx=(0,12))

        # action buttons
        actions = ctk.CTkFrame(filter_box, fg_color="transparent")
        actions.grid(row=0, column=1, sticky="e", padx=12, pady=12)
        ctk.CTkButton(actions, text="Add Staff", width=120, command=self.add_staff).pack(side="left", padx=4)
        ctk.CTkButton(actions, text="Remove Staff", width=140, command=self.remove_staff).pack(side="left", padx=4)
        ctk.CTkButton(actions, text="Archive Staff", width=140, command=self.archive_selected_staff).pack(side="left", padx=4)
        ctk.CTkButton(actions, text="Restore Staff", width=140, command=self.restore_selected_staff).pack(side="left", padx=4)
        ctk.CTkButton(actions, text="Remove Archived", width=150, command=self.remove_archived_staff).pack(side="left", padx=4)

        # Table container
        table_box = ctk.CTkFrame(frame, corner_radius=8, border_width=1, border_color="#2f6fff", fg_color="#061428")
        table_box.grid(row=1, column=0, sticky="nsew", padx=8, pady=0)
        table_box.grid_rowconfigure(0, weight=1)
        table_box.grid_columnconfigure(0, weight=1)

        cols = ("staff_id", "name", "contact", "role", "status")
        self.staff_tree = ttk.Treeview(table_box, columns=cols, show="headings", style="WhiteBlueprint.Treeview")
        for c in cols:
            self.staff_tree.heading(c, text=c.title())
            self.staff_tree.column(c, minwidth=150, stretch=True, anchor="w")
        self.staff_tree.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        vsb = ttk.Scrollbar(table_box, orient="vertical", command=self.staff_tree.yview)
        self.staff_tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns", padx=(0,8), pady=8)

        try:
            self.staff_tree.configure(selectmode='browse')
        except Exception:
            pass

        self.load_staff()

    def load_staff(self):
        if not hasattr(self, "staff_tree"):
            return
        for r in self.staff_tree.get_children():
            self.staff_tree.delete(r)
        # support view filter: Active / Archived / All
        view = (self.staff_view_var.get() if hasattr(self, "staff_view_var") else "Active").lower()
        rows = self.staff_model.all()
        for s in rows:
            st = (s.get("status") or "").lower() if isinstance(s, dict) else ((s[4] or "").lower() if len(s) > 4 else "")
            if view == "active" and st != "active":
                continue
            if view == "archived" and st != "archived":
                continue
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

    def archive_selected_staff(self):
        sid = self.get_selected_staff_id()
        if not sid:
            messagebox.showwarning("Select", "Please select staff to archive.", parent=self)
            return
        if not messagebox.askyesno("Confirm", "Archive selected staff?", parent=self):
            return
        try:
            self.staff_model.archive(sid)
        except Exception:
            messagebox.showerror("Error", "Failed to archive staff.", parent=self)
            return
        self.load_staff()
        messagebox.showinfo("Archived", "Staff archived.", parent=self)

    def restore_selected_staff(self):
        sid = self.get_selected_staff_id()
        if not sid:
            # if none selected, check if archived staff exist and offer to switch view
            archived = self.staff_model.archived()
            if archived:
                if messagebox.askyesno("No selection", "No staff selected. Show Archived staff now?", parent=self):
                    try:
                        if not hasattr(self, 'staff_view_var'):
                            self.staff_view_var = tk.StringVar(value='Archived')
                        else:
                            self.staff_view_var.set('Archived')
                        self.load_staff()
                    except Exception:
                        pass
                    return
            messagebox.showwarning("Select", "Please select staff to restore.", parent=self)
            return
        if not messagebox.askyesno("Confirm", "Restore selected staff?", parent=self):
            return
        try:
            self.staff_model.restore(sid)
        except Exception:
            messagebox.showerror("Error", "Failed to restore staff.", parent=self)
            return
        self.load_staff()
        messagebox.showinfo("Restored", "Staff restored to Active.", parent=self)

    def remove_archived_staff(self):
        # remove all archived staff after confirmation
        archived = self.staff_model.archived()
        if not archived:
            messagebox.showinfo("Info", "No archived staff to remove.", parent=self)
            return
        if not messagebox.askyesno("Confirm", f"This will permanently remove {len(archived)} archived staff. Continue?", parent=self):
            return
        try:
            for s in archived:
                sid = s['staff_id'] if isinstance(s, dict) else s[0]
                self.staff_model.delete(sid)
        except Exception:
            messagebox.showerror("Error", "Failed to remove archived staff.", parent=self)
            return
        self.load_staff()
        messagebox.showinfo("Removed", "Archived staff removed.", parent=self)

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
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Filter box
        filter_box = ctk.CTkFrame(frame, corner_radius=8, border_width=1, border_color="#2f6fff", fg_color="#061428")
        filter_box.grid(row=0, column=0, sticky="ew", padx=8, pady=(6,12))

        ctk.CTkButton(filter_box, text="Restore Tenant", width=130, command=self.restore_tenant).pack(side="left", padx=12, pady=12)

        # Table container
        table_box = ctk.CTkFrame(frame, corner_radius=8, border_width=1, border_color="#2f6fff", fg_color="#061428")
        table_box.grid(row=1, column=0, sticky="nsew", padx=8, pady=0)
        table_box.grid_rowconfigure(0, weight=1)
        table_box.grid_columnconfigure(0, weight=1)

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
        self.recycle_tree = ttk.Treeview(table_box, columns=cols, show="headings", style="WhiteBlueprint.Treeview")
        for c in cols:
            self.recycle_tree.heading(c, text=c.replace("_", " ").title())
            self.recycle_tree.column(c, minwidth=100, stretch=True, anchor="w")
        self.recycle_tree.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        vsb = ttk.Scrollbar(table_box, orient="vertical", command=self.recycle_tree.yview)
        self.recycle_tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns", padx=(0,8), pady=8)

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
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=0)
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Metrics row (summary cards)
        metrics_box = ctk.CTkFrame(frame, corner_radius=8, border_width=0, fg_color="transparent")
        metrics_box.grid(row=0, column=0, sticky="ew", padx=8, pady=(6,8))
        for i in range(4):
            metrics_box.grid_columnconfigure(i, weight=1)

        def make_metric(parent, title, value, fg="#cfe6ff"):
            f = ctk.CTkFrame(parent, corner_radius=6, border_width=1, border_color="#2f6fff", fg_color="#061428")
            lbl_title = ctk.CTkLabel(f, text=title, text_color="#9fc5ff", font=ctk.CTkFont(size=10))
            lbl_value = ctk.CTkLabel(f, text=value, text_color=fg, font=ctk.CTkFont(size=18, weight="bold"))
            lbl_title.pack(anchor="w", padx=12, pady=(8,2))
            lbl_value.pack(anchor="w", padx=12, pady=(0,12))
            return f

        # placeholders; values updated in load_reports
        self.metric_rev = make_metric(metrics_box, "Total Revenue YTD", "₱0")
        self.metric_rev.grid(row=0, column=0, sticky="nsew", padx=6)
        self.metric_exp = make_metric(metrics_box, "Total Expenses YTD", "₱0")
        self.metric_exp.grid(row=0, column=1, sticky="nsew", padx=6)
        self.metric_net = make_metric(metrics_box, "Net Income YTD", "₱0")
        self.metric_net.grid(row=0, column=2, sticky="nsew", padx=6)
        self.metric_occ = make_metric(metrics_box, "Occupancy Rate", "0%")
        self.metric_occ.grid(row=0, column=3, sticky="nsew", padx=6)

        # Filter box for reports
        filter_box = ctk.CTkFrame(frame, corner_radius=8, border_width=1, border_color="#2f6fff", fg_color="#061428")
        filter_box.grid(row=1, column=0, sticky="ew", padx=8, pady=(6,12))
        filter_box.grid_columnconfigure(0, weight=1)

        filters_row = ctk.CTkFrame(filter_box, fg_color="transparent")
        filters_row.grid(row=0, column=0, sticky="ew", padx=12, pady=12)

        today = datetime.date.today()
        self.rep_year_var = tk.IntVar(value=today.year)
        self.rep_month_var = tk.IntVar(value=today.month)

        ctk.CTkLabel(filters_row, text="Start Date:").pack(side="left", padx=(0,6))
        year_e = ctk.CTkEntry(filters_row, width=100, textvariable=self.rep_year_var)
        year_e.pack(side="left", padx=(0,8))

        ctk.CTkLabel(filters_row, text="Month:").pack(side="left", padx=(4,6))
        month_e = ctk.CTkEntry(filters_row, width=60, textvariable=self.rep_month_var)
        month_e.pack(side="left", padx=(0,8))

        ctk.CTkButton(filters_row, text="Generate", width=120, command=self.load_reports).pack(side="left", padx=8)
        ctk.CTkButton(filters_row, text="Export PDF", width=120, command=lambda: None).pack(side="left", padx=8)
        ctk.CTkButton(filters_row, text="Export CSV", width=120, command=lambda: None).pack(side="left", padx=8)

        # Reports content area (bordered)
        table_box = ctk.CTkFrame(frame, corner_radius=8, border_width=1, border_color="#2f6fff", fg_color="#061428")
        table_box.grid(row=2, column=0, sticky="nsew", padx=8, pady=0)
        # reserve rows: 0 -> summary text, 1 -> label, 2 -> expanding logs table
        table_box.grid_rowconfigure(0, weight=0)
        table_box.grid_rowconfigure(1, weight=0)
        table_box.grid_rowconfigure(2, weight=1)
        table_box.grid_columnconfigure(0, weight=1)

        # ensure the white/blue treeview styles exist here (in case show_units wasn't called yet)
        try:
            style = ttk.Style()
            try:
                style.theme_use('default')
            except Exception:
                pass
            style.configure("White.Treeview", background="white", fieldbackground="white", foreground="black")
            style.configure("White.Treeview.Heading", background="#0b2a59", foreground="#9fc5ff", relief="flat", font=(None, 10, 'bold'))
            style.configure("WhiteBlueprint.Treeview", background="white", fieldbackground="white", foreground="black")
            style.configure("WhiteBlueprint.Treeview.Heading", background="#0b2a59", foreground="#9fc5ff", relief="flat", font=(None, 10, 'bold'))
        except Exception:
            pass

        # summary text area
        self.reports_text = tk.Text(table_box, height=8, font=("Segoe UI", 11), bg="#061428", fg="#cfe6ff")
        self.reports_text.grid(row=0, column=0, sticky="ew", padx=8, pady=8)

        # Activity logs below inside the same boxed container
        lbl = ctk.CTkLabel(table_box, text="Activity Logs", font=ctk.CTkFont(size=13, weight="bold"), text_color="#9fc5ff")
        lbl.grid(row=1, column=0, sticky="w", padx=8, pady=(4,2))

        cols = ("timestamp", "action", "details")
        # use the white table style so the reports table appears with white background and standard headings
        self.logs_tree = ttk.Treeview(table_box, columns=cols, show="headings", style="White.Treeview")
        for c in cols:
            self.logs_tree.heading(c, text=c.title())
            if c == "timestamp":
                self.logs_tree.column(c, minwidth=120, stretch=True, anchor="w")
            elif c == "action":
                self.logs_tree.column(c, minwidth=100, stretch=True, anchor="w")
            else:
                self.logs_tree.column(c, minwidth=200, stretch=True, anchor="w")
        self.logs_tree.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0,8))

        vsb = ttk.Scrollbar(table_box, orient="vertical", command=self.logs_tree.yview)
        self.logs_tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=2, column=1, sticky="ns", padx=(0,8), pady=(0,8))

        self.load_reports()
        self.load_activity_logs()

    def load_reports(self):
        year = self.rep_year_var.get() if hasattr(self, "rep_year_var") else datetime.date.today().year
        month = self.rep_month_var.get() if hasattr(self, "rep_month_var") else datetime.date.today().month

        income = self.payment_model.total_for_month(year, month)
        maint_cost = self.maintenance_model.total_fee_for_month(year, month)
        net_income = income - maint_cost

        # Calculate YTD (year-to-date) totals
        ytd_income = 0.0
        ytd_expenses = 0.0
        for m in range(1, month + 1):
            ytd_income += self.payment_model.total_for_month(year, m)
            ytd_expenses += self.maintenance_model.total_fee_for_month(year, m)
        ytd_net = ytd_income - ytd_expenses

        total_units = len(self.unit_model.all())
        occupied = self.db.query("SELECT COUNT(*) as c FROM units WHERE status='Occupied'")[0]["c"]
        occupancy_rate = (occupied / total_units * 100) if total_units > 0 else 0.0

        if hasattr(self, "metric_rev"):
            for child in self.metric_rev.winfo_children():
                if isinstance(child, ctk.CTkLabel) and "₱" not in child.cget("text"):
                    continue
                if isinstance(child, ctk.CTkLabel):
                    child.configure(text=f"₱{ytd_income:,.2f}")
                    break
        
        if hasattr(self, "metric_exp"):
            for child in self.metric_exp.winfo_children():
                if isinstance(child, ctk.CTkLabel) and "₱" not in child.cget("text"):
                    continue
                if isinstance(child, ctk.CTkLabel):
                    child.configure(text=f"₱{ytd_expenses:,.2f}")
                    break
        
        if hasattr(self, "metric_net"):
            for child in self.metric_net.winfo_children():
                if isinstance(child, ctk.CTkLabel) and "₱" not in child.cget("text"):
                    continue
                if isinstance(child, ctk.CTkLabel):
                    child.configure(text=f"₱{ytd_net:,.2f}")
                    break
        
        if hasattr(self, "metric_occ"):
            for child in self.metric_occ.winfo_children():
                if isinstance(child, ctk.CTkLabel) and "%" not in child.cget("text"):
                    continue
                if isinstance(child, ctk.CTkLabel):
                    child.configure(text=f"{occupancy_rate:.1f}%")
                    break

        lines = []
        lines.append(f"REPORTS FOR {year}-{month:02d}")
        lines.append("=" * 40)
        lines.append("")
        lines.append(f"Total Billing Collected (Paid) This Month: ₱{income:.2f}")
        lines.append(f"Total Maintenance Fees This Month: ₱{maint_cost:.2f}")
        lines.append(f"Net Income This Month: ₱{net_income:.2f}")
        lines.append("")
        lines.append(f"Revenue: ₱{ytd_income:,.2f}")
        lines.append(f"Expenses: ₱{ytd_expenses:,.2f}")
        lines.append(f"Net Income: ₱{ytd_net:,.2f}")
        lines.append("")
        lines.append(f"Occupancy Rate: {occupancy_rate:.1f}% ({occupied}/{total_units} units)")
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

    def load_activity_logs(self):
        if not hasattr(self, "logs_tree"):
            return
        for r in self.logs_tree.get_children():
            self.logs_tree.delete(r)
        rows = self.activity_model.all()
        for row in rows:
            self.logs_tree.insert(
                "",
                tk.END,
                values=(row["timestamp"], row["action"], row["details"] or ""),
            )

    def export_logs_excel(self):
        if Workbook is None:
            messagebox.showwarning("Excel", "openpyxl is not installed. Install it with 'pip install openpyxl'.", parent=self)
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            title="Save Activity Logs Excel"
        )
        if not path:
            return
        wb = Workbook()
        ws = wb.active
        ws.title = "Activity Logs"
        ws.append(["Log ID", "Timestamp", "Action", "Details"])
        for row in self.activity_model.all():
            ws.append([row["log_id"], row["timestamp"], row["action"], row["details"] or ""])
        wb.save(path)
        messagebox.showinfo("Saved", f"Logs exported to {path}", parent=self)

    def clear_logs(self):
        if not messagebox.askyesno("Clear Logs", "Are you sure you want to clear all activity logs?", parent=self):
            return
        self.activity_model.clear()
        self.load_activity_logs()
        messagebox.showinfo("Cleared", "All activity logs have been cleared.", parent=self)

    def backup_database(self):
        from shutil import copy2
        path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database Files", "*.db"), ("All Files", "*.*")],
            title="Save Database Backup"
        )
        if not path:
            return
        try:
            copy2(self.db.db_file, path)
            self.log_action("Backup Database", f"Backup saved to {path}")
            messagebox.showinfo("Backup", f"Database backup saved to {path}", parent=self)
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to backup database:\n{e}", parent=self)

    def restore_database(self):
        from shutil import copy2
        if not messagebox.askyesno(
            "Restore Database",
            "Restoring a backup will overwrite the current data. Continue?",
            parent=self,
        ):
            return
        path = filedialog.askopenfilename(
            filetypes=[("Database Files", "*.db"), ("All Files", "*.*")],
            title="Select Database Backup to Restore"
        )
        if not path:
            return
        try:
            self.db.close()
        except Exception:
            pass
        try:
            copy2(path, self.db.db_file)
            messagebox.showinfo(
                "Restore",
                "Database has been restored. Please restart the application to apply changes.",
                parent=self,
            )
        except Exception as e:
            messagebox.showerror("Restore Error", f"Failed to restore database:\n{e}", parent=self)

    def show_policy(self):
        PolicyDialog(self)

    def change_password(self):
        dlg = ChangePasswordDialog(self, self.db)
        self.wait_window(dlg)

    def show_settings(self):
        txt = (
            "Settings:\n\n"
            "- UI Theme: Toggle using 'Toggle Theme' button.\n"
            "- Other settings can be added here."
        )
        messagebox.showinfo("Settings", txt, parent=self)
        
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
