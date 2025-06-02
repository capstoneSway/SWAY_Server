from django_cron import CronJobBase, Schedule
from .models import Lightning
from django.utils import timezone

class UpdateLightningStatusCronJob(CronJobBase):
    RUN_EVERY_MINS = 5  # 5분마다 실행

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'lightning.update_lightning_event_status'  # 고유 코드

    def do(self):
        now = timezone.now()
        updated = Lightning.objects.filter(end_time__lt=now, status='inProgress')\
                                        .update(status='done')
        print(f"[Cron] Lightning {updated}개 상태 업데이트 완료 at {now}")