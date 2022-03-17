from django.urls import path

from vatglobal.api.views import TransactionUploadView

urlpatterns = [
    path('transactions/upload/', TransactionUploadView.as_view()),
]