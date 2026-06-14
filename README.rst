~~~~~~~~~~~~~~~~~~~~~~~~~~~
OTP plugin for ofxstatement
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Plugins to read statements provided by OTP (https://www.otpbank.hu).

Current plugin
==============

It's a fork and adaptation of https://github.com/Jacotsu/ofxstatement-intesasp

Legacy plugins
==============

The plugins with "legacy" in their names parse the files exported by the previous
version of OTP's netbank. That version is no longer available since September 2021.

The exported XMLs are pretty much conformant to CAMT.053 (ISO-20022),
with some extra information thrown in here and there, or some missing data
in some other places. The 'otp' plugin handles these types of exports.

For some weird reason credit card statements differed from debit
card statements and can only be exported in CSV format. The 'otp_credit'
plugin handles such exports.

The XML part is pretty much a copy-paste of https://github.com/kedder/ofxstatement-iso20022
at commit 6cd6d0317a801d466efb30322ab4d71a10771454 with modifications to accomodate 
the idiosyncracies of OTP exported XMLs. The CSV side is some basic wrapping over
the built-in CSVStatementParser.

Editing the plugin
===================

You can follow the instructions at https://github.com/kedder/ofxstatement-sample
if you want to make changes to this plugin. Pull requests are welcome!

The plugin code lives in its own top-level package, ``ofxstatement_otp``, and is
wired into ``ofxstatement`` purely through the entry points declared in
``setup.py`` (this matches the layout of the upstream sample). The plugin
*names* used on the command line are ``otp``, ``otp_legacy`` and
``otp_legacy_credit``.

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

There is no automated test suite yet. The ``manual_test/`` directory contains a
small helper so you can exercise the ``otp`` plugin without a real bank export.

1. Generate a synthetic OTP-format XLSX (fake data, correct structure)::

       .venv/bin/python manual_test/generate_sample.py

   This writes ``manual_test/sample.xlsx``.

2. Convert it with the normal CLI and inspect the OFX::

       .venv/bin/ofxstatement convert -t otp manual_test/sample.xlsx out.ofx

   To convert a real export, point the command at it instead of the sample.
