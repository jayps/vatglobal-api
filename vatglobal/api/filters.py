import django_filters
from django_filters import filters

from vatglobal.api.models import Transaction


class TransactionFilter(django_filters.FilterSet):
    date = filters.DateFilter()

    # Allowing for 2 character ISO-3166-1 (alpha-2) codes as per the example in the instructions, such as
    # /retrieveRows?country=DE&date=2020/08/05&currency=GBP
    # see: https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes.
    country = filters.CharFilter(max_length=2, min_length=2)

    class Meta:
        model = Transaction
        fields = {
            'date': ['exact', ],
            'country': ['exact', ]
        }
