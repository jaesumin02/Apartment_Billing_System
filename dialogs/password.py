import customtkinter as ctk
from tkinter import messagebox

class ChangePasswordDialog(ctk.CTkToplevel):
    def __init__(self, parent, db):
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
