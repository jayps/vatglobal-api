import datetime
from unittest.mock import patch

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from vatglobal.api.models import CurrencyHistory
from vatglobal.api.utils import create_transaction_from_row, get_currency_conversion


class TestTransactionCreation(TestCase):
    def test_transaction_creation_with_invalid_row(self):
        data = ['2020/1/23', 'sele', 'ZA', 'ZAR', '631.13', '113.6']
        with self.assertRaises(ValidationError):
            create_transaction_from_row(data)

    def test_transaction_creation_with_valid_row(self):
        data = ['2020/1/23', 'sale', 'ZA', 'ZAR', '631.13', '113.6']
        created = create_transaction_from_row(data)
        assert created == True

    def test_transaction_creation_with_date_other_than_2020(self):
        data = ['2021/1/23', 'sale', 'ZA', 'ZAR', '631.13', '113.6']
        created = create_transaction_from_row(data)
        assert created == False

    def test_transaction_creation_with_invalid_date(self):
        data = ['NotAValidDate', 'sale', 'ZA', 'ZAR', '631.13', '113.6']
        with self.assertRaises(ValidationError):
            create_transaction_from_row(data)


class TestCurrencyConversion(TestCase):
    @patch('vatglobal.api.utils.get_currency_conversion_rate_from_ecb')
    def test_get_existing_currency_conversion_rate(self, mock_get_currency_conversion_rate_from_ecb):
        date = datetime.date(year=2020, month=1, day=1)
        CurrencyHistory.objects.create(
            date=date,
            from_currency='USD',
            to_currency='ZAR',
            conversion_rate=15.00
        )

        conversion_rate = get_currency_conversion(from_currency='USD', to_currency='ZAR', date=date)
        assert conversion_rate == 15.00, f'Expected conversion rate of 15.00, but got {conversion_rate}'
        assert mock_get_currency_conversion_rate_from_ecb.call_count == 0, f'Expected get_currency_conversion_rate_from_ecb not to have been called, but it was called {mock_get_currency_conversion_rate_from_ecb.call_count} times.'


    @patch('vatglobal.api.utils.get_currency_conversion_rate_from_ecb')
    def test_get_currency_conversion_rate_with_stored_record(self, mock_get_currency_conversion_rate_from_ecb):
        mock_get_currency_conversion_rate_from_ecb.side_effect = (20.00,)
        date = datetime.date(year=2020, month=1, day=1)

        conversion_rate = get_currency_conversion(from_currency='EUR', to_currency='ZAR', date=date)
        assert conversion_rate == 20.00, f'Expected conversion rate of 20.00, but got {conversion_rate}'
        assert mock_get_currency_conversion_rate_from_ecb.call_count == 1, f'Expected get_currency_conversion_rate_from_ecb to have been called once, but it was called {mock_get_currency_conversion_rate_from_ecb.call_count} times.'

