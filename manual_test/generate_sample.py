#!/usr/bin/env python3
"""Generate a synthetic OTP XLSX export for manual testing.

This mimics the structure the `otp` plugin expects from the current OTP netbank
export:

  * a sheet named ``Tranzakciók``
  * a metadata preamble (title + labelled cells for account numbers and the
    query start/end dates)
  * a transaction table header, followed by data rows
  * 11 columns (A-K) in the order of the ``Transaction`` dataclass in
    ``src/ofxstatement_otp/otp.py``
  * two distinct account numbers (so the ``account`` filter can be exercised),
    plus a hidden row and a no-booking-date row for the skip paths

It is NOT real bank data -- all account numbers, names and amounts are made up.
It doubles as the committable, anonymized fixture the tests run against.

Usage:
    python manual_test/generate_sample.py [output.xlsx]
"""
import sys
from datetime import datetime

from openpyxl import Workbook

TRANSACTIONS_SHEET_NAME = "Tranzakciók"

# Two fake accounts so the account filter has something to split on.
ACCOUNT_CHECKING = "11111111-22222222"
ACCOUNT_CREDIT = "33333333-44444444"

# Metadata preamble. Each entry is (label in column A, value in column B).
# The parser locates these by label, so the exact rows don't matter.
PREAMBLE = [
    ("Számlatörténet", None),
    (None, None),
    ("Számlaszám", f"[{ACCOUNT_CHECKING}, {ACCOUNT_CREDIT}]"),
    ("Lekérdezés időpontja", "2024-02-01 10:00:00"),
    ("Lekérdezés kezdete", "2024-01-01"),
    ("Lekérdezés vége", "2024-01-31"),
    ("Szűrési feltétel", "számla szűrővel: []"),
    (None, None),
]

# Transaction table header (row order must match the Transaction dataclass).
HEADER = [
    "Számlaszám",
    "Ellenoldali számlaszám",
    "Ellenoldali név",
    "Forgalom típusa",
    "Közlemény",
    "Tranzakció kategória",
    "Banki azonosító",
    "Tranzakció időpontja",
    "Könyvelés dátuma",
    "Összeg",
    "Devizanem",
]

# Data rows. Column H (transaction datetime) is written as a string, except one
# row that uses a native datetime to exercise both code paths. Amounts are
# signed floats, as in the real export.
ROWS = [
    [ACCOUNT_CHECKING, "", "SPAR MAGYARORSZAG KFT", "VÁSÁRLÁS KÁRTYÁVAL", "SPAR vásárlás", "Élelmiszer", "2024010209150011001", "2024-01-02 09:15:00", "2024-01-02", -4990.00, "HUF"],
    [ACCOUNT_CHECKING, "11600006-00000000-87654321", "Példa János", "NAPKÖZBENI ÁTUTALÁS", "Lakbér január", "Átutalás", "2024010312000011002", "2024-01-03 12:00:00", "2024-01-03", -120000.00, "HUF"],
    [ACCOUNT_CHECKING, "10300002-00000000-11112222", "Munkáltató Zrt.", "AZONNALI ÁTUTALÁS", "Munkabér", "Fizetés", "2024010508300011003", "2024-01-05 08:30:00", "2024-01-05", 450000.00, "HUF"],
    # Native datetime cell (not a string) to exercise _to_datetime's datetime branch.
    [ACCOUNT_CHECKING, "", "MOL TOLTOALLOMAS", "VÁSÁRLÁS KÁRTYÁVAL", "Tankolás", "Üzemanyag", "2024010718450011004", datetime(2024, 1, 7, 18, 45, 0), "2024-01-07", -15500.50, "HUF"],
    [ACCOUNT_CHECKING, "", "OTP Bank", "ZÁRLATI DÍJ", "Számlavezetési díj", "Bankköltség", "2024011000000011005", "2024-01-10 00:00:00", "2024-01-10", -1290.00, "HUF"],
    [ACCOUNT_CHECKING, "", "Valami Bolt", "ISMERETLEN TRANZAKCIÓ TÍPUS", "Ismeretlen típus -> PAYMENT", "Egyéb", "2024011510050011006", "2024-01-15 10:05:00", "2024-01-15", -2500.00, "HUF"],
    # A second account -- only emitted when no filter (or the credit filter) is set.
    [ACCOUNT_CREDIT, "", "MEDIA MARKT", "VÁSÁRLÁS KÁRTYÁVAL", "Mosógép", "Műszaki cikk", "2024011214200012001", "2024-01-12 14:20:00", "2024-01-12", -89990.00, "HUF"],
    [ACCOUNT_CREDIT, "", "OTP Bank", "KAMATJÓVÁÍRÁS", "Havi kamat", "Kamat", "2024011811300012002", "2024-01-18 11:30:00", "2024-01-18", 12.50, "HUF"],
]

# SKIPPED: no booking date (column I empty), e.g. a pending item.
INCOMPLETE_ROW = [ACCOUNT_CHECKING, "", "Pending", "FÜGGŐ TÉTEL", "Nem könyvelt tétel", "Egyéb", "2024012000000011099", "2024-01-20 00:00:00", None, -999.00, "HUF"]

# SKIPPED: hidden row (netbank filter artifact).
HIDDEN_ROW = [ACCOUNT_CHECKING, "", "REJTETT SOR", "VÁSÁRLÁS KÁRTYÁVAL", "Ez a sor el van rejtve", "Rejtett", "2024012216000011098", "2024-01-22 16:00:00", "2024-01-22", -7777.00, "HUF"]


def build_workbook() -> Workbook:
    wb = Workbook()
    ws = wb.active
    ws.title = TRANSACTIONS_SHEET_NAME

    for label, value in PREAMBLE:
        ws.append([label, value])

    ws.append(HEADER)
    for row in ROWS:
        ws.append(row)

    # A hidden row, to exercise the hidden-row skipping logic.
    ws.append(HIDDEN_ROW)
    ws.row_dimensions[ws.max_row].hidden = True

    # An incomplete row (no booking date), to exercise that skip path.
    ws.append(INCOMPLETE_ROW)

    return wb


def main() -> None:
    out = sys.argv[1] if len(sys.argv) > 1 else "manual_test/sample.xlsx"
    wb = build_workbook()
    wb.save(out)
    print(f"Wrote sample OTP export to {out}")


if __name__ == "__main__":
    main()
