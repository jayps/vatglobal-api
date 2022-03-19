from django.contrib import admin

from vatglobal.api.models import Transaction, CurrencyHistory


class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'type',
        'country',
        'currency',
        'net',
        'vat',
    )


class CurrencyHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'from_currency',
        'to_currency',
        'conversion_rate',
    )


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(CurrencyHistory, CurrencyHistoryAdmin)