from django.urls import path
from .views import (FetchInitialExchangeRatesView, 
                    FetchTodayExchangeRatesView, 
                    ExchangeRateOverviewView,
                    ExchangeMemoCreateView,
                    ExchangeMemoDeleteView,
                    FetchExchangeRatesByDateView,
                    UserExchangeMemoListView)

urlpatterns = [
    path('fetch/initial/', FetchInitialExchangeRatesView.as_view(), name='fetch-initial'),
    path('fetch/daily/', FetchTodayExchangeRatesView.as_view(), name='fetch-daily'),
    path('overview/<str:cur_unit>/', ExchangeRateOverviewView.as_view(), name='currency-overview'),
    path('memo/', ExchangeMemoCreateView.as_view(), name='memo-create'),
    path('memo/<int:id>/delete/', ExchangeMemoDeleteView.as_view(), name='memo-delete'),
    path('memo/my/', UserExchangeMemoListView.as_view(), name='memo-my-list'),
    path('fetch/by-date/', FetchExchangeRatesByDateView.as_view(), name='fetch_by_date'),
]