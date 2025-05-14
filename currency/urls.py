from django.urls import path
from .views import (FetchInitialExchangeRatesView, 
                    FetchTodayExchangeRatesView, 
                    ExchangeRateOverviewView,
                    ExchangeMemoCreateView,
                    ExchangeMemoDeleteView)

urlpatterns = [
    path('fetch/initial/', FetchInitialExchangeRatesView.as_view(), name='fetch-initial'),
    path('fetch/daily/', FetchTodayExchangeRatesView.as_view(), name='fetch-daily'),
    path('overview/<str:cur_unit>/', ExchangeRateOverviewView.as_view(), name='currency-overview'),
    path('memo/', ExchangeMemoCreateView.as_view(), name='memo-create'),
    path('memo/<int:id>/', ExchangeMemoDeleteView.as_view(), name='memo-delete'),
]