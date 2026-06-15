"""Shared mapping from OTP transaction descriptions to OFX trntype codes.

Both the current (``otp``) and legacy (``otp_legacy``) plugins read the same
set of Hungarian transaction descriptions, so the table lives here as a single
module-level constant -- built once at import time rather than rebuilt on every
lookup inside each plugin.
"""

DEFAULT_TYPE = "PAYMENT"

TRANS_MAP = {
    "NAPKÖZBENI ÁTUTALÁS": "XFER",
    "VÁSÁRLÁS KÁRTYÁVAL": "POS",
    "ESETI MEGBÍZÁSOK KÖLTSÉGE": "SRVCHG",
    "AZONNALI ÁTUTALÁS": "XFER",
    "ÁRUVISSZAVÉT ELLENÉRTÉKE": "POS",
    "ÉRTÉKPAPÍR ÁLLANDÓ VÉTELI MB": "XFER",
    "ZÁRLATI DÍJ": "SRVCHG",
    "LAKÁSTAKARÉK BETÉT TERHELÉSE": "XFER",
    "HITELTÖRLESZTÉS EGYÉB": "XFER",
    "HITELTÖRLESZTÉS BESZEDÉSE": "SRVCHG",
    "Minimum fizetendő összeg besz.díja": "SRVCHG",
    "ÁTUTALÁS (OTP-N BELÜL)": "XFER",
    "AZONNALI ÁTUTALÁS BANKON BELÜL": "XFER",
    "KONVERZIÓ ÜGYF.HUFSZLÁRÓL DEVSZLÁRA": "XFER",
    "TERHELÉS": "PAYMENT",
    "HITELTÖRLESZTÉS BEFIZETÉS / ÁTUTALÁ": "PAYMENT",
    "PÉNZÁTVEZ. ÉRTÉKPAPÍR SZLA-RÓL": "XFER",
    "IDŐSZAKOS KÖLTSÉGEK": "SRVCHG",
    "KAMATJÓVÁÍRÁS": "XFER",
    "PRIVÁT BANKI CSOMAGDÍJ": "SRVCHG",
    "20TBE0561242 BÉT vétel  HB": "PAYMENT",
    "EGYÉB BIZTOSÍTÁSI DÍJ": "PAYMENT",
}


def transaction_type(description: str) -> str:
    """Map an OTP transaction description to an OFX trntype.

    The description is stripped before lookup; unknown descriptions fall back
    to ``PAYMENT``.
    """
    return TRANS_MAP.get(description.strip(), DEFAULT_TYPE)
