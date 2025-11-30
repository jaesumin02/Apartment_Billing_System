import customtkinter as ctk
import tkinter as tk

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
            "4. Damage to property may incur maintenance fees."
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
