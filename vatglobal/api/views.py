import csv
import io
from datetime import datetime

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from vatglobal.api.serializers import UploadSerializer, TransactionSerializer


class TransactionUploadView(APIView):
    def post(self, request, format=None):
        serializer = UploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = request.FILES['file'] # Get the file from the request

        # Since we're not saving the file, just using it in memory, we have to do a little magic.
        # Check out https://andromedayelton.com/2017/04/25/adventures-with-parsing-django-uploaded-csv-files-in-python3/ for a more in depth explanation.
        # Basically, we're reading the file from memory as bytes, decoding that to a string, and producing an input for a CSV reader.
        decoded_file = file.read().decode('UTF-8')
        csv_string = io.StringIO(decoded_file)
        reader = csv.reader(csv_string, delimiter=',')

        next(reader) # Skip the header
        done = False
        line = 1
        while not done:
            try:
                row = next(reader) # We're using a generator here to save on memory.
                type = row[1].lower()
                # TODO: Conditionally execute this based on an environment variable.
                if type == 'sele':
                    type = 'sale'
                if type == 'parchase':
                    type = 'purchase'

                try:
                    transaction_date = datetime.strptime(row[0], '%Y/%m/%d').date()
                except ValueError as e:
                    # TODO: Consider returning an error here or conditionally continuing
                    pass

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
                line += 1

            except ValidationError as e:
                return Response(data=e.detail, status=status.HTTP_400_BAD_REQUEST)
            except StopIteration:
                done = True

        return Response(data=serializer.validated_data, status=status.HTTP_201_CREATED)