# Generated by Django 5.2 on 2025-05-28 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lightning', '0004_lightning_is_active_lightning_meeting_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lightning',
            name='is_active',
            field=models.BooleanField(default=True, null=True),
        ),
    ]
