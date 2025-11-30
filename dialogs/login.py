import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

class LoginDialog(ctk.CTkToplevel):
    def __init__(self, parent, db):
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
