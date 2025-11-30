import customtkinter as ctk
from tkinter import messagebox

class MaintenanceDialog(ctk.CTkToplevel):
    def __init__(self, parent, staff_model):
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
