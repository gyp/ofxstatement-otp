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
  * several distinct account numbers (so the ``account`` filter can be
    exercised), including a credit-card account whose number is longer than
    the current-account ones and a declared account with no activity at all,
    plus a hidden row and no-booking-date rows for the skip paths

It is NOT real bank data -- all account numbers, names and amounts are made up.
It doubles as the committable, anonymized fixture the tests run against.

Usage:
    python manual_test/generate_sample.py [output.xlsx]
"""
import sys
from datetime import datetime

from openpyxl import Workbook

TRANSACTIONS_SHEET_NAME = "Tranzakciók"

# Fake accounts so the account filter has something to split on. The real
# export writes account numbers unformatted (no dashes) and credit-card
# accounts carry a longer number than current accounts.
ACCOUNT_CHECKING = "1111111122222222"
ACCOUNT_CREDIT = "333333334444444455555555"
# Declared in the preamble but with no transactions in the queried period.
ACCOUNT_DORMANT = "6666666677777777"

# Metadata preamble. Each entry is (label in column A, value in column B).
# The parser locates these by label, so the exact rows don't matter.
PREAMBLE = [
    ("Számlatörténet", None),
    (None, None),
    (
        "Számlaszám",
        f"[{ACCOUNT_CHECKING}, {ACCOUNT_CREDIT}, {ACCOUNT_DORMANT}]",
    ),
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
    [ACCOUNT_CHECKING, "116000060000000087654321", "Példa János", "NAPKÖZBENI ÁTUTALÁS", "Lakbér január", "Átutalás", "2024010312000011002", "2024-01-03 12:00:00", "2024-01-03", -120000.00, "HUF"],
    [ACCOUNT_CHECKING, "103000020000000011112222", "Munkáltató Zrt.", "AZONNALI ÁTUTALÁS", "Munkabér", "Fizetés", "2024010508300011003", "2024-01-05 08:30:00", "2024-01-05", 450000.00, "HUF"],
    # Native datetime cell (not a string) to exercise _to_datetime's datetime branch.
    [ACCOUNT_CHECKING, "", "MOL TOLTOALLOMAS", "VÁSÁRLÁS KÁRTYÁVAL", "Tankolás", "Üzemanyag", "2024010718450011004", datetime(2024, 1, 7, 18, 45, 0), "2024-01-07", -15500.50, "HUF"],
    [ACCOUNT_CHECKING, "", "OTP Bank", "ZÁRLATI DÍJ", "Számlavezetési díj", "Bankköltség", "2024011000000011005", "2024-01-10 00:00:00", "2024-01-10", -1290.00, "HUF"],
    [ACCOUNT_CHECKING, "", "Valami Bolt", "ISMERETLEN TRANZAKCIÓ TÍPUS", "Ismeretlen típus -> PAYMENT", "Egyéb", "2024011510050011006", "2024-01-15 10:05:00", "2024-01-15", -2500.00, "HUF"],
    # The credit-card repayment shows up on both accounts: the paying current
    # account references the card's account number in column B, and the card
    # account books the matching credit. The description here is written with
    # the doubled inner spaces the real export uses.
    [ACCOUNT_CHECKING, ACCOUNT_CREDIT, "Hitelkártyaszámla", "QVIK  FIZETÉS  BANKON BELÜL", "", "Nem kategorizált", "2024012007320011007", "2024-01-20 07:32:14", "2024-01-20", -13562.00, "HUF"],
    # The credit-card account -- only emitted when no filter (or the credit
    # filter) is set.
    [ACCOUNT_CREDIT, "", "MEDIA MARKT", "VÁSÁRLÁS KÁRTYÁVAL", "Mosógép", "Műszaki cikk", "2024011214200012001", "2024-01-12 14:20:00", "2024-01-12", -89990.00, "HUF"],
    [ACCOUNT_CREDIT, "", "OTP Bank", "KAMATJÓVÁÍRÁS", "Havi kamat", "Kamat", "2024011811300012002", "2024-01-18 11:30:00", "2024-01-18", 12.50, "HUF"],
    [ACCOUNT_CREDIT, ACCOUNT_CHECKING, "PÉLDA JÁNOS", "HITELTÖRLESZTÉS BEFIZETÉS / ÁTUTALÁ", "HITELTÖRLESZTÉS BEFIZETÉS / ÁTUTALÁS", "Nem kategorizált", "20240120073000156503925BATCH", "2024-01-20 07:30:15", "2024-01-20", 13562.00, "HUF"],
    [ACCOUNT_CREDIT, "", "BANKKÁRTYA ÉVES DÍJ", "BANKKÁRTYA ÉVES DÍJ", "BANKKÁRTYA ÉVES DÍJ", "Egyéb", "20240124074800630315339BATCH", "2024-01-24 07:48:34", "2024-01-24", -6862.00, "HUF"],
]

# SKIPPED: no booking date, e.g. a pending item. The real export leaves the
# cell either empty or as an empty string, so both variants appear here.
INCOMPLETE_ROWS = [
    [ACCOUNT_CHECKING, "", "Pending", "FÜGGŐ TÉTEL", "Nem könyvelt tétel", "Egyéb", "2024012000000011099", "2024-01-20 00:00:00", None, -999.00, "HUF"],
    [ACCOUNT_CHECKING, "", "Zárolt tétel", "", "", "Egyéb", "2024012500000011097", "2024-01-25 00:00:00", "", -888.00, "HUF"],
]

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

    # Incomplete rows (no booking date), to exercise that skip path.
    for row in INCOMPLETE_ROWS:
        ws.append(row)

    return wb


def main() -> None:
    out = sys.argv[1] if len(sys.argv) > 1 else "manual_test/sample.xlsx"
    wb = build_workbook()
    wb.save(out)
    print(f"Wrote sample OTP export to {out}")


if __name__ == "__main__":
    main()
