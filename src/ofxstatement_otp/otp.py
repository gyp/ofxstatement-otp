from openpyxl import load_workbook
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import logging

from ofxstatement.plugin import Plugin
from ofxstatement.parser import StatementParser
from ofxstatement.statement import (Statement, StatementLine,
                                    generate_transaction_id)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('OTP')

TRANSACTIONS_SHEET_NAME = 'Tranzakciók'

@dataclass
class Transaction:
    transaction_date: datetime
    booking_date: datetime
    description: str
    in_or_out: str
    partner_name: str
    partner_account: str
    otp_generated_category: str
    memo: str
    account_name: str
    account_no: str
    amount: Decimal
    currency: str


class OtpPlugin(Plugin):
    """OTP Bank, after the 2021 September update (XLSX)
    """
    def get_parser(self, filename):
        parser = OtpXlsxParser(filename)
        parser.statement.bank_id = self.settings.get('BIC', 'IntesaSP')
        return parser


class OtpXlsxParser(StatementParser):

    def split_records(self):
        return self._get_transactions()

    def __init__(self, filename):
        self.filename = filename
        self.statement = Statement()
        self.statement.account_id = self._get_account_id()
        self.statement.currency = self._get_currency()
        self.statement.start_balance = self._get_start_balance()
        self.statement.start_date = self._get_start_date()
        self.statement.end_balance = self._get_end_balance()
        self.statement.end_date = self._get_end_date()
        logging.debug(self.statement)

    def parse(self):
        return super(OtpXlsxParser, self).parse()

    def parse_record(self, record: Transaction):
        logging.debug(record)
        stat_line = StatementLine(None,
                                  record.booking_date,
                                  record.memo,
                                  Decimal(record.amount))
        logging.debug(stat_line)
        stat_line.id = generate_transaction_id(stat_line)
        stat_line.date_user = record.transaction_date
        stat_line.payee = record.partner_name
        stat_line.trntype = self._get_transaction_type(record)
        logging.debug(stat_line)
        return stat_line

    def _get_account_id(self):
        # FIXME: there's no single field for this in this format
        wb = load_workbook(self.filename)
        return wb[TRANSACTIONS_SHEET_NAME]['D8'].value

    def _get_currency(self):
        # TODO: support non-HUF accounts
        return 'HUF'

    def _get_transactions(self) -> list[Transaction]:
        wb = load_workbook(self.filename)
        starting_column = 'A'
        ending_column = 'L'
        starting_row = 2
        offset = 0

        while True:
            data = wb[TRANSACTIONS_SHEET_NAME][
                        '{}{}:{}{}'.format(starting_column,
                                           starting_row + offset,
                                           ending_column,
                                           starting_row + offset
                                           )]

            values = [*map(lambda x: x.value, data[0])]
            logging.debug(values)

            # skip hidden rows -- some filters are applied as such
            if wb.active.row_dimensions[starting_row + offset].hidden:
                logging.debug("Skipping hidden row: " + str(starting_row + offset))
                offset += 1
                continue

            # stop when we reach the end of the file
            if not values[0]:
                break

            # skip lines without parseable dates
            if not values[1]:
                logging.debug("Skipping incomplete row: " + str(starting_row + offset))
                offset += 1
                continue

            values[0] = datetime.strptime(values[0], '%Y-%m-%d %H:%M:%S')
            values[1] = datetime.strptime(values[1], '%Y-%m-%d')
            offset += 1
            yield Transaction(*values)


    def _get_transaction_type(self, transaction: Transaction) -> str:
        trans_map = {
                     'NAPKÖZBENI ÁTUTALÁS': 'XFER',
                     'VÁSÁRLÁS KÁRTYÁVAL': 'POS',
                     'ESETI MEGBÍZÁSOK KÖLTSÉGE': 'SRVCHG',
                     'AZONNALI ÁTUTALÁS': 'XFER',
                     'ÁRUVISSZAVÉT ELLENÉRTÉKE': 'POS',
                     'ÉRTÉKPAPÍR ÁLLANDÓ VÉTELI MB': 'XFER',
                     'ZÁRLATI DÍJ': 'SRVCHG',
                     'LAKÁSTAKARÉK BETÉT TERHELÉSE': 'XFER',
                     'HITELTÖRLESZTÉS EGYÉB': 'XFER',
                     'HITELTÖRLESZTÉS BESZEDÉSE': 'SRVCHG',
                     'Minimum fizetendő összeg besz.díja': 'SRVCHG',
                     'ÁTUTALÁS (OTP-N BELÜL)': 'XFER',
                     'AZONNALI ÁTUTALÁS BANKON BELÜL': 'XFER',
                     'KONVERZIÓ ÜGYF.HUFSZLÁRÓL DEVSZLÁRA': 'XFER',
                     'TERHELÉS': 'PAYMENT',
                     'HITELTÖRLESZTÉS BEFIZETÉS / ÁTUTALÁ': 'PAYMENT',
                     'PÉNZÁTVEZ. ÉRTÉKPAPÍR SZLA-RÓL': 'XFER',
                     'IDŐSZAKOS KÖLTSÉGEK': 'SRVCHG',
                     'KAMATJÓVÁÍRÁS': 'XFER',
                     'PRIVÁT BANKI CSOMAGDÍJ': 'SRVCHG',
                     '20TBE0561242 BÉT vétel  HB': 'PAYMENT',
                     'EGYÉB BIZTOSÍTÁSI DÍJ': 'PAYMENT'
                     }
        try:
            return trans_map[transaction.description.strip()]
        except KeyError:
            return 'PAYMENT'

    def _get_start_balance(self):
        return None

    def _get_end_balance(self):
        return None

    def _get_start_date(self):
        wb = load_workbook(self.filename)
        date = wb[TRANSACTIONS_SHEET_NAME]['B2'].value
        return datetime.strptime(date, '%Y-%m-%d')

    def _get_end_date(self):
        return None
        #return datetime.strptime('2050-01-01', '%Y-%m-%d')

