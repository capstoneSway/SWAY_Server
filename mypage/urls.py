from django.urls import path
from .views import MyPageView

app_name = 'mypage'

urlpatterns = [
    path('', MyPageView.as_view(), name='mypage-view'),
]