from django.shortcuts import render, redirect
import environ, urllib, os
from pathlib import Path
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework import status
import requests

# 환경변수 파일 관련 설정
env = environ.Env(DEBUG=(bool, False))
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(env_file=os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env('SECRET_KEY')
SOCIAL_AUTH_KAKAO_CLIENT_ID = env('SOCIAL_AUTH_KAKAO_CLIENT_ID')
SOCIAL_AUTH_KAKAO_SECRET = env('SOCIAL_AUTH_KAKAO_SECRET')
REDIRECT_URI = 'http://127.0.0.1:8000/accounts/login/kakao/callback'

kakao_login_uri = "https://kauth.kakao.com/oauth/authorize"
kakao_token_uri = "https://kauth.kakao.com/oauth/token"
kakao_profile_uri = "https://kapi.kakao.com/v2/user/me"

# code 요청
# def kakao_login(request):
#     app_rest_api_key = SOCIAL_AUTH_KAKAO_CLIENT_ID
#     redirect_uri = "http://127.0.0.1:8000/accounts/login/kakao/callback"
#     return redirect(
#         f"https://kauth.kakao.com/oauth/authorize?client_id={app_rest_api_key}&redirect_uri={redirect_uri}&response_type=code"
#     )
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


# access token 요청
# def kakao_callback(request):  


#     code = request.GET.get("code")
#     print("인가 코드: ", code)                                                                
#     # params = urllib.parse.urlencode(request.GET)                                      
#     # return redirect(f'http://127.0.0.1:8000/accounts/login/kakao/callback?{params}')   
#     return render(request, 'kakao_callback.html', {"code": code})


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
                
            user_email = kakao_account.get('email')
            
            # TODO: 회원가입 및 로그인 처리 로직 구현 필요
            # 임시로 사용자 정보만 반환
            response_data = {
                'social_type': social_type,
                'social_id': social_id,
                'user_email': user_email,
                'nickname': kakao_account.get('profile', {}).get('nickname'),
                'profile_image': kakao_account.get('profile', {}).get('profile_image_url'),
                'thumbnail_image': kakao_account.get('profile', {}).get('thumbnail_image_url'),
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except requests.RequestException as e:
            return Response({'error': f'Failed to communicate with Kakao API: {str(e)}'}, 
                          status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({'error': f'Unexpected error: {str(e)}'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)