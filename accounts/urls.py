from django.urls import path
import urllib
from .views import KakaoLoginView, KakaoCallbackView

#app_name = 'accounts'

urlpatterns = [
    path('login/kakao/', KakaoLoginView.as_view(), name='kakao_login'),
    path('login/kakao/callback/', KakaoCallbackView.as_view(), name='kakao_callback'),
]