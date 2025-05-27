from django.shortcuts import render
import requests
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import ExchangeRate
from .serializers import ExchangeRateSerializer, ExchangeMemoSerializer
from .models import ExchangeMemo
from django.conf import settings
from datetime import datetime, timedelta
from .currency_name import CURRENCY_NAME_MAP

# Create your views here.
# 최근 14일 환율 저장 View
class FetchInitialExchangeRatesView(APIView):
    def get(self, request):
        base_url = 'https://api.exchangerate.host/historical'
        today = datetime.today()
        days = [today - timedelta(days=i) for i in reversed(range(14))]

        currencies = ",".join([
            "AED", "AUD", "BHD", "BND", "CAD", "CHF", "CNY", "DKK", "EUR", "GBP",
            "HKD", "IDR", "JPY", "KWD", "MYR", "NOK", "NZD", "SAR", "SEK", "SGD", "THB", "USD"
        ])

        saved_count = 0

        for day in days:
            date_str = day.strftime('%Y-%m-%d')

            params = {
                'access_key': settings.CURRENCYLAYER_API_KEY,
                'date': date_str,
                'source': 'KRW',
                'currencies': currencies
            }

            response = requests.get(base_url, params=params)
            if response.status_code != 200:
                continue

            data = response.json()
            quotes = data.get('quotes', {})
            date_str_from_api = data.get("date")
            if not date_str_from_api:
                continue

            try:
                date_obj = datetime.strptime(date_str_from_api, "%Y-%m-%d").date()
            except ValueError:
                continue

            for key, rate in quotes.items():
                # key 예시: "KRWUSD" → target_currency = "USD"
                if not key.startswith("KRW"):
                    continue
                target_currency = key[3:]
                unit_rate = round(1 / rate, 4) if rate else None
                currency_name = CURRENCY_NAME_MAP.get(target_currency, '')

                ExchangeRate.objects.update_or_create(
                    date=date_obj,
                    base_currency='KRW',
                    target_currency=target_currency,
                    defaults={
                        'rate': rate,
                        'unit_rate': unit_rate,
                        'currency_name': currency_name,
                    }
                )
                saved_count += 1

        return Response({'message': f'최근 14일 환율 데이터 저장 완료 (총 {saved_count}건)'}, status=status.HTTP_200_OK)


# 매일 환율 저장 View
class FetchTodayExchangeRatesView(APIView):
    def get(self, request):
        base_url = 'https://api.exchangerate.host/live'
        date_obj = datetime.today().date()
        currencies = ",".join([
            "AED","AUD","BHD","BND","CAD","CHF","CNY","DKK","EUR","GBP",
            "HKD","IDR","JPY","KWD","MYR","NOK","NZD","SAR","SEK","SGD","THB","USD"
        ])

        params = {
            'access_key': settings.CURRENCYLAYER_API_KEY,
            'source': 'KRW',
            'currencies': currencies,
        }

        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            return Response({'error': 'API 요청 실패'}, status=status.HTTP_502_BAD_GATEWAY)

        data = response.json()
        quotes = data.get('quotes', {})

        if not quotes:
            return Response({'error': 'quotes가 비어 있음', 'raw': data}, status=204)

        for key, rate in quotes.items():
            if not key.startswith('KRW'):
                continue
            target_currency = key[3:]
            unit_rate = round(1 / rate, 4) if rate else None
            currency_name = CURRENCY_NAME_MAP.get(target_currency, '')

            ExchangeRate.objects.update_or_create(
                date=date_obj,
                base_currency='KRW',
                target_currency=target_currency,
                defaults={
                    'rate': rate,
                    'unit_rate': unit_rate,
                    'currency_name': currency_name,
                }
            )
        
        ExchangeRate.objects.update_or_create(
            date=date_obj,
            base_currency='KRW',
            target_currency='KRW',
            defaults={
                'rate': 1.0,
                'unit_rate': 1.0,
                'currency_name': '대한민국 원화',
            }
        )

        return Response({'message': f'{date_obj} 환율 저장 완료'}, status=status.HTTP_200_OK)


# 환율 메모 CRUD
class ExchangeMemoCreateView(generics.CreateAPIView):
    serializer_class = ExchangeMemoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ExchangeMemoDeleteView(generics.DestroyAPIView):
    serializer_class = ExchangeMemoSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return ExchangeMemo.objects.filter(user=self.request.user)


# 환율그래프 및 계산 조회 + 메모 조회 View
class ExchangeRateOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, cur_unit):
        user = request.user
        today = datetime.today().date()
        start = today - timedelta(days=6)  # 최근 7일 (오늘 포함)

        rates = ExchangeRate.objects.filter(
            target_currency=cur_unit.upper(),
            date__range=(start, today)
        ).order_by('date')

        if not rates.exists():
            return Response({"error": "해당 통화의 환율 정보가 없습니다."}, status=404)

        history = [
            {
                "date": r.date.strftime("%Y-%m-%d"),
                "rate": r.unit_rate
            }
            for r in rates
        ]

        today_obj = next((r for r in rates if r.date == today), None)
        today_data = {
            "date": today_obj.date.strftime("%Y-%m-%d"),
            "cur_unit": today_obj.target_currency,
            "cur_nm": today_obj.currency_name,
            "rate": today_obj.unit_rate
        } if today_obj else None

        memos = ExchangeMemo.objects.filter(
            user=user,
            from_currency=cur_unit.upper()
        ).order_by('-date')

        serialized_memos = ExchangeMemoSerializer(memos, many=True).data

        return Response({
            "today": today_data,
            "history": history,
            "memos": serialized_memos,
        })


# 특정 날짜 환율 저장 View(응급용)
class FetchExchangeRatesByDateView(APIView):
    def get(self, request):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'error': 'date 파라미터를 제공해주세요. 예: ?date=2025-05-13'}, status=400)

        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return Response({'error': '날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식을 사용하세요.'}, status=400)

        base_url = 'https://api.exchangerate.host/historical'
        currencies = ",".join([
            "AED", "AUD", "BHD", "BND", "CAD", "CHF", "CNY", "DKK", "EUR", "GBP",
            "HKD", "IDR", "JPY", "KWD", "MYR", "NOK", "NZD", "SAR", "SEK", "SGD", "THB", "USD"
        ])

        params = {
            'access_key': settings.CURRENCYLAYER_API_KEY,
            'date': date_str,
            'source': 'KRW',
            'currencies': currencies
        }

        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            return Response({'error': f'API 요청 실패 ({response.status_code})'}, status=502)

        data = response.json()
        quotes = data.get('quotes', {})
        if not quotes:
            return Response({'error': 'quotes가 비어 있습니다.', 'raw': data}, status=204)

        try:
            date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return Response({'error': f"날짜 파싱 실패: {data.get('date')}"}, status=500)

        saved = 0
        for key, rate in quotes.items():
            if not key.startswith('KRW'):
                continue
            target_currency = key[3:]
            unit_rate = round(1 / rate, 4) if rate else None
            currency_name = CURRENCY_NAME_MAP.get(target_currency, '')

            ExchangeRate.objects.update_or_create(
                date=date_obj,
                base_currency='KRW',
                target_currency=target_currency,
                defaults={
                    'rate': rate,
                    'unit_rate': unit_rate,
                    'currency_name': currency_name,
                }
            )
            saved += 1

        return Response({'message': f"{date_str} 기준 환율 저장 완료", 'saved': saved}, status=200)