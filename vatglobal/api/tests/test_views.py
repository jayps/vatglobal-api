import datetime
import os.path
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from vatglobal.api.models import Transaction


def upload_file(client, filename, skip_errors=False):
    file = open(f'{os.path.dirname(os.path.realpath(__file__))}/{filename}', 'rb')
    data = SimpleUploadedFile(
        content=file.read(),
        name=file.name,
        content_type='multipart/form-data'
    )
    res = client.post(reverse('upload'), {'file': data, 'skip_errors': skip_errors}, format='multipart')

    return res

def assert_status_code(assertion, response):
    assert assertion == response.status_code, f'Expected {assertion} status code, but got {response.status_code}'

def assert_error_message(expected_message, response):
    assert expected_message == response.json().get('error'), f'Expected "{expected_message}" status code, but got "{response.json().get("error")}"'


class TestTransactionUploadView(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch('vatglobal.api.views.create_transaction_from_row')
    def test_when_validation_fails_returns_400(self, mock_create_transaction_from_row):
        mock_create_transaction_from_row.side_effect = ValidationError()
        response = upload_file(self.client, 'test_data/test_data.csv')
        assert_status_code(400, response)

    @patch('vatglobal.api.views.create_transaction_from_row')
    def test_when_valid_file_uploaded_returns_201(self, mock_create_transaction_from_row):
        response = upload_file(self.client, 'test_data/test_data.csv')
        assert_status_code(201, response)

    @patch('vatglobal.api.views.create_transaction_from_row')
    def test_when_invalid_file_uploaded_with_skip_errors_returns_201(self, mock_create_transaction_from_row):
        mock_create_transaction_from_row.side_effect = ValidationError()
        response = upload_file(self.client, 'test_data/test_data.csv', skip_errors=True)
        assert_status_code(201, response)

    @patch('vatglobal.api.views.create_transaction_from_row')
    def test_when_file_uploaded_with_unexpected_error_returns_500(self, mock_create_transaction_from_row):
        mock_create_transaction_from_row.side_effect = Exception('Something unexpected went wrong')
        response = upload_file(self.client, 'test_data/test_data.csv', skip_errors=True)
        assert_status_code(500, response)


class TestTransactionViewSet(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_when_invalid_country_code_supplied_returns_400(self):
        response = self.client.get(
            reverse('retrieve'),
            {'date': '2020/01/01', 'country': 'ZZ', 'currency': 'ZAR'}
        )
        assert_status_code(400, response)

    def test_when_invalid_currency_code_supplied_returns_400(self):
        response = self.client.get(
            reverse('retrieve'),
            {'date': '2020/01/01', 'country': 'ZA', 'currency': 'AAA'}
        )
        assert_status_code(400, response)

    def test_successful_retrieval_without_conversion(self):
        Transaction.objects.create(
            date=datetime.date(year=2020, month=1, day=1),
            type='purchase',
            country='ZA',
            currency='ZAR',
            net=100,
            vat=15
        )
        Transaction.objects.create(
            date=datetime.date(year=2020, month=1, day=1),
            type='sale',
            country='ZA',
            currency='ZAR',
            net=200,
            vat=30
        )
        Transaction.objects.create(
            date=datetime.date(year=2020, month=1, day=2),
            type='sale',
            country='ZA',
            currency='ZAR',
            net=100,
            vat=15
        )

        response = self.client.get(
            reverse('retrieve'),
            {'date': '2020/01/01', 'country': 'ZA'}
        )
        number_of_records_returned = len(response.json())

        assert number_of_records_returned == 2, f'Expected 2 records to be returned, but got {number_of_records_returned}'
