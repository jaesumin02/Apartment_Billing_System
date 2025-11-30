import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from dialogs.receipt import format_receipt

sample = {
    "payment_id": 123,
    "tenant_id": 45,
    "name": "Juan Dela Cruz",
    "date_paid": "2025-11-30",
    "status": "Paid",
    "note": "November rent",
    "rent": 4500.0,
    "electricity": 150.0,
    "water": 80.0,
}

print(format_receipt(sample))
