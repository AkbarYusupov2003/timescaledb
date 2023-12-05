# Generated by Django 4.2.7 on 2023-12-05 11:20

from django.db import migrations, models
import timescale.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('statistic', '0004_devicevisit_alter_broadcastday_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdsView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', timescale.db.models.fields.TimescaleDateTimeField(interval='3 month', verbose_name='Создано')),
            ],
            options={
                'verbose_name': 'Просмотр рекламы',
                'verbose_name_plural': '04. Просмотры реклам',
                'db_table': 'statistic_ads_view',
                'ordering': ('-time',),
            },
        ),
    ]