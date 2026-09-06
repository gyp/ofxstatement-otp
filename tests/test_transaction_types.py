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


def test_doubled_inner_spaces_are_collapsed_before_lookup():
    # The export writes some descriptions with doubled inner spaces.
    assert transaction_type("QVIK  FIZETÉS  BANKON BELÜL") == "XFER"


def test_keys_with_doubled_inner_spaces_still_match():
    # The table itself carries such a description; normalising the lookup must
    # not make its entry unreachable.
    assert transaction_type("20TBE0561242 BÉT vétel  HB") == "PAYMENT"
    assert transaction_type("20TBE0561242 BÉT vétel HB") == "PAYMENT"


def test_credit_card_descriptions_from_the_2026_09_export():
    assert transaction_type("BANKKÁRTYA ÉVES DÍJ") == "SRVCHG"
    assert transaction_type("BANKKÁRTYA ÉVES DÍJ JÓV.") == "SRVCHG"
    assert transaction_type("BANKKÁRTYÁVAL KAPCS. DÍJ") == "SRVCHG"
    assert transaction_type("AZONNALI FIZETÉS BANKON BELÜL") == "XFER"
    assert transaction_type("NAPKÖZBENI ÁTUTALÁS (CSOPORTOS)") == "XFER"
    assert transaction_type("LAKÁS/JELZÁLOG HITEL TÖRL") == "XFER"
    assert transaction_type("ÉRTÉKPAPÍR SZLADÍJ") == "SRVCHG"
    assert transaction_type("PRÉMIUM NEXT SZOLGÁLTATÁS") == "SRVCHG"
