from django.urls import path
import urllib
from .views import (KakaoLoginView, 
                    KakaoCallbackView, 
                    UserInfoView, 
                    LogoutAPIView, 
                    CheckNicknameView,
                    SetNicknameView,
                    SetNationalityView,
                    CookieTokenRefreshView,
                    DeleteAccountView)

#app_name = 'accounts'

urlpatterns = [
    path('login/kakao/', KakaoLoginView.as_view(), name='kakao_login'),
    path('login/kakao/callback/', KakaoCallbackView.as_view(), name='kakao_callback'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('user/info/', UserInfoView.as_view(), name='user_info'),
    path('logout/kakao/', LogoutAPIView.as_view(), name='kakao_logout'),
    path('check-nickname/', CheckNicknameView.as_view(), name='check-nickname'),
    path('set-nickname/', SetNicknameView.as_view(), name='set-nickname'),
    path('set-nationality/', SetNationalityView.as_view(), name='set-nationality'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),   
]