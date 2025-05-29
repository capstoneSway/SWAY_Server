from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from jwt import decode as jwt_decode
from django.conf import settings

User = get_user_model()

@database_sync_to_async
def get_user(validated_token):
    try:
        username = validated_token['username']
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token_list = query_params.get("token")

        if token_list:
            token = token_list[0]  # ✅ 이 시점에서 token은 str
            print("🔑 JWT token (raw):", token)  # 👈 디버깅 위치 ①

            try:
                validated_token = UntypedToken(token)
                print("✅ JWT validated token:", validated_token)  # 👈 디버깅 위치 ②

                scope['user'] = await get_user(validated_token)

            except (InvalidToken, TokenError) as e:
                print("❌ Token error:", str(e))  # 👈 디버깅 위치 ③
                scope['user'] = AnonymousUser()
        else:
            print("⚠️ No token in query string.")  # 👈 디버깅 위치 ④
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)

# class JWTAuthMiddleware(BaseMiddleware):
#     async def __call__(self, scope, receive, send):
#         # 추출
#         query_string = scope.get("query_string", b"").decode()
#         query_params = parse_qs(query_string)
#         token_list = query_params.get("token")

#         if token_list:
#             token = token_list[0]
#             try:
#                 # 유효성 검증
#                 validated_token = UntypedToken(token[0])
#                 # 사용자 정보 설정
#                 scope['user'] = await get_user(validated_token)
#             except (InvalidToken, TokenError):
#                 scope['user'] = AnonymousUser()
#         else:
#             scope['user'] = AnonymousUser()

#         return await super().__call__(scope, receive, send)

# # ✅ 테스트 유저 주입 함수
# @database_sync_to_async
# def get_test_user():
#     return User.objects.get(email="test@test.com")

# class JWTAuthMiddleware(BaseMiddleware):
#     async def __call__(self, scope, receive, send):
#         headers = dict(scope['headers'])

#         if b'authorization' in headers:
#             try:
#                 token_type, token = headers[b'authorization'].decode().split()
#                 if token_type == 'Bearer':
#                     # JWT 유효성 검증
#                     validated_token = UntypedToken(token)
#                     # 유저 조회
#                     scope['user'] = await get_user(validated_token)
#                 else:
#                     scope['user'] = AnonymousUser()
#             except (InvalidToken, TokenError, KeyError, ValueError):
#                 scope['user'] = AnonymousUser()
#         else:
#             scope['user'] = AnonymousUser()
#             # ✅ JWT가 없으면 테스트 유저로 강제 지정
#             # scope['user'] = await get_test_user()  # ⚠️ 반드시 "test@test.com" 유저가 DB에 있어야 함

#         return await super().__call__(scope, receive, send)
