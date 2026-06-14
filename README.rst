~~~~~~~~~~~~~~~~~~~~~~~~~~~
OTP plugin for ofxstatement
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Plugins to read statements provided by OTP (https://www.otpbank.hu).

Current plugin
==============

It's a fork and adaptation of https://github.com/Jacotsu/ofxstatement-intesasp

The ``otp`` plugin reads the post-2026-June netbank XLSX export::

    ofxstatement convert -t otp statement.xlsx out.ofx

Selecting a single account
--------------------------

A single OTP export bundles **every** account into one file (identified only by
account number). Without further configuration the plugin emits one statement
containing all of them. To get a clean per-account OFX, set the ``account``
option to the account number (a case-insensitive substring is enough); rows for
other accounts are skipped.

Define named plugin types in your ofxstatement config
(``ofxstatement edit-config``)::

    [otp:checking]
    plugin = otp
    account = 11773535

    [otp:credit]
    plugin = otp
    account = 11773016

then convert each account from the same export::

    ofxstatement convert -t otp:checking statement.xlsx checking.ofx
    ofxstatement convert -t otp:credit  statement.xlsx credit.ofx


Legacy plugins
==============

The ``otp_legacy`` plugin parses the **pre-2026-June** OTP netbank XLSX export
-- the format the ``otp`` plugin itself used to read before OTP changed the
export in June 2026::

    ofxstatement convert -t otp_legacy old-statement.xlsx out.ofx

In that older format the transaction table started on row 2 (columns A-L), the
account id was taken from cell ``D8`` and the statement start date from cell
``B2``. New exports look different (a metadata preamble, a relocated header and
a new column order), so use the ``otp`` plugin for anything exported from June
2026 onwards.

(Even older XML/CSV exports from the netbank version retired in September 2021
are no longer supported.)

Editing the plugin
===================

You can follow the instructions at https://github.com/kedder/ofxstatement-sample
if you want to make changes to this plugin. Pull requests are welcome!

The plugin code lives in its own top-level package, ``ofxstatement_otp``, and is
wired into ``ofxstatement`` purely through the entry points declared in
``setup.py`` (this matches the layout of the upstream sample). The plugin
*names* used on the command line are ``otp`` (current export) and
``otp_legacy`` (pre-2026-June export).

Development setup
=================

Create a virtualenv and install the plugin in editable mode (this pulls in
``ofxstatement`` and ``openpyxl`` and registers the entry points)::

    python3 -m venv .venv
    .venv/bin/pip install -e .

Because the install is editable, edits to ``src/ofxstatement_otp/`` take effect
immediately -- no reinstall needed. Confirm the plugins are registered with::

    .venv/bin/ofxstatement list-plugins

Manual testing
==============

The automated test suite runs with ``make test`` (pytest). For exercising the
``otp`` plugin against a realistic file without a real bank export, the
``manual_test/`` directory contains a small helper.

1. Generate a synthetic OTP-format XLSX (fake data, correct structure)::

       .venv/bin/python manual_test/generate_sample.py

   This writes ``manual_test/sample.xlsx``.

2. Convert it with the normal CLI and inspect the OFX::

       .venv/bin/ofxstatement convert -t otp manual_test/sample.xlsx out.ofx

   To convert a real export, point the command at it instead of the sample.
