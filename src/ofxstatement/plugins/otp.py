import xml.etree.ElementTree as ET
import datetime
import html
import re

from ofxstatement.plugin import Plugin
from ofxstatement.statement import Statement, StatementLine


CD_CREDIT = 'CRDT'
CD_DEBIT = 'DBIT'

class OtpPlugin(Plugin):
    """OTP (XML)
    """

    def get_parser(self, filename):
        return OtpParser(filename)


class OtpParser(object):
    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        """Main entry point for parsers
        """
        self.statement = Statement()
        tree = ET.parse(self.filename)

        self._parse_statement_properties(tree)
        self._parse_lines(tree)

        return self.statement

    def _parse_statement_properties(self, tree):
        stmt = tree.find('./Rpt')

        bnk = stmt.find('./Acct/Svcr/FinInstnId/Nm')
        iban = stmt.find('./Acct/Id/Othr/Id')
        bals = stmt.findall('./Bal')

        bal_amts = {}
        bal_dates = {}
        for bal in bals:
            cd = bal.find('./Tp/CdOrPrtry/Cd')
            amt = bal.find('./Amt')
            dt = bal.find('./Dt')

            # Amount currency should match with statement currency
            bal_amts[cd.text] = self._parse_amount(amt)
            bal_dates[cd.text] = self._parse_date(dt)

        self.statement.bank_id = bnk.text
        self.statement.account_id = iban.text
        self.statement.start_balance = bal_amts['OPBD']
        self.statement.start_date = bal_dates['OPBD']
        self.statement.end_balance = bal_amts.get('CLBD', None)
        self.statement.end_date = bal_dates.get('CLBD', None)

    def _parse_lines(self, tree):
        for ntry in _findall(tree, 'Rpt/Ntry'):
            sline = self._parse_line(ntry)
            if sline is not None:
                self.statement.lines.append(sline)

    def _parse_line(self, ntry):
        # don't try to parse pending entries, too many items missing
        if _find(ntry, 'Sts').text == 'PDNG':
            return None

        sline = StatementLine()

        crdeb = _find(ntry, 'CdtDbtInd').text

        amtnode = _find(ntry, 'Amt')
        amt = self._parse_amount(amtnode)
        if crdeb == CD_DEBIT:
            amt = -amt
            payee = _find(ntry, 'NtryDtls/TxDtls/RltdPties/Cdtr/Nm')
        else:
            payee = _find(ntry, 'NtryDtls/TxDtls/RltdPties/Dbtr/Nm')
        if payee is not None:
            payee = payee.text

        sline.payee = payee
        sline.amount = amt

        dt = _find(ntry, 'ValDt')
        sline.date = self._parse_date(dt)

        bookdt = _find(ntry, 'BookgDt')
        sline.date_user = self._parse_date(bookdt)

        svcref = _find(ntry, 'NtryDtls/TxDtls/Refs/AcctSvcrRef')
        sline.refnum = getattr(svcref, 'text', None)

        rmtinf = _find(ntry, 'NtryDtls/TxDtls/RmtInf/Ustrd')
        sline.memo = rmtinf.text if rmtinf.text else ''

        addtlinf_node = _find(ntry, 'NtryDtls/TxDtls/AddtlTxInf')
        if addtlinf_node is not None and addtlinf_node.text is not None:
            addtlinf = self._parse_addtlinf(addtlinf_node)
        else:
            addtlinf = ''

        if 'VÁSÁRLÁS KÁRTYÁVAL' == addtlinf and not sline.payee:
            sline.payee = _trim_payee(sline.memo)

        sline.memo += ' ' + addtlinf

        return sline

    def _parse_date(self, dtnode):
        if dtnode is None:
            return None

        dt = _find(dtnode, 'Dt')
        dttm = _find(dtnode, 'DtTm')

        if dt is not None and dt.text is not None:
            return datetime.datetime.strptime(dt.text, "%Y-%m-%d")
        else:
            assert dttm is not None
            return datetime.datetime.fromisoformat(dttm.text, "%Y-%m-%dT%H:%M:%S")


    def _parse_amount(self, amtnode):
        if amtnode.text is not None:
            return float(amtnode.text)
        else:
            return None

    def _parse_addtlinf(self, addtlinf):
        string = '<root>' + html.unescape(addtlinf.text).replace("&", "&amp;") + '</root>'
        for infonode_label in ['narr', 'inf']:
            if ET.fromstring(string).find(infonode_label) is not None:
                return ET.fromstring(string).find(infonode_label).text
        return None


def _toxpath(spath):
    tags = spath.split('/')
    path = ['%s' % t for t in tags]
    xpath = './%s' % '/'.join(path)
    return xpath


def _find(tree, spath):
    return tree.find(_toxpath(spath))


def _findall(tree, spath):
    return tree.findall(_toxpath(spath))

_trim_payee_regexes = [
    re.compile('   .*'),
    re.compile('\d+\.\d+\.\d+ \d+'),
    re.compile('[\d,]+EUR.*')
]
def _trim_payee(payee):
    for r in _trim_payee_regexes:
        payee = r.sub('', payee)
    return payee
