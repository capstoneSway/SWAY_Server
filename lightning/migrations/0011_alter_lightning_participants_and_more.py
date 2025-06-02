from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('lightning', '0010_alter_lightning_host'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # `ManyToManyField`에서 `through` 옵션을 제거
        migrations.AlterField(
            model_name='lightning',
            name='participants',
            field=models.ManyToManyField(related_name='joined_lightnings', to=settings.AUTH_USER_MODEL),
        ),
        # `LightningParticipation` 모델 삭제
        migrations.DeleteModel(
            name='LightningParticipation',
        ),
    ]