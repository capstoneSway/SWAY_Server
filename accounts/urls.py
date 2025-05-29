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
                    DeleteAccountView,
                    ProfileUpdateView)
from django.urls import path
from .views import update_fcm_token

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
    path('user/info/image-update/', ProfileUpdateView.as_view(), name='profile-image-update'),
    path('fcm-token/', update_fcm_token, name='update_fcm_token'),
]