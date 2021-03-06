from django.urls import path

from vatglobal.api.views import TransactionUploadView, TransactionViewSet

urlpatterns = [
    path('processFile/', TransactionUploadView.as_view(), name='upload'),
    path('retrieveRows/', TransactionViewSet.as_view(), name='retrieve'),
]