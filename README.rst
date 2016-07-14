~~~~~~~~~~~~~~~~~~~~~~~~~~~
OTP plugin for ofxstatement
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Plugin to read OTP (https://www.otpbank.hu) exported XMLs.

The exported XMLs are pretty much conformant to CAMT.053 (ISO-20022),
with some extra information thrown in here and there, or some missing data
in some other places.

This plugin is pretty much a copy-paste of https://github.com/kedder/ofxstatement-iso20022
at commit 6cd6d0317a801d466efb30322ab4d71a10771454 with modifications to accomodate 
the idiosyncracies of OTP exported XMLs.
