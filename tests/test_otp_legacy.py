"""Tests for the ``otp_legacy`` plugin.

``otp_legacy`` parses the pre-2026-June OTP netbank XLSX export (the format the
``otp`` plugin used to read before OTP changed the export in June 2026). The
fixture is the committed, anonymized ``sample-old-format-pre-2026-06.xlsx``.
"""

from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from ofxstatement_otp.otp_legacy import OtpLegacyXlsxParser

REPO_ROOT = Path(__file__).resolve().parent.parent
OLD_SAMPLE = REPO_ROOT / "manual_test" / "sample-old-format-pre-2026-06.xlsx"


@pytest.fixture
def statement():
    parser = OtpLegacyXlsxParser(str(OLD_SAMPLE))
    return parser.parse()


def test_skips_hidden_and_incomplete_rows(statement):
    # 8 data rows; the hidden row and the no-booking-date row are skipped.
    assert len(statement.lines) == 8


def test_start_date_from_first_booking(statement):
    assert statement.start_date == datetime(2024, 1, 2)


def test_currency_is_huf(statement):
    assert statement.currency == "HUF"


def test_payees_and_amounts(statement):
    first = statement.lines[0]
    assert first.payee == "SPAR MAGYARORSZAG KFT"
    assert first.amount == Decimal("-4990")
    assert first.date == datetime(2024, 1, 2)


def test_trntype_mapping(statement):
    # Keyed by memo -- payees collide ("OTP Bank" is both a fee and interest).
    by_memo = {line.memo: line.trntype for line in statement.lines}
    assert by_memo["SPAR vásárlás"] == "POS"  # VÁSÁRLÁS KÁRTYÁVAL
    assert by_memo["Lakbér január"] == "XFER"  # NAPKÖZBENI ÁTUTALÁS
    assert by_memo["Számlavezetési díj"] == "SRVCHG"  # ZÁRLATI DÍJ
    assert by_memo["Havi kamat"] == "XFER"  # KAMATJÓVÁÍRÁS
    # Unknown description falls back to PAYMENT.
    assert by_memo["Ismeretlen típus -> PAYMENT"] == "PAYMENT"


def test_every_line_has_an_id(statement):
    assert all(line.id for line in statement.lines)


def test_default_bank_id_is_otp_bic():
    from ofxstatement_otp.otp_legacy import OtpLegacyPlugin

    parser = OtpLegacyPlugin(None, {}).get_parser(str(OLD_SAMPLE))
    assert parser.statement.bank_id == "OTPVHUHB"
