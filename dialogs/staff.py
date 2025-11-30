import customtkinter as ctk
from tkinter import messagebox

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
        ctk.CTkButton(btn_frame, text="Cancel", width=100, fg_color="#555555", command=self.destroy).pack(side="left", padx=4)

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
