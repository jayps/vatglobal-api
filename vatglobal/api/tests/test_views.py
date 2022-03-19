import os.path
from unittest import TestCase
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient


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

    def test_when_no_date_supplied_returns_400(self):
        response = self.client.get(
            reverse('retrieve'),
            {'country': 'ZA', 'currency': 'ZAR'}
        )
        assert_status_code(400, response)
        assert_error_message('date query parameter is required.', response)

    def test_when_invalid_date_supplied_returns_400(self):
        response = self.client.get(
            reverse('retrieve'),
            {'date': 'thisIsNotADate', 'country': 'ZA', 'currency': 'ZAR'}
        )
        assert_status_code(400, response)
        assert_error_message('date query parameter must be in the format YYYY/MM/DD', response)

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
