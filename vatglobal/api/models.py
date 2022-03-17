import uuid

from django.db import models


class Transaction(models.Model):
    TYPE_CHOICES = (
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    country = models.CharField(max_length=32)
    currency = models.CharField(max_length=32)
    net = models.FloatField()
    vat = models.FloatField()
