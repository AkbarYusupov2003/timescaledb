# Generated by Django 4.2.7 on 2023-11-21 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statistic', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='broadcasthour',
            name='watched_duration',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='broadcasthour',
            name='watched_users_count',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contenthour',
            name='watched_duration',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contenthour',
            name='watched_users_count',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
