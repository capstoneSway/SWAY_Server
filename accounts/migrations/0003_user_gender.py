# Generated by Django 5.2 on 2025-05-16 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_nationality_alter_user_nickname'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
