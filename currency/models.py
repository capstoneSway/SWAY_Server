from django.db import models
from accounts.models import User

class ExchangeRate(models.Model):
    date = models.DateField()
    base_currency = models.CharField(max_length=10, default='KRW')
    target_currency = models.CharField(max_length=10)
    rate = models.FloatField()  # 1 KRW → target_currency
    unit_rate = models.FloatField(null=True, blank=True)  # 1 target_currency → KRW
    currency_name = models.CharField(max_length=50, null=True, blank=True)  # 예: 미국 달러

    class Meta:
        unique_together = ('date', 'base_currency', 'target_currency')

    def __str__(self):
        return f"{self.date} | {self.base_currency} → {self.target_currency} ({self.currency_name}) = {self.rate}"

class ExchangeMemo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    foreign_currency = models.CharField(max_length=10)
    foreign_amount = models.FloatField()
    krw_amount = models.FloatField()
    exchange_rate = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.foreign_currency} - {self.content}"