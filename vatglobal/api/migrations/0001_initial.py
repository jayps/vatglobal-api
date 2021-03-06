# Generated by Django 4.0.3 on 2022-03-17 19:34

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('type', models.CharField(choices=[('sale', 'Sale'), ('purchase', 'Purchase')], max_length=10)),
                ('country', models.CharField(max_length=32)),
                ('currency', models.CharField(max_length=32)),
                ('net', models.FloatField()),
                ('vat', models.FloatField()),
            ],
        ),
    ]
