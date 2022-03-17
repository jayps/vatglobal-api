from rest_framework import serializers

from vatglobal.api.models import Transaction


class UploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'