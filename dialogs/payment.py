import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

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
