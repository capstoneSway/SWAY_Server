from django.urls import path, include
import urllib
from .views import kakao_login, kakao_callback

urlpatterns = [
    path('accounts/login/kakao/', kakao_login, name='kakao_login'),
    path('accounts/login/kakao/callback', kakao_callback, name='kakao_callback'),
]