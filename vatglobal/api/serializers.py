from rest_framework import serializers

from vatglobal.api.data.iso_3166_1_countries import is_valid_country_code
from vatglobal.api.data.iso_4217_currencies import is_valid_currency_code
from vatglobal.api.models import Transaction


class UploadRequestSerializer(serializers.Serializer):
    file = serializers.FileField()
    skip_errors = serializers.BooleanField(default=False)


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class TransactionFiltersSerializer(serializers.Serializer):
    date = serializers.DateField(input_formats=['%Y/%m/%d'])
    country = serializers.CharField()
    currency = serializers.CharField(required=False)

    @staticmethod
    def validate_country(country):
        if not is_valid_country_code(country):
            raise serializers.ValidationError('country query parameter must be ISO-3166-1 alpha-2')

        return country

    @staticmethod
    def validate_currency(currency):
        if not is_valid_currency_code(currency):
            raise serializers.ValidationError('currency query parameter must be ISO-4217')

        return currency