import csv
import io


# Since we're not saving the file, just using it in memory, we have to do a little magic.
# Check out https://andromedayelton.com/2017/04/25/adventures-with-parsing-django-uploaded-csv-files-in-python3/ for a more in depth explanation.
# Basically, we're reading the file from memory as bytes, decoding that to a string, and producing an input for a CSV reader.
from datetime import datetime

from rest_framework.exceptions import ValidationError

from vatglobal.api.serializers import TransactionSerializer


def get_reader_from_file(file):
    decoded_file = file.read().decode('UTF-8')
    csv_string = io.StringIO(decoded_file)
    return csv.reader(csv_string, delimiter=',')


def create_transaction_from_row(row, row_index):
    type = row[1].lower()
    # TODO: Conditionally execute this based on an environment variable.
    if type == 'sele':
        type = 'sale'
    if type == 'parchase':
        type = 'purchase'

    try:
        transaction_date = datetime.strptime(row[0], '%Y/%m/%d').date()
    except ValueError as e:
        raise ValidationError(f'Invalid date at line {row_index}: {row[0]}')

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