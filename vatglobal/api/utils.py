import csv
import io
from datetime import datetime

import requests
from requests import HTTPError
from rest_framework.exceptions import ValidationError

from vatglobal.api.models import CurrencyHistory
from vatglobal.api.serializers import TransactionSerializer


# Since we're not saving the file, just using it in memory, we have to do a little magic.
# Check out https://andromedayelton.com/2017/04/25/adventures-with-parsing-django-uploaded-csv-files-in-python3/ for a more in depth explanation.
# Basically, we're reading the file from memory as bytes, decoding that to a string, and producing an input for a CSV reader.
def get_line_from_csv(file):
    decoded_file = file.read().decode('UTF-8')
    csv_string = io.StringIO(decoded_file)
    reader = csv.reader(csv_string, delimiter=',')
    for line in reader:
        yield line


def create_transaction_from_row(row):
    # Row format should be Date,Purchase/Sale,Country,Currency,Net,VAT
    type = row[1].lower()

    try:
        transaction_date = datetime.strptime(row[0], '%Y/%m/%d').date()
    except ValueError as e:
        raise ValidationError(f'Invalid date {row[0]}')

    if transaction_date.year != 2020:
        return False

    transaction = TransactionSerializer(
        data={
            'date': transaction_date,
            'type': type,
            'country': row[2],
            'currency': row[3],
            'net': row[4],
            'vat': row[5],
        }
    )

    # Throw validation errors according to the rule of the serializer. Things like invalid 'type' fields will come up here.
    transaction.is_valid(raise_exception=True)
    transaction.save()

    return True

# There's great information on the ECB API at
# https://www.datacareer.de/blog/accessing-ecb-exchange-rate-data-in-python/
# AND https://sdw-wsrest.ecb.europa.eu/help/
def get_currency_conversion_rate_from_ecb(date, from_currency, to_currency):
    year = date.year
    month = date.strftime('%m')
    day = date.strftime('%d')
    resource = 'data'
    frequency = 'D'
    exr_type = 'SP00'
    series_variation = 'A'
    data_flow = 'EXR'  # exchange rates
    url = f'https://sdw-wsrest.ecb.europa.eu/service/{resource}/{data_flow}/{frequency}.{to_currency}.{from_currency}.{exr_type}.{series_variation}?startPeriod={year}-{month}-{day}&endPeriod={year}-{month}-{day}'
    response = requests.get(url, headers={'Accept': 'application/json'})
    response.raise_for_status()
    results = response.json()
    # This took some figuring out to do from looking at the responses and working out some jsonpath stuff in insomnia
    conversion_rate = results.get('dataSets')[0].get('series').get('0:0:0:0:0').get('observations').get('0')[0]
    return conversion_rate


def get_currency_conversion(from_currency, to_currency, date):
    # Check for existing history records first. If we have none, fetch from the ECB API.
    stored_conversion_record = CurrencyHistory.objects.filter(from_currency=from_currency, to_currency=to_currency,
                                                              date=date)
    if stored_conversion_record.exists():
        return stored_conversion_record.first().conversion_rate

    conversion_rate = get_currency_conversion_rate_from_ecb(date, from_currency, to_currency)

    CurrencyHistory.objects.create(from_currency=from_currency, to_currency=to_currency, date=date,
                                   conversion_rate=conversion_rate)

    return conversion_rate


# Go over a list of transactions and convert their vat, net and currency fields to the desired currency.
def convert_transaction_list_currency(queryset, desired_currency, filtered_date):
    from_currencies_list = list(
        set([transaction.currency for transaction in queryset if transaction.currency != desired_currency]))
    currency_map = {}
    for currency in from_currencies_list:
        try:
            currency_map[currency] = get_currency_conversion(currency, desired_currency, filtered_date)
        except HTTPError:
            # Just changing the error message here to something more readable.
            raise HTTPError(
                f'Could not fetch conversion rate from {currency} to {desired_currency} for {filtered_date}')

    for transaction in queryset:
        # Remember to not convert from ZAR to ZAR, for instance :) This would be strange.
        if transaction.currency is not desired_currency and currency_map.get(transaction.currency) is not None:
            transaction.net = transaction.net * currency_map[transaction.currency]
            transaction.vat = transaction.vat * currency_map[transaction.currency]
            transaction.currency = desired_currency

    return queryset
