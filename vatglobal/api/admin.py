from django.contrib import admin

from vatglobal.api.models import Transaction


class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'type',
        'country',
        'currency',
        'net',
        'vat',
    )


admin.site.register(Transaction, TransactionAdmin)