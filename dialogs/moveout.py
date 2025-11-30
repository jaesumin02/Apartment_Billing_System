import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

class MoveOutDialog(ctk.CTkToplevel):
    def __init__(self, parent, tenant_name):
        super().__init__(parent)
        self.saved = False
        self.reason = ""
        self.date = __import__('datetime').date.today().isoformat()

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
