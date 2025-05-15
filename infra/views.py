from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET

# Create your views here.
@require_GET
def health_check(request):
    return JsonResponse({'status': 'ok'}, status=200)