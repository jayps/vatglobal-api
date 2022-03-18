import csv
import io


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