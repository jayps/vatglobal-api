from datetime import datetime

from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from vatglobal.api.data.iso_3166_1_countries import is_valid_country_code
from vatglobal.api.data.iso_4217_currencies import is_valid_currency_code
from vatglobal.api.models import Transaction
from vatglobal.api.serializers import UploadRequestSerializer, TransactionSerializer
from vatglobal.api.utils import create_transaction_from_row, get_line_from_csv, get_currency_conversion


class TransactionUploadView(APIView):
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
    def get(self, request):
        queryset = Transaction.objects.order_by('date')

        date = request.GET.get('date')
        if not date:
            return Response(data={'error': 'date query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            filtered_date = datetime.strptime(date, '%Y/%m/%d').date()
        except ValueError as e:
            return Response(data={'error': 'date query parameter must be in the format YYYY/MM/DD'},
                            status=status.HTTP_400_BAD_REQUEST)

        country = request.GET.get('country')
        if not is_valid_country_code(country):
            return Response(data={'error': 'country query parameter must be ISO-3166-1 alpha-2'},
                            status=status.HTTP_400_BAD_REQUEST)

        desired_currency = request.GET.get('currency')
        if desired_currency and not is_valid_currency_code(desired_currency):
            return Response(data={'error': 'currency query parameter must be ISO-4217'},
                            status=status.HTTP_400_BAD_REQUEST)

        queryset = queryset.filter(date=filtered_date, country=country)#[:5]

        if desired_currency:
            from_currencies_list = list(set([transaction.currency for transaction in queryset if transaction.currency != desired_currency]))
            currency_map = {}
            for currency in from_currencies_list:
                try:
                    currency_map[currency] = get_currency_conversion(currency, desired_currency, filtered_date)
                except Exception as e:
                    return Response({'error': f'Could not fetch exchange rates for {currency} to {desired_currency} for {filtered_date}: {str(e)}'})
            for transaction in queryset:
                transaction.net = transaction.net * currency_map[transaction.currency]
                transaction.vat = transaction.vat * currency_map[transaction.currency]
                transaction.currency = desired_currency

        return Response(data=TransactionSerializer(queryset, many=True).data, status=status.HTTP_200_OK)
