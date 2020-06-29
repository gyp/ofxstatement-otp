import csv

from ofxstatement.plugin import Plugin
from ofxstatement.statement import Statement, StatementLine, BankAccount, generate_transaction_id
from ofxstatement.parser import CsvStatementParser


class OtpCreditPlugin(Plugin):
    """OTP Credit Card Statements (CSV)
    """

    def get_parser(self, filename):
        return OtpCreditParser(filename)


class OtpCreditParser(CsvStatementParser):

    date_format = "%Y%m%d"
    encoding = 'utf-8'

    mappings = {
        "date": 5,
        "payee": 10,
        "memo": 9,
        "amount": 2,
        "trntype": 1,
    }

    def __init__(self, filename):
        self.statement = Statement(
            bank_id = "OTP Bank Nyrt.",
            account_id = self.get_account_id_from_file(filename)
        )
        self.fin = open(filename, encoding=self.encoding)

    def get_account_id_from_file(self, filename):
        with open(filename, encoding=self.encoding) as csvfile:
            first_line = next(self._get_reader(csvfile))
            return first_line[0]

    def split_records(self):
        return self._get_reader(self.fin)

    def _get_reader(self, fin):
        return csv.reader(fin, delimiter=';')

    def parse_record(self, line):
        stmt_line = super().parse_record(line)
        stmt_line.id = generate_transaction_id(stmt_line)
        return stmt_line

    def parse_value(self, value, field):
        if field == "trntype":
            return self.parse_trntype(value)
        elif field == "memo":
            return self.parse_memo(value)
        else:
            return super().parse_value(value, field)

    def parse_trntype(self, value):
        transaction_mapping = {
            "T": "CREDIT",
            "J": "DEBIT"
        }
        return transaction_mapping[value]

    def parse_memo(self, value):
        if value == "VÁSÁRLÁS KÁRTYÁVAL":
            # this is completely redundant and non-informative, let's just drop it
            return None
        else:
            return value