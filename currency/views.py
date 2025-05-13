from django.shortcuts import render
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ExchangeRate
from .serializers import ExchangeRateSerializer
from django.conf import settings
from datetime import datetime, timedelta


# Create your views here.
# 최초 7일치 데이터 저장용 View
class FetchInitialExchangeRatesView(APIView):
    def get(self, request):
        base_url = 'https://www.koreaexim.go.kr/site/program/financial/exchangeJSON'
        today = datetime.today()
        days = [today - timedelta(days=i) for i in range(0, 12)]

        for day in days:
            date_str = day.strftime("%Y%m%d")
            params = {
                'authkey': settings.EXIM_API_KEY,
                'searchdate': date_str,
                'data': 'AP01',
            }
            response = requests.get(base_url, params=params)
            if response.status_code != 200:
                continue
            data = response.json()
            for item in data:
                serializer = ExchangeRateSerializer(data={
                    'cur_unit': item.get('cur_unit'),
                    'cur_nm': item.get('cur_nm'),
                    'ttb': item.get('ttb'),
                    'tts': item.get('tts'),
                    'deal_bas_r': item.get('deal_bas_r'),
                    'bkpr': item.get('bkpr'),
                    'y_efee_r': item.get('yy_efee_r'),
                    'ten_d_efee_r': item.get('ten_dd_efee_r'),
                    'kftc_deal_bas_r': item.get('kftc_deal_bas_r'),
                    'kftc_bkpr': item.get('kftc_bkpr'),
                    'date': day.date()
                })
                if serializer.is_valid():
                    ExchangeRate.objects.update_or_create(
                        cur_unit=item.get('cur_unit'),
                        date=day.date(),
                        defaults=serializer.validated_data
                    )
        
        return Response({'message': '최근 12일 환율 데이터 저장 완료'}, status=status.HTTP_200_OK)
        
# 매일 환율 저장 View
class FetchTodayExchangeRatesView(APIView):
    def get(self, request):
        today = datetime.today().strftime("%Y%m%d")
        base_url = 'https://www.koreaexim.go.kr/site/program/financial/exchangeJSON'
        params = {
            'authkey': settings.EXIM_API_KEY,
            'searchdate': today,
            'data': 'AP01',
        }
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            return Response({'error': 'API 요청 실패'}, status=status.HTTP_502_BAD_GATEWAY)

        data = response.json()
        for item in data:
            serializer = ExchangeRateSerializer(data={
                'cur_unit': item.get('cur_unit'),
                'cur_nm': item.get('cur_nm'),
                'ttb': item.get('ttb'),
                'tts': item.get('tts'),
                'deal_bas_r': item.get('deal_bas_r'),
                'bkpr': item.get('bkpr'),
                'y_efee_r': item.get('yy_efee_r'),
                'ten_d_efee_r': item.get('ten_dd_efee_r'),
                'kftc_deal_bas_r': item.get('kftc_deal_bas_r'),
                'kftc_bkpr': item.get('kftc_bkpr'),
                'date': datetime.today().date()
            })
            if serializer.is_valid():
                ExchangeRate.objects.update_or_create(
                    cur_unit=item.get('cur_unit'),
                    date=datetime.today().date(),
                    defaults=serializer.validated_data
                )

        return Response({'message': '오늘의 환율 데이터 저장 완료'}, status=status.HTTP_200_OK)


class ExchangeRateOverviewView(APIView):
    def get(self, request, cur_unit):
        today = datetime.today().date()
        start = today - timedelta(days=6)  # 오늘 포함 7일간

        rates = ExchangeRate.objects.filter(
            cur_unit=cur_unit.upper(),
            date__range=(start, today)
        ).order_by('date')

        if not rates.exists():
            return Response({"error": "해당 통화의 환율 정보가 없습니다."}, status=404)

        history = [
            {
                "date": r.date.strftime("%Y-%m-%d"),
                "rate": float(r.deal_bas_r.replace(',', ''))
            }
            for r in rates
        ]

        today_obj = next((r for r in rates if r.date == today), None)
        if today_obj:
            today_data = {
                "date": today_obj.date.strftime("%Y-%m-%d"),
                "cur_unit": today_obj.cur_unit,
                "cur_nm": today_obj.cur_nm,
                "rate": float(today_obj.deal_bas_r.replace(',', ''))
            }
        else:
            today_data = None  # 오늘 데이터가 없을 수도 있음 (API 실패 등)

        return Response({
            "today": today_data,
            "history": history
        })
# -----------------------------------test-----------------------------------------
# class FetchExchangeRateView(APIView):
#     def get(self, request):
#         url = "https://www.koreaexim.go.kr/site/program/financial/exchangeJSON"
#         params = {
#             'authkey': settings.EXIM_API_KEY,  # settings.py에 설정해둘 것
#             'searchdate': '20250512',  # 오늘 날짜 기본
#             'data': 'AP01',
#         }

#         response = requests.get(url, params=params)
#         if response.status_code != 200:
#             return Response({'error': 'API 요청 실패'}, status=status.HTTP_502_BAD_GATEWAY)

#         data = response.json()

#         # 오류코드 확인
#         if isinstance(data, dict) and data.get('RESULT') != 1:
#             return Response({'error': 'API 데이터 오류'}, status=status.HTTP_400_BAD_REQUEST)

#         # 기존 데이터 삭제 (선택)
#         ExchangeRate.objects.all().delete()

#         for item in data:
#             serializer = ExchangeRateSerializer(data={
#                 'cur_unit': item.get('cur_unit'),
#                 'cur_nm': item.get('cur_nm'),
#                 'ttb': item.get('ttb'),
#                 'tts': item.get('tts'),
#                 'deal_bas_r': item.get('deal_bas_r'),
#                 'bkpr': item.get('bkpr'),
#                 'y_efee_r': item.get('yy_efee_r'),
#                 'ten_d_efee_r': item.get('ten_dd_efee_r'),
#                 'kftc_deal_bas_r': item.get('kftc_deal_bas_r'),
#                 'kftc_bkpr': item.get('kftc_bkpr'),
#             })
#             if serializer.is_valid():
#                 serializer.save()
#             else:
#                 print("유효성 검사 실패:", serializer.errors)

#         return Response({'message': '환율 정보가 성공적으로 갱신되었습니다.'}, status=status.HTTP_200_OK)
