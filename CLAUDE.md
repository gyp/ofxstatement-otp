# CLAUDE.md

## Overview

`ofxstatement-otp` is a plugin for [ofxstatement](https://github.com/kedder/ofxstatement)
that converts statement exports from the Hungarian bank OTP into OFX. It ships two plugins,
one per **XLSX** export format, registered as `ofxstatement` entry points in [setup.py](setup.py):

- **`otp`** — current plugin for the post-2026-June netbank XLSX export.
- **`otp_legacy`** — the pre-2026-June XLSX export (the format `otp` itself used before
  OTP changed the export in June 2026).

New work should focus on the `otp` plugin; `otp_legacy` is frozen for converting older
exports. (The XML/CSV plugins for the netbank version retired in September 2021 have been
removed.)

## Workflow (MANDATORY)

From this point on, **every change must go through a full TDD cycle**:

1. **Write a failing test first** that captures the intended behaviour (in [tests/](tests/)).
2. **Run the suite (`make test`) and watch the new test fail** — confirm it fails for the
   right reason, not a typo or import error.
3. **Make the change** to the source.
4. **Run the suite again and watch it turn green** — the new test passes and nothing else
   regressed.

Do not write production code before there is a failing test for it.

## Architecture

Both plugins live in a single top-level package, [src/ofxstatement_otp/](src/ofxstatement_otp/),
and are wired in via the `ofxstatement` entry points in [setup.py](setup.py) — the plugin
code is **not** part of the core `ofxstatement.plugins` namespace (the core ships as a regular
package, so it can't be extended that way; this layout matches the upstream sample).

Each plugin follows the ofxstatement model: a `Plugin` subclass whose `get_parser()` returns a
`StatementParser` subclass.

The current plugin lives in [src/ofxstatement_otp/otp.py](src/ofxstatement_otp/otp.py):

- The export has a **metadata preamble** (rows 1–~14: a `Számlatörténet` title, the list of
  account numbers, and the query date range) followed by the transaction table. The table
  has **11 columns (A–K)**: `Számlaszám` (account no), `Ellenoldali számlaszám` (partner
  account), `Ellenoldali név` (partner name), `Forgalom típusa` (description), `Közlemény`
  (memo), `Tranzakció kategória`, `Banki azonosító` (unique txn id), `Tranzakció időpontja`
  (txn datetime), `Könyvelés dátuma` (booking date), `Összeg` (signed amount), `Devizanem`.
- `_find_header_row()` locates the table header dynamically (the row where col A ==
  `Számlaszám` and col B == `Ellenoldali számlaszám`), so it tolerates preamble changes.
- `OtpXlsxParser.split_records()` iterates data rows below the header, skipping **hidden
  rows** (netbank filter artifacts) and rows with no booking date, then yields `Transaction`
  dataclasses. Date cells are parsed via `_to_datetime()`, which accepts both strings and
  native `datetime` cells.
- **The export bundles every account into one file.** Set the `account` plugin setting (a
  substring of the account number, case-insensitive) to emit a statement for just one
  account — rows for other accounts are skipped. This replaces the old external
  `csvgrep`-based splitting wrapper.
- `parse_record()` turns each `Transaction` into a `StatementLine`, using `Banki azonosító`
  (col G) as the OFX FITID.
- Statement metadata is read by **label** from the preamble: `account_id` from the matched
  account number, `start_date`/`end_date` from `Lekérdezés kezdete`/`Lekérdezés vége`.
- `_get_transaction_type()` maps Hungarian transaction descriptions (e.g. `VÁSÁRLÁS KÁRTYÁVAL`)
  to OFX `trntype` codes via the `trans_map` dict, defaulting to `PAYMENT` for unknown labels.

The legacy plugin [otp_legacy.py](src/ofxstatement_otp/otp_legacy.py) is the **frozen
pre-2026-June** XLSX parser: data from row 2, columns A–L, `account_id` from cell `D8` and
`start_date` from cell `B2`. It is exercised by [tests/test_otp_legacy.py](tests/test_otp_legacy.py)
against the committed `manual_test/sample-old-format-pre-2026-06.xlsx` fixture.

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
.venv/bin/ofxstatement list-plugins   # confirm otp / otp_legacy
```

Edits to `src/ofxstatement_otp/` apply live — no reinstall needed.

Manual test helper lives in [manual_test/](manual_test/):

- `python manual_test/generate_sample.py` — writes `manual_test/sample.xlsx`, a
  synthetic export with the correct structure (Tranzakciók sheet, metadata preamble,
  a dynamically-located table header, columns A–K, two distinct accounts, plus a hidden
  row and a no-booking-date row to exercise the skip paths). It is also the anonymized
  fixture used by `tests/`.
- Then convert it the normal way:
  `ofxstatement convert -t otp manual_test/sample.xlsx out.ofx`

Two pre-generated, committed sample exports also live in [manual_test/](manual_test/)
(the default `sample.xlsx` itself stays gitignored):

- `sample-new-format-2026-06.xlsx` — the current format; converts with `-t otp`.
- `sample-old-format-pre-2026-06.xlsx` — the pre-2026-06 format, kept for reference. It
  does **not** parse with the current `otp` plugin; it documents the layout OTP retired
  when it changed the export in June 2026.

Real (non-anonymized) exports must never be committed; `manual_test/*DO-NOT*COMMIT*` is
gitignored for that.

The old `~/bin/otpconvert` wrapper (csvkit split into checking/credit) is **retired** — its
per-account split now lives in the plugin via the `account` setting, and OTP's current format
no longer has the `Számla név` column it grepped on. To split one combined export, define
named config types, e.g. `[otp:checking] plugin=otp account=11111111` and
`[otp:credit] plugin=otp account=33333333`, then `ofxstatement convert -t otp:checking …`.

## Gotchas & known limitations

- `_get_currency()` reads col K (`Devizanem`) but defaults to **HUF**; mixed-currency
  handling within one statement is untested.
- start/end balance return `None` (not present in the export).
- To support a new transaction kind, add an entry to the `trans_map` dict in
  `_get_transaction_type()`.
- Without an `account` setting the statement mixes **all** accounts in the file (and
  `account_id` is just the first account seen); set `account` for a clean per-account OFX.
