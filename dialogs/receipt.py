import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas as pdf_canvas
except ImportError:
    pdf_canvas = None
import os
import tempfile


def format_receipt(payment_row: dict) -> str:
    try:
        pr = dict(payment_row)
    except Exception:
        pr = payment_row

    WIDTH = 60
    sep = "=" * WIDTH
    dash = "-" * WIDTH
    receipt_text = sep + "\n"
    receipt_text += "PAYMENT RECEIPT".center(WIDTH) + "\n"
    receipt_text += sep + "\n\n"

    payment_id = pr.get("payment_id") or "N/A"
    tenant_id = pr.get("tenant_id") or "N/A"
    receipt_text += f"Receipt No.:    {payment_id}\n"
    receipt_text += f"Tenant ID:      {tenant_id}\n"

    name = pr.get("name") or ""
    if name:
        receipt_text += f"Tenant:         {name}\n"

    date_paid = pr.get("date_paid") or "Not Paid"
    receipt_text += f"Date Paid:      {date_paid}\n"
    status = (pr.get("status") or "Due").upper()
    receipt_text += f"Status:         {status}\n"

    note = pr.get("note") or ""
    if note:
        receipt_text += f"Note:           {note}\n"

    receipt_text += "\n" + dash + "\n"
    receipt_text += "CHARGES & PAYMENTS:\n"
    receipt_text += dash + "\n"

    rent = float(pr.get("rent") or 0.0)
    electricity = float(pr.get("electricity") or 0.0)
    water = float(pr.get("water") or 0.0)

    receipt_text += f"Rent:           ₱{rent:>12.2f}\n"
    receipt_text += f"Electricity:    ₱{electricity:>12.2f}\n"
    receipt_text += f"Water:          ₱{water:>12.2f}\n"
    receipt_text += dash + "\n"

    total = rent + electricity + water
    receipt_text += f"TOTAL BILL:     ₱{total:>12.2f}\n"
    receipt_text += sep + "\n\n"
    receipt_text += "Thank you for your payment!\n"
    return receipt_text

class ReceiptDialog(ctk.CTkToplevel):
    def __init__(self, parent, payment_row):
        super().__init__(parent)
        # normalize mapping (accept sqlite3.Row)
        try:
            self.payment_row = dict(payment_row)
        except Exception:
            self.payment_row = payment_row

        pid = self.payment_row.get("payment_id") or "N/A"
        self.title(f"Receipt - Payment #{pid}")
        # Larger default size for better readability
        self.geometry("720x560")
        self.resizable(True, True)
        # Make it visually prominent
        try:
            self.attributes("-topmost", True)
        except Exception:
            pass

        self.build_ui()
        self.transient(parent)
        self.grab_set()
        try:
            self.lift()
            self.focus_force()
        except Exception:
            pass
        try:
            self.after(800, lambda: self.attributes("-topmost", False))
        except Exception:
            pass

    def build_ui(self):
        frm = ctk.CTkFrame(self, corner_radius=12)
        frm.pack(fill="both", expand=True, padx=16, pady=16)

        title_lbl = ctk.CTkLabel(frm, text="PAYMENT RECEIPT", font=ctk.CTkFont(size=16, weight="bold"))
        title_lbl.pack(pady=(4, 8))

        receipt_text = format_receipt(self.payment_row)

        text_frame = ctk.CTkFrame(frm, corner_radius=6)
        text_frame.pack(fill="both", expand=True, pady=(4, 8))

        self.text_box = tk.Text(
            text_frame,
            height=20,
            width=80,
            bg="white",
            fg="black",
            font=("Courier New", 12),
            relief="flat",
            borderwidth=0,
            wrap="word"
        )
        self.text_box.pack(fill="both", expand=True, padx=1, pady=1)
        self.text_box.insert("1.0", receipt_text)
        self.text_box.config(state="disabled")

        btn_fr = ctk.CTkFrame(frm, fg_color="transparent")
        btn_fr.pack(pady=(6, 2))

        ctk.CTkButton(btn_fr, text="Save as PDF", width=120, command=self.save_pdf).pack(side="left", padx=6)
        ctk.CTkButton(btn_fr, text="Print", width=100, command=self.print_receipt).pack(side="left", padx=6)
        ctk.CTkButton(btn_fr, text="Close", width=100, fg_color="#555555", command=self.destroy).pack(side="left", padx=6)

    def print_receipt(self):
        if pdf_canvas is None:
            messagebox.showwarning(
                "PDF Library Missing",
                "reportlab is required to print receipts. Install it with 'pip install reportlab'.",
                parent=self,
            )
            return
        import tempfile
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp.close()
        path = tmp.name
        c = pdf_canvas.Canvas(path, pagesize=A4)
        width, height = A4
        y = height - 50
        lines = self.text_box.get("1.0", "end-1c").splitlines()
        for line in lines:
            c.drawString(40, y, line)
            y -= 18
            if y < 40:
                c.showPage()
                y = height - 50
        c.showPage()
        c.save()
        try:
            if hasattr(os, "startfile"):
                os.startfile(path, "print")
                messagebox.showinfo("Print", "Receipt sent to the default printer.", parent=self)
            else:
                messagebox.showinfo("Print", f"Receipt saved to {path}. Please open and print it manually.", parent=self)
        except Exception:
            messagebox.showinfo("Print", f"Receipt saved to {path}. Please open and print it manually.", parent=self)

    def save_pdf(self):
        if pdf_canvas is None:
            messagebox.showwarning("PDF Library Missing", "reportlab is required to generate PDF receipts. Install it with 'pip install reportlab'.", parent=self)
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Save receipt PDF"
        )
        if not path:
            return

        c = pdf_canvas.Canvas(path, pagesize=A4)
        width, height = A4
        y = height - 50
        lines = self.text_box.get("1.0", "end-1c").splitlines()
        for line in lines:
            c.drawString(40, y, line)
            y -= 18
            if y < 40:
                c.showPage()
                y = height - 50
        c.showPage()
        c.save()
        messagebox.showinfo("Saved", f"Receipt saved to {path}", parent=self)
