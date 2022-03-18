from django.urls import path, include
from rest_framework.routers import DefaultRouter

from vatglobal.api.views import TransactionUploadView, TransactionViewSet

router = DefaultRouter()
router.register('retrieveRows', TransactionViewSet)

urlpatterns = [
    path('processFile/', TransactionUploadView.as_view()),
    path('', include(router.urls))
]