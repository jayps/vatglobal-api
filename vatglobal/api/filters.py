import django_filters
from django_filters import filters

from vatglobal.api.models import Transaction


class TransactionFilter(django_filters.FilterSet):
    date = filters.DateFilter()

    # I'm allowing any character filter for country since ISO-3166 allows for full country names, and ISO-3166-1
    # allows for alpha-2 and alpha-3 codes as at https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes.
    country = filters.CharFilter()

    class Meta:
        model = Transaction
        fields = {
            'date': ['exact', ],
            'country': ['exact', ]
        }
