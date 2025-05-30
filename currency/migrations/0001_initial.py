# Generated by Django 5.2 on 2025-05-25 11:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExchangeMemo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('foreign_currency', models.CharField(max_length=10)),
                ('foreign_amount', models.FloatField()),
                ('krw_amount', models.FloatField()),
                ('exchange_rate', models.FloatField()),
                ('date', models.DateField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ExchangeRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('base_currency', models.CharField(default='KRW', max_length=10)),
                ('target_currency', models.CharField(max_length=10)),
                ('rate', models.FloatField()),
                ('unit_rate', models.FloatField(blank=True, null=True)),
                ('currency_name', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'unique_together': {('date', 'base_currency', 'target_currency')},
            },
        ),
    ]
