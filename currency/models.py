from django.db import models
from accounts.models import User

# Create your models here.
class ExchangeRate(models.Model):
    cur_unit = models.CharField(max_length=10)  # 통화코드
    cur_nm = models.CharField(max_length=50)    # 통화명
    ttb = models.CharField(max_length=20)       # 전신환(송금 받으실 때)
    tts = models.CharField(max_length=20)       # 전신환(송금 보내실 때)
    deal_bas_r = models.CharField(max_length=20) # 매매 기준율
    bkpr = models.CharField(max_length=20)      # 장부가격
    y_efee_r = models.CharField(max_length=20)  # 년환가료율
    ten_d_efee_r = models.CharField(max_length=20)  # 10일환가료율
    kftc_deal_bas_r = models.CharField(max_length=20)  # 서울외국환중개 기준율
    kftc_bkpr = models.CharField(max_length=20)        # 서울외국환중개 장부가격
    date = models.DateField()   # 저장 날짜

    class Meta:
        unique_together = ['cur_unit', 'date']

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