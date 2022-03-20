from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from requests import HTTPError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from vatglobal.api.models import Transaction
from vatglobal.api.serializers import UploadRequestSerializer, TransactionSerializer, TransactionFiltersSerializer
from vatglobal.api.utils import create_transaction_from_row, get_line_from_csv, convert_transaction_list_currency


class TransactionUploadView(APIView):
    parser_classes = (MultiPartParser,)
    @swagger_auto_schema(
        operation_description='Upload a CSV containing transactions.',
        responses={
            201: 'Successfully stored transactions',
            400: 'Invalid content in CSV',
            500: 'Internal server error / something unexpected happened'
        },
        request_body=UploadRequestSerializer
    )
    def post(self, request, format=None):
        serializer = UploadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        skip_errors = serializer.validated_data.get('skip_errors', False)

        file = request.FILES['file']  # Get the file from the request

        reader = get_line_from_csv(file)
        next(reader)  # Skip header

        with transaction.atomic():
            for line in reader:
                try:
                    create_transaction_from_row(line)
                except ValidationError as e:
                    if skip_errors:
                        continue
                    return Response(data=e.detail, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_201_CREATED)


class TransactionViewSet(APIView):
    @swagger_auto_schema(
        operation_description='Retrieve a list of transactions.',
        responses={
            200: 'Successfully retrieved transactions',
            404: 'Could not retrieve conversion rates from ECB API',
        },
        query_serializer=TransactionFiltersSerializer
    )
    def get(self, request):
        filters = TransactionFiltersSerializer(data=request.GET)
        filters.is_valid(raise_exception=True)

        filtered_date = filters.validated_data.get('date')
        country = filters.validated_data.get('country')
        desired_currency = filters.validated_data.get('currency')

        # Intial queryset
        queryset = Transaction.objects.order_by('date').filter(date=filtered_date, country=country)

        if desired_currency:
            try:
                queryset = convert_transaction_list_currency(queryset, desired_currency, filtered_date)
            except HTTPError as e:
                return Response(data={'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response(data=TransactionSerializer(queryset, many=True).data, status=status.HTTP_200_OK)
