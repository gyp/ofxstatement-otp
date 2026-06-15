"""Tests for the current OTP XLSX parser.

The fixture is the synthetic export produced by
``manual_test/generate_sample.py`` -- the same anonymized structure as a real
post-2021 OTP netbank export.
"""

import importlib.util
import re
import sys
import warnings
import zipfile
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from ofxstatement_otp.otp import OtpXlsxParser

REPO_ROOT = Path(__file__).resolve().parent.parent

# Load manual_test/generate_sample.py (not a package) to reuse build_workbook.
_spec = importlib.util.spec_from_file_location(
    "generate_sample", REPO_ROOT / "manual_test" / "generate_sample.py"
)
assert _spec is not None and _spec.loader is not None
generate_sample = importlib.util.module_from_spec(_spec)
sys.modules["generate_sample"] = generate_sample
_spec.loader.exec_module(generate_sample)

CHECKING = generate_sample.ACCOUNT_CHECKING
CREDIT = generate_sample.ACCOUNT_CREDIT


@pytest.fixture
def sample_xlsx(tmp_path):
    path = tmp_path / "sample.xlsx"
    generate_sample.build_workbook().save(path)
    return str(path)


def parse(filename, settings=None):
    parser = OtpXlsxParser(filename, settings or {})
    return parser.statement, parser.parse()


def _strip_named_styles(path):
    """Rewrite an xlsx in place so its stylesheet has no named styles.

    This reproduces the real OTP export, which makes openpyxl emit
    "Workbook contains no default style, apply openpyxl's default".
    """
    with zipfile.ZipFile(path) as zin:
        items = {name: zin.read(name) for name in zin.namelist()}
    items["xl/styles.xml"] = re.sub(
        rb"<cellStyles[ >].*?</cellStyles>", b"", items["xl/styles.xml"], flags=re.S
    )
    with zipfile.ZipFile(path, "w") as zout:
        for name, data in items.items():
            zout.writestr(name, data)


def test_no_openpyxl_default_style_warning(sample_xlsx):
    _strip_named_styles(sample_xlsx)
    # Sanity check: a raw load of this file *does* warn.
    with warnings.catch_warnings(record=True) as raw:
        warnings.simplefilter("always")
        from openpyxl import load_workbook

        load_workbook(sample_xlsx)
    assert any("no default style" in str(w.message) for w in raw)

    # The parser must not surface that warning to the user.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        parse(sample_xlsx, {"account": CHECKING})
    assert not any("no default style" in str(w.message) for w in caught)


def test_unfiltered_includes_all_accounts(sample_xlsx):
    statement, result = parse(sample_xlsx)
    # 8 data rows; the hidden row and the no-booking-date row are skipped.
    assert len(result.lines) == 8
    accounts = {line.payee for line in result.lines}
    assert "MEDIA MARKT" in accounts  # a credit-account line is present


def test_account_filter_selects_one_account(sample_xlsx):
    statement, result = parse(sample_xlsx, {"account": CHECKING})
    assert len(result.lines) == 6  # only the checking-account rows
    assert statement.account_id == CHECKING
    # The credit-only payee must not appear.
    assert all(line.payee != "MEDIA MARKT" for line in result.lines)


def test_account_filter_is_substring_and_case_insensitive(sample_xlsx):
    # CREDIT is "33333333-44444444"; match on a lowercase substring.
    _, result = parse(sample_xlsx, {"account": "33333333"})
    assert len(result.lines) == 2
    assert all(line.payee in {"MEDIA MARKT", "OTP Bank"} for line in result.lines)


def test_account_id_unset_when_filter_matches_nothing(sample_xlsx):
    # A filter that matches no account must not pass itself off as the
    # statement's account_id; it should be left unset.
    statement, result = parse(sample_xlsx, {"account": "99999999"})
    assert result.lines == []
    assert statement.account_id is None


def test_fitid_comes_from_bank_identifier(sample_xlsx):
    _, result = parse(sample_xlsx, {"account": CHECKING})
    first = result.lines[0]
    assert first.id == "2024010209150011001"


def test_statement_dates_from_preamble(sample_xlsx):
    statement, _ = parse(sample_xlsx)
    assert statement.start_date == datetime(2024, 1, 1)
    assert statement.end_date == datetime(2024, 1, 31)


def test_amount_and_currency(sample_xlsx):
    statement, result = parse(sample_xlsx, {"account": CHECKING})
    assert statement.currency == "HUF"
    assert result.lines[0].amount == Decimal("-4990.00")


def test_trntype_mapping(sample_xlsx):
    _, result = parse(sample_xlsx, {"account": CHECKING})
    by_payee = {line.payee: line for line in result.lines}
    assert by_payee["SPAR MAGYARORSZAG KFT"].trntype == "POS"
    assert by_payee["Példa János"].trntype == "XFER"
    # Unknown description falls back to PAYMENT.
    assert by_payee["Valami Bolt"].trntype == "PAYMENT"


def test_missing_transaction_datetime_does_not_crash(tmp_path):
    # A booked row (booking date present) whose transaction datetime is blank
    # must still be emitted, with date_user unset, rather than crashing.
    wb = generate_sample.build_workbook()
    ws = wb[generate_sample.TRANSACTIONS_SHEET_NAME]
    ws.append(
        [
            CHECKING,
            "",
            "NO TXN TIME",
            "VÁSÁRLÁS KÁRTYÁVAL",
            "memo",
            "Egyéb",
            "2024012909999011010",
            None,
            "2024-01-29",
            -100.00,
            "HUF",
        ]
    )
    path = tmp_path / "sample.xlsx"
    wb.save(path)

    _, result = parse(str(path), {"account": CHECKING})
    line = next(line for line in result.lines if line.payee == "NO TXN TIME")
    assert line.date == datetime(2024, 1, 29)
    assert line.date_user is None


def test_native_datetime_cell_is_parsed(sample_xlsx):
    # The MOL row uses a native datetime cell for the transaction date.
    _, result = parse(sample_xlsx, {"account": CHECKING})
    mol = next(line for line in result.lines if line.payee == "MOL TOLTOALLOMAS")
    assert mol.date_user == datetime(2024, 1, 7, 18, 45, 0)
    assert mol.date == datetime(2024, 1, 7)
