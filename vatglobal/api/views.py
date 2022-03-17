import csv
import io

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from vatglobal.api.serializers import UploadSerializer


class TransactionUploadView(APIView):
    def post(self, request, format=None):
        serializer = UploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = request.FILES['file']
        decoded_file = file.read().decode('UTF-8')
        csv_string = io.StringIO(decoded_file)
        for line in csv.reader(csv_string, delimiter=','):
            print(line)


        return Response(data=serializer.validated_data, status=status.HTTP_201_CREATED)