from django.urls import path
from .views import FetchExchangeRateView

urlpatterns = [
    path('fetch/', FetchExchangeRateView.as_view(), name='fetch-exchange-rate'),
]
