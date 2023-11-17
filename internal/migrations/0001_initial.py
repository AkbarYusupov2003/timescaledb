# Generated by Django 4.2.7 on 2023-11-17 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AllowedPeriod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
            ],
            options={
                'verbose_name': 'Разрешенный период',
                'verbose_name_plural': 'Разрешенные периоды',
            },
        ),
        migrations.CreateModel(
            name='AllowedSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sub_id', models.CharField(max_length=8)),
                ('description', models.CharField(max_length=512)),
            ],
            options={
                'verbose_name': 'Разрешенная подписка',
                'verbose_name_plural': 'Разрешенные подписки',
            },
        ),
    ]
