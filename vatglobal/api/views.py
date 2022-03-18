import csv
import io
from datetime import datetime

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from vatglobal.api.serializers import UploadSerializer, TransactionSerializer
from vatglobal.api.utils import get_reader_from_file, create_transaction_from_row


class TransactionUploadView(APIView):
    def post(self, request, format=None):
        serializer = UploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = request.FILES['file'] # Get the file from the request

        reader = get_reader_from_file(file)

        next(reader) # Skip the header
        done = False
        row_index = 1

        while not done:
            try:
                row = next(reader) # We're using a generator here to save on memory.
                create_transaction_from_row(row, row_index)
                row_index += 1
            except ValidationError as e:
                pass
                # return Response(data=e.detail, status=status.HTTP_400_BAD_REQUEST)
            except StopIteration:
                done = True

        return Response(data=serializer.validated_data, status=status.HTTP_201_CREATED)