from django.urls import path
import urllib
from .views import KakaoLoginView, KakaoCallbackView
#from .views import * #로컬

#app_name = 'accounts' #로컬

urlpatterns = [
    path('login/kakao/', KakaoLoginView.as_view(), name='kakao_login'),
    path('login/kakao/callback/', KakaoCallbackView.as_view(), name='kakao_callback'),
    #path('login/', login), #로컬
    #path('signup/', signup), #로컬
    #path('logout/', logout) #로컬
]