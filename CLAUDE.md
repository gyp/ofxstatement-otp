# CLAUDE.md

## Overview

`ofxstatement-otp` is a plugin for [ofxstatement](https://github.com/kedder/ofxstatement)
that converts statement exports from the Hungarian bank OTP into OFX. It ships three plugins,
one per export format, registered as `ofxstatement` entry points in [setup.py](setup.py):

- **`otp`** — current plugin for the post-2021-September netbank **XLSX** export.
- **`otp_legacy`** — pre-2021-September debit export, XML (≈CAMT.053 / ISO-20022).
- **`otp_legacy_credit`** — pre-2021-September credit-card export, CSV.

The legacy plugins target a netbank version retired in September 2021; new work should focus
on the `otp` plugin.

## Architecture

The three plugins live in a single top-level package, [src/ofxstatement_otp/](src/ofxstatement_otp/),
and are wired in via the `ofxstatement` entry points in [setup.py](setup.py) — the plugin
code is **not** part of the core `ofxstatement.plugins` namespace (the core ships as a regular
package, so it can't be extended that way; this layout matches the upstream sample).

Each plugin follows the ofxstatement model: a `Plugin` subclass whose `get_parser()` returns a
`StatementParser` subclass.

The current plugin lives in [src/ofxstatement_otp/otp.py](src/ofxstatement_otp/otp.py):

- `OtpXlsxParser.split_records()` reads the `Tranzakciók` sheet with `openpyxl`, iterating
  columns A–L from row 2. It skips **hidden rows** (artifacts of netbank filters) and rows
  with no booking date, then yields `Transaction` dataclasses.
- `parse_record()` turns each `Transaction` into a `StatementLine`.
- Statement metadata is read from **fixed cell coordinates** (`D8` = account id, `B2` = start
  date) because the format has no clean fields for them.
- `_get_transaction_type()` maps Hungarian transaction descriptions (e.g. `VÁSÁRLÁS KÁRTYÁVAL`)
  to OFX `trntype` codes via the `trans_map` dict, defaulting to `PAYMENT` for unknown labels.

The legacy plugins ([otp_legacy.py](src/ofxstatement_otp/otp_legacy.py),
[otp_credit_legacy.py](src/ofxstatement_otp/otp_credit_legacy.py)) are adapted from
ofxstatement-iso20022 (XML) and the built-in `CSVStatementParser` (CSV).

## Commands

From the [Makefile](Makefile):

- `make test` — run pytest
- `make coverage` — pytest with coverage for `src/ofxstatement`
- `make black` — format `setup.py src tests`
- `make mypy` — type-check `src tests`
- `make` — runs test, mypy, and black

Run a conversion with the installed CLI:

```
ofxstatement convert -t otp <statement.xlsx> out.ofx
```

## Dev setup & manual testing

Editable install works now that the plugin lives in its own top-level package:

```
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/ofxstatement list-plugins   # confirm otp / otp_legacy / otp_legacy_credit
```

Edits to `src/ofxstatement_otp/` apply live — no reinstall needed.

Manual test helper lives in [manual_test/](manual_test/):

- `python manual_test/generate_sample.py` — writes `manual_test/sample.xlsx`, a
  synthetic export with the correct structure (Tranzakciók sheet, header in row
  1, data from row 2, columns A–L, plus a hidden row and an incomplete row to
  exercise the skip paths).
- Then convert it the normal way:
  `ofxstatement convert -t otp manual_test/sample.xlsx out.ofx`

There is also a personal `~/bin/otpconvert` wrapper (outside this repo) that
splits a combined export into checking/credit via csvkit before calling the CLI.

## Gotchas & known limitations

- **No automated `tests/` directory yet**, even though the Makefile and Pipfile
  reference pytest. Manual testing is via [manual_test/](manual_test/) (see above).
- The `otp` plugin **hardcodes HUF** in `_get_currency()`; non-HUF accounts are unsupported.
- `account_id` is read from a single cell (`D8`) as a workaround — the XLSX format has no
  dedicated account field (see the `FIXME` in `_get_account_id`).
- start/end balance and end date all return `None`.
- To support a new transaction kind, add an entry to the `trans_map` dict in
  `_get_transaction_type()`.
