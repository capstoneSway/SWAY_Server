from django.shortcuts import render, redirect
import environ, urllib, os
from pathlib import Path
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from rest_framework_simplejwt.views import TokenRefreshView
import requests
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from accounts.models import User
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, LogoutSerializer, NicknameSerializer, NationalitySerializer, ProfileUpdateSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser


# 환경변수 파일 관련 설정
env = environ.Env(DEBUG=(bool, False))
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(env_file=os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env('SECRET_KEY')
SOCIAL_AUTH_KAKAO_CLIENT_ID = env('SOCIAL_AUTH_KAKAO_CLIENT_ID')
SOCIAL_AUTH_KAKAO_SECRET = env('SOCIAL_AUTH_KAKAO_SECRET')
REDIRECT_URI = env('KAKAO_REDIRECT_URI')
# REDIRECT_URI = "http://127.0.0.1:8000/accounts/login/kakao/callback" # 로컬 테스트용

kakao_login_uri = "https://kauth.kakao.com/oauth/authorize"
kakao_token_uri = "https://kauth.kakao.com/oauth/token"
kakao_profile_uri = "https://kapi.kakao.com/v2/user/me"


# 카카오 로그인 요청(카카오 로그인 페이지로 이동)
class KakaoLoginView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        '''
        kakao code 요청
        '''
        client_id = SOCIAL_AUTH_KAKAO_CLIENT_ID
        redirect_uri = REDIRECT_URI

        uri = f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"

        res = redirect(uri)
        return res

# 카카오 로그인 콜백(카카오 로그인 후 콜백 처리)
class KakaoCallbackView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        '''
        kakao access_token 요청 및 user_info 요청
        '''
        try:
            data = request.query_params.copy()

            # access_token 발급 요청
            code = data.get('code')
            if not code:
                return Response({'error': 'Authorization code is required'}, 
                            status=status.HTTP_400_BAD_REQUEST)

            request_data = {
                'grant_type': 'authorization_code',
                'client_id': SOCIAL_AUTH_KAKAO_CLIENT_ID,
                'redirect_uri': REDIRECT_URI,
                'client_secret': SOCIAL_AUTH_KAKAO_SECRET,
                'code': code,
            }
            token_headers = {
                'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'
            }
            token_res = requests.post(kakao_token_uri, data=request_data, headers=token_headers)
            token_res.raise_for_status()  # Check for HTTP errors

            token_json = token_res.json()
            refresh_token = token_json.get('refresh_token')
            access_token = token_json.get('access_token')

            if not access_token:
                return Response({'error': 'Failed to get access token'}, 
                            status=status.HTTP_400_BAD_REQUEST)

            auth_headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
            }
            user_info_res = requests.get(kakao_profile_uri, headers=auth_headers)
            user_info_res.raise_for_status()  # Check for HTTP errors
            user_info_json = user_info_res.json()

            social_type = 'kakao'
            social_id = f"{social_type}_{user_info_json.get('id')}"

            kakao_account = user_info_json.get('kakao_account')
            if not kakao_account:
                return Response({'error': 'Failed to get kakao account info'}, 
                            status=status.HTTP_400_BAD_REQUEST)
                
            user_email = kakao_account.get('email')  # 여기가 None일 수 있음
            username = f"{kakao_account.get('profile', {}).get('nickname')}_{user_email}"
            profile_image = kakao_account.get('profile', {}).get('profile_image_url')
            gender = kakao_account.get("gender")
            # 이메일이 없으면 기본 이메일을 할당하거나 이메일을 요구할 수 있음
            if not user_email:
                # 기본 이메일을 제공하거나, 이메일 입력을 유도할 수 있음
                return Response({'error': 'Email is required from Kakao account'}, 
                                status=status.HTTP_400_BAD_REQUEST)

            # 임시로 사용자 정보만 반환
            response_data = {
                # 'social_type': social_type,
                # 'social_id': social_id,
                # 'user_email': user_email,
                # 'nickname': nickname,
                # 'profile_image': profile_image,
                # 'thumbnail_image': kakao_account.get('profile', {}).get('thumbnail_image_url'),
                # 'access_token': access_token,
                # 'refresh_token': refresh_token,
                # "gender" : gender,
            }

            # 이미 존재하는 사용자라면 로그인 처리
            
            try:
                user = User.objects.get(social_id=social_id)
                print("이미 존재합니다")
                #jwt 토큰으로 변환
                refresh = RefreshToken.for_user(user)
                jwt_token_data = {
                    'jwt_access': str(refresh.access_token),
                    'jwt_refresh': str(refresh),
                }
                response_data.update(jwt_token_data) #여기까지
                response = Response(response_data, status=status.HTTP_200_OK)
                response.set_cookie("jwt_access", value=str(refresh.access_token), max_age=None, expires=None, secure=True, samesite="None", httponly=True)
                response.set_cookie("jwt_refresh", value=str(refresh), max_age=None, expires=None, secure=True, samesite="None", httponly=True)
                return response
            except User.DoesNotExist:
                print("신규 생성")
                # 신규 사용자 생성
                user = User.objects.create_user(
                    email=user_email,
                    social_id=social_id,
                    social_type=social_type,
                    username=username,
                    profile_image=profile_image,
                    gender=gender
                )

        except requests.RequestException as e:
            return Response({'error': f'Failed to communicate with Kakao API: {str(e)}'}, 
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({'error': f'Unexpected error: {str(e)}'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        #jwt토큰변환2
        refresh = RefreshToken.for_user(user) 
        jwt_token_data = {
            'jwt_access': str(refresh.access_token),
            'jwt_refresh': str(refresh),
        }
        response_data.update(jwt_token_data) #여기까지
        return Response(response_data, status=status.HTTP_200_OK)

# access 토큰 재발급
class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('jwt_refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token is missing'}, status=status.HTTP_401_UNAUTHORIZED)

        request.data['refresh'] = refresh_token
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            if "access" in response.data:
                response.set_cookie("jwt_access", value=response.data["access"], httponly=True, secure=True, samesite="None")
            if "refresh" in response.data:
                response.set_cookie("jwt_refresh", value=response.data["refresh"], httponly=True, secure=True, samesite="None")

        return response

# 유저 정보 조회
class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
# class UserInfoView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         if user.profile_image_changed:
#             image_url = f"https://{settings.AWS_CLOUDFRONT_DOMAIN}/{user.profile_image_changed.name}"
#         else:
#             image_url = user.profile_image

#     def get(self, request):
#         user = request.user
#         return Response({
#             "username": user.username,
#             "profile_image": user.profile_image,
#             "nickname": user.nickname,
#             "nationality": user.nationality,
#             "gender": user.gender,
#         })

# 유저 로그아웃
class LogoutAPIView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response("Successfully logged out", status=status.HTTP_204_NO_CONTENT)

# 유저 닉네임 중복 체크
class CheckNicknameView(APIView):
    # permission_classes = [AllowAny,]
    def get(self, request):
        nickname = request.query_params.get("nickname")

        if not nickname:
            return Response({"error": "nickname is required."}, status=status.HTTP_400_BAD_REQUEST)

        exists = User.objects.filter(nickname=nickname).exists()
        return Response({"available": not exists})

# 유저 닉네임 저장
class SetNicknameView(generics.UpdateAPIView):
    serializer_class = NicknameSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

# 유저 국적 저장
class SetNationalityView(generics.UpdateAPIView):
    serializer_class = NationalitySerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

# 프로필 이미지 업데이트
class ProfileUpdateView(generics.UpdateAPIView):
    serializer_class = ProfileUpdateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user

# 유저 탈퇴
class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        
        # 사용자 탈퇴와 관련된 모든 처리
        try:
            user.delete_user_and_participations()  # 탈퇴 전 필요한 로직 수행
            return Response({'detail': 'Account deleted successfully.'}, status=204)
        except Exception as e:
            return Response({'detail': f'Error: {str(e)}'}, status=400)

# 유저 고유 FCM 토큰 업데이트
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_fcm_token(request):
    user = request.user
    token = request.data.get('fcm_token')

    if not token:
        return Response({'error': 'FCM token is required.'}, status=400)

    user.fcm_token = token
    user.save()
    return Response({'message': 'FCM token updated successfully.'})
#==============================================================================
"""
# 로컬 세팅
from .models import CustomUser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer, SignupSerializer
from django.contrib import auth
from django.contrib.auth.hashers import make_password

# Create your views here.
@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = auth.authenticate(
            request=request,
            username=serializer.data['username'],
            password=serializer.data['password']
        )
        if user is not None:
            auth.login(request, user)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        new_user = serializer.save(password = make_password(serializer.validated_data['password']))
        auth.login(request, new_user)
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout(request):
    auth.logout(request)
    return Response(status=status.HTTP_200_OK)
"""