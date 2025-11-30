import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from constants import DORM_DEFAULT_CAPACITY

class UnitEditDialog(ctk.CTkToplevel):
    def __init__(self, parent, unit=None):
        super().__init__(parent)
        self.unit = unit or {}
        self.result = {}
        self.saved = False
        title = f"Edit Unit - {self.unit.get('unit_code')}" if self.unit.get('unit_code') else "Add Unit"
        self.title(title)
        self.geometry("480x300")
        self.resizable(False, False)
        self.build_ui()
        self.transient(parent)
        self.grab_set()

    def build_ui(self):
        frm = ctk.CTkFrame(self, corner_radius=12)
        frm.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(frm, text="Unit Code", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.code_e = ctk.CTkEntry(frm, width=160)
        if self.unit.get('unit_code'):
            self.code_e.insert(0, str(self.unit.get('unit_code')))
        self.code_e.grid(row=0, column=1, sticky="w", padx=6, pady=4)

        ctk.CTkLabel(frm, text="Unit Type").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self.type_cmb = ctk.CTkComboBox(frm, values=["Solo", "Family", "Dorm"], width=200)
        self.type_cmb.set(self.unit.get('unit_type') or 'Solo')
        self.type_cmb.grid(row=1, column=1, sticky="w", padx=6, pady=4)

        ctk.CTkLabel(frm, text="Price").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        self.price_e = ctk.CTkEntry(frm, width=160)
        self.price_e.insert(0, str(self.unit.get('price') or 0.0))
        self.price_e.grid(row=2, column=1, sticky="w", padx=6, pady=4)

        ctk.CTkLabel(frm, text="Capacity").grid(row=3, column=0, sticky="w", padx=6, pady=4)
        self.cap_e = ctk.CTkEntry(frm, width=120)
        self.cap_e.insert(0, str(self.unit.get('capacity') or DORM_DEFAULT_CAPACITY))
        self.cap_e.grid(row=3, column=1, sticky="w", padx=6, pady=4)

        btn_fr = ctk.CTkFrame(frm, fg_color="transparent")
        btn_fr.grid(row=4, column=0, columnspan=2, pady=12)
        ctk.CTkButton(btn_fr, text="Save", width=120, command=self.on_save).pack(side="left", padx=6)
        ctk.CTkButton(btn_fr, text="Cancel", width=100, fg_color="#555555", command=self.destroy).pack(side="left", padx=6)

    def on_save(self):
        code = self.code_e.get().strip()
        if not code:
            messagebox.showwarning("Input", "Unit code is required.", parent=self)
            return
        try:
            price = float(self.price_e.get().strip() or 0)
        except ValueError:
            messagebox.showwarning("Input", "Price must be numeric.", parent=self)
            return
        try:
            cap = int(self.cap_e.get().strip() or 0)
        except ValueError:
            messagebox.showwarning("Input", "Capacity must be an integer.", parent=self)
            return
        if cap < 0:
            messagebox.showwarning("Input", "Capacity cannot be negative.", parent=self)
            return

        self.result = {
            'unit_id': self.unit.get('unit_id'),
            'unit_code': code,
            'unit_type': self.type_cmb.get(),
            'price': price,
            'capacity': cap,
        }
        self.saved = True
        self.destroy()
