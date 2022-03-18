from django.urls import path

from vatglobal.api.views import TransactionUploadView, TransactionViewSet

urlpatterns = [
    path('processFile/', TransactionUploadView.as_view()),
    path('retrieveRows/', TransactionViewSet.as_view()),
]