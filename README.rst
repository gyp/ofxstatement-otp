~~~~~~~~~~~~~~~~~~~~~~~~~~~
OTP plugin for ofxstatement
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Plugins to read OTP (https://www.otpbank.hu) exported XMLs and CSVs.

The exported XMLs are pretty much conformant to CAMT.053 (ISO-20022),
with some extra information thrown in here and there, or some missing data
in some other places. The 'otp' plugin handles these types of exports.

For some weird reason credit card statements at OTP differ from debit
card statements and can only be exported in CSV format. The 'otp_credit'
plugin handles such exports.

The XML part of  plugin is pretty much a copy-paste of https://github.com/kedder/ofxstatement-iso20022
at commit 6cd6d0317a801d466efb30322ab4d71a10771454 with modifications to accomodate 
the idiosyncracies of OTP exported XMLs. The CSV side is some basic wrapping over
the built-in CSVStatementParser.
