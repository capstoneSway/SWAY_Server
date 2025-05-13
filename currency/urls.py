from django.urls import path
from .views import FetchInitialExchangeRatesView, FetchTodayExchangeRatesView, ExchangeRateOverviewView

urlpatterns = [
    path('fetch/initial/', FetchInitialExchangeRatesView.as_view(), name='fetch-initial'),
    path('fetch/daily/', FetchTodayExchangeRatesView.as_view(), name='fetch-daily'),
    path('overview/<str:cur_unit>/', ExchangeRateOverviewView.as_view(), name='currency-overview'),
]