# Generated by Django 4.2.7 on 2023-11-22 11:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statistic', '0005_alter_broadcasthour_watched_duration_and_more'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='broadcasthour',
            table='statistic_broadcast_hour',
        ),
        migrations.AlterModelTable(
            name='contenthour',
            table='statistic_content_hour',
        ),
        migrations.AlterModelTable(
            name='history',
            table='statistic_history',
        ),
        migrations.AlterModelTable(
            name='register',
            table='statistic_register',
        ),
        migrations.AlterModelTable(
            name='subscription',
            table='statistic_subscription',
        ),
    ]
