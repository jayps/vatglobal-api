import csv
import io
import json

import requests


# Since we're not saving the file, just using it in memory, we have to do a little magic.
# Check out https://andromedayelton.com/2017/04/25/adventures-with-parsing-django-uploaded-csv-files-in-python3/ for a more in depth explanation.
# Basically, we're reading the file from memory as bytes, decoding that to a string, and producing an input for a CSV reader.
from datetime import datetime

from rest_framework.exceptions import ValidationError

from vatglobal.api.serializers import TransactionSerializer


def get_line_from_csv(file):
    decoded_file = file.read().decode('UTF-8')
    csv_string = io.StringIO(decoded_file)
    reader = csv.reader(csv_string, delimiter=',')
    for line in reader:
        yield line

def create_transaction_from_row(row):
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
    transaction.is_valid(raise_exception=True)
    transaction.save()

    return True

def get_currency_conversion(from_currency, to_currency, date):
    year = date.year
    month = date.strftime('%m')
    day = date.strftime('%d')
    resource = 'data'
    frequency = 'D'
    exr_type = 'SP00'
    series_variation = 'A'
    data_flow = 'EXR' # exchange rates
    url = f'https://sdw-wsrest.ecb.europa.eu/service/{resource}/{data_flow}/{frequency}.{to_currency}.{from_currency}.{exr_type}.{series_variation}?startPeriod={year}-{month}-{day}&endPeriod={year}-{month}-{day}'
    response = requests.get(url, headers={'Accept': 'application/json'})
    response.raise_for_status()
    results = json.loads(response.text)

    # This took some figuring out to do from looking at the responses and working out some jsonpath stuff in insomnia
    return results.get('dataSets')[0].get('series').get('0:0:0:0:0').get('observations').get('0')[0]