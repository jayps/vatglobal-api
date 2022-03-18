from rest_framework import serializers

from vatglobal.api.models import Transaction


class UploadRequestSerializer(serializers.Serializer):
    file = serializers.FileField()
    skip_errors = serializers.BooleanField(default=False)


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'