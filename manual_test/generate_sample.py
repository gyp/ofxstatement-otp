#!/usr/bin/env python3
"""Generate a synthetic OTP XLSX export for manual testing.

This produces a workbook that mimics the structure the `otp` plugin expects
(post-2021-September OTP netbank export):

  * a sheet named ``Tranzakciók``
  * a header in row 1, transaction data from row 2 onwards
  * 12 columns (A-L) in the order of the ``Transaction`` dataclass in
    ``src/ofxstatement_otp/otp.py``

It is NOT real bank data -- all names, accounts and amounts are made up. It
exists only so the plugin can be exercised end-to-end without a real export.

Usage:
    python manual_test/generate_sample.py [output.xlsx]
"""
import sys
from openpyxl import Workbook

TRANSACTIONS_SHEET_NAME = "Tranzakciók"

# Column order must match the Transaction dataclass:
# transaction_date, booking_date, description, in_or_out, partner_name,
# partner_account, otp_generated_category, memo, account_name, account_no,
# amount, currency
HEADER = [
    "Tranzakció dátuma",
    "Könyvelés dátuma",
    "Megnevezés",
    "Be/Ki",
    "Partner neve",
    "Partner számlaszáma",
    "Kategória",
    "Közlemény",
    "Számla neve",
    "Számlaszám",
    "Összeg",
    "Pénznem",
]

# Dates are written as strings because the parser calls datetime.strptime on
# them ('%Y-%m-%d %H:%M:%S' for column A, '%Y-%m-%d' for column B).
ROWS = [
    ["2024-01-02 09:15:00", "2024-01-02", "VÁSÁRLÁS KÁRTYÁVAL", "K", "SPAR MAGYARORSZAG KFT", "", "Élelmiszer", "SPAR vásárlás", "Lakossági számla", "11773016-12345678", -4990.00, "HUF"],
    ["2024-01-03 12:00:00", "2024-01-03", "NAPKÖZBENI ÁTUTALÁS", "K", "Kovács János", "11600006-00000000-87654321", "Átutalás", "Lakbér január", "Lakossági számla", "11773016-12345678", -120000.00, "HUF"],
    ["2024-01-05 08:30:00", "2024-01-05", "AZONNALI ÁTUTALÁS", "J", "Munkáltató Zrt.", "10300002-00000000-11112222", "Fizetés", "Munkabér", "Lakossági számla", "11773016-12345678", 450000.00, "HUF"],
    ["2024-01-07 18:45:00", "2024-01-07", "VÁSÁRLÁS KÁRTYÁVAL", "K", "MOL TOLTOALLOMAS", "", "Üzemanyag", "Tankolás", "Lakossági számla", "11773016-12345678", -15500.50, "HUF"],
    ["2024-01-10 00:00:00", "2024-01-10", "ZÁRLATI DÍJ", "K", "OTP Bank", "", "Bankköltség", "Számlavezetési díj", "Lakossági számla", "11773016-12345678", -1290.00, "HUF"],
    ["2024-01-12 14:20:00", "2024-01-12", "ÁRUVISSZAVÉT ELLENÉRTÉKE", "J", "MEDIA MARKT", "", "Visszatérítés", "Termék visszavét", "Lakossági számla", "11773016-12345678", 29990.00, "HUF"],
    ["2024-01-15 10:05:00", "2024-01-15", "ISMERETLEN TRANZAKCIÓ TÍPUS", "K", "Valami Bolt", "", "Egyéb", "Ismeretlen típus -> PAYMENT", "Lakossági számla", "11773016-12345678", -2500.00, "HUF"],
    ["2024-01-18 11:30:00", "2024-01-18", "KAMATJÓVÁÍRÁS", "J", "OTP Bank", "", "Kamat", "Havi kamat", "Lakossági számla", "11773016-12345678", 12.50, "HUF"],
]

# A row that should be SKIPPED because its booking date (column B) is empty.
INCOMPLETE_ROW = ["2024-01-20 00:00:00", None, "FÜGGŐ TÉTEL", "K", "Pending", "", "", "Nem könyvelt tétel", "Lakossági számla", "11773016-12345678", -999.00, "HUF"]

# A row that should be SKIPPED because it is hidden (netbank filter artifact).
HIDDEN_ROW = ["2024-01-22 16:00:00", "2024-01-22", "VÁSÁRLÁS KÁRTYÁVAL", "K", "REJTETT SOR", "", "Rejtett", "Ez a sor el van rejtve", "Lakossági számla", "11773016-12345678", -7777.00, "HUF"]


def build_workbook() -> Workbook:
    wb = Workbook()
    ws = wb.active
    ws.title = TRANSACTIONS_SHEET_NAME

    ws.append(HEADER)
    for row in ROWS:
        ws.append(row)

    # Add a hidden row to exercise the hidden-row skipping logic.
    ws.append(HIDDEN_ROW)
    ws.row_dimensions[ws.max_row].hidden = True

    # Add an incomplete row (no booking date) to exercise that skip path.
    ws.append(INCOMPLETE_ROW)

    return wb


def main() -> None:
    out = sys.argv[1] if len(sys.argv) > 1 else "manual_test/sample.xlsx"
    wb = build_workbook()
    wb.save(out)
    print(f"Wrote sample OTP export to {out}")


if __name__ == "__main__":
    main()
