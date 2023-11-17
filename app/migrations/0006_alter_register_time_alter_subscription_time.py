# Generated by Django 4.2.7 on 2023-11-17 05:51

from django.db import migrations
import timescale.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_alter_register_time_alter_subscription_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='register',
            name='time',
            field=timescale.db.models.fields.TimescaleDateTimeField(interval='0'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='time',
            field=timescale.db.models.fields.TimescaleDateTimeField(interval='0'),
        ),
    ]
