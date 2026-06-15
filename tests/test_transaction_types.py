"""Tests for the shared transaction-type mapping used by both plugins.

The mapping from OTP transaction descriptions to OFX trntype codes is identical
for the current and legacy exports, so it lives in one module-level table rather
than being rebuilt on every lookup inside each plugin.
"""

from ofxstatement_otp.transaction_types import TRANS_MAP, transaction_type


def test_known_descriptions_map_to_their_codes():
    assert transaction_type("VÁSÁRLÁS KÁRTYÁVAL") == "POS"
    assert transaction_type("NAPKÖZBENI ÁTUTALÁS") == "XFER"
    assert transaction_type("ZÁRLATI DÍJ") == "SRVCHG"


def test_unknown_description_defaults_to_payment():
    assert transaction_type("NINCS ILYEN TÍPUS") == "PAYMENT"


def test_description_is_stripped_before_lookup():
    assert transaction_type("  VÁSÁRLÁS KÁRTYÁVAL  ") == "POS"


def test_both_plugins_delegate_to_the_shared_helper():
    # Guard against re-introducing a per-plugin copy of the table.
    from ofxstatement_otp import otp, otp_legacy

    assert otp.transaction_type is transaction_type
    assert otp_legacy.transaction_type is transaction_type
    assert isinstance(TRANS_MAP, dict)
