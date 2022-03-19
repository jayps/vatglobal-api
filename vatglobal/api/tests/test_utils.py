from django.test import TestCase
from rest_framework.exceptions import ValidationError

from vatglobal.api.utils import create_transaction_from_row


class TestTransactionCreation(TestCase):
    def test_transaction_creation_with_invalid_row(self):
        data = ['2020/1/23','sele','ZA','ZAR','631.13','113.6']
        with self.assertRaises(ValidationError):
            create_transaction_from_row(data)

    def test_transaction_creation_with_valid_row(self):
        data = ['2020/1/23','sale','ZA','ZAR','631.13','113.6']
        created = create_transaction_from_row(data)
        assert created == True

    def test_transaction_creation_with_date_other_than_2020(self):
        data = ['2021/1/23','sale','ZA','ZAR','631.13','113.6']
        created = create_transaction_from_row(data)
        assert created == False

    def test_transaction_creation_with_invalid_date(self):
        data = ['NotAValidDate','sale','ZA','ZAR','631.13','113.6']
        with self.assertRaises(ValidationError):
            create_transaction_from_row(data)