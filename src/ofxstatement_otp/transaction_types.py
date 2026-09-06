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
    "AZONNALI FIZETÉS BANKON BELÜL": "XFER",
    "QVIK FIZETÉS": "XFER",
    "QVIK FIZETÉS BANKON BELÜL": "XFER",
    "NAPKÖZBENI ÁTUTALÁS (CSOPORTOS)": "XFER",
    "LAKÁS/JELZÁLOG HITEL TÖRL": "XFER",
    "BANKKÁRTYA ÉVES DÍJ": "SRVCHG",
    "BANKKÁRTYA ÉVES DÍJ JÓV.": "SRVCHG",
    "BANKKÁRTYÁVAL KAPCS. DÍJ": "SRVCHG",
    "ÉRTÉKPAPÍR SZLADÍJ": "SRVCHG",
    "PRÉMIUM NEXT SZOLGÁLTATÁS": "SRVCHG",
}


def _normalise(description: str) -> str:
    """Collapse surrounding and doubled inner whitespace.

    The export writes some descriptions with doubled inner spaces (e.g.
    ``QVIK  FIZETÉS``), which would otherwise never match a table entry.
    """
    return " ".join(str(description).split())


# Keys are normalised the same way as lookups, so a table entry that itself
# carries doubled spaces stays reachable.
_NORMALISED_MAP = {_normalise(key): value for key, value in TRANS_MAP.items()}


def transaction_type(description: str) -> str:
    """Map an OTP transaction description to an OFX trntype.

    Whitespace in the description is normalised before lookup; unknown
    descriptions fall back to ``PAYMENT``.
    """
    return _NORMALISED_MAP.get(_normalise(description), DEFAULT_TYPE)
