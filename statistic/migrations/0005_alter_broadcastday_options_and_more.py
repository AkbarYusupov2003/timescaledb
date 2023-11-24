# Generated by Django 4.2.7 on 2023-11-24 15:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statistic', '0004_alter_history_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='broadcastday',
            options={'ordering': ('-time',), 'verbose_name': 'Телеканал за день', 'verbose_name_plural': 'Телеканалы за день'},
        ),
        migrations.AlterModelOptions(
            name='broadcasthour',
            options={'ordering': ('-time',), 'verbose_name': 'Телеканал за час', 'verbose_name_plural': 'Телеканалы за час'},
        ),
        migrations.AlterModelOptions(
            name='broadcastmonth',
            options={'ordering': ('-time',), 'verbose_name': 'Телеканал за месяц', 'verbose_name_plural': 'Телеканалы за месяц'},
        ),
        migrations.AlterModelOptions(
            name='contentday',
            options={'ordering': ('-time',), 'verbose_name': 'Контент за день', 'verbose_name_plural': 'Контенты за день'},
        ),
        migrations.AlterModelOptions(
            name='contentmonth',
            options={'ordering': ('-time',), 'verbose_name': 'Контент за месяц', 'verbose_name_plural': 'Контенты за месяц'},
        ),
        migrations.AlterModelOptions(
            name='history',
            options={'ordering': ('-time',), 'verbose_name': 'История просмотра', 'verbose_name_plural': 'Истории просмотров'},
        ),
        migrations.AlterModelOptions(
            name='register',
            options={'ordering': ('-time',), 'verbose_name': 'Регистрация', 'verbose_name_plural': 'Регистрации'},
        ),
        migrations.AlterModelOptions(
            name='report',
            options={'ordering': ('-created_at',), 'verbose_name': 'Отчет', 'verbose_name_plural': 'Отчеты'},
        ),
        migrations.AlterModelOptions(
            name='subscription',
            options={'ordering': ('-time',), 'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
    ]
