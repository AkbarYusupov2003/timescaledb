# Generated by Django 4.2.7 on 2023-12-06 17:37

from django.db import migrations, models
import timescale.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('statistic', '0015_devicevisit_app_type_devicevisit_country_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceVisitHour',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', timescale.db.models.fields.TimescaleDateTimeField(interval='3 month', verbose_name='Создано')),
                ('app_type', models.CharField(choices=[('app', 'app'), ('tv', 'tv'), ('web', 'web')])),
                ('device_type', models.CharField(choices=[('Smartphone', 'Smartphone'), ('Tablet', 'Tablet'), ('SmartTV', 'SmartTV'), ('Desktop', 'Desktop')])),
                ('os_type', models.CharField(choices=[('Android', 'Android'), ('iOS', 'iOS'), ('Windows', 'Windows'), ('Linux', 'Linux'), ('Tizen', 'Tizen'), ('Web0S', 'Web0S'), ('Mac OS X', 'Mac OS X'), ('Chrome OS', 'Chrome OS'), ('FreeBSD', 'FreeBSD'), ('Ubuntu', 'Ubuntu')])),
                ('country', models.CharField(max_length=32)),
            ],
            options={
                'verbose_name': 'Посещения с девайсов в час',
                'verbose_name_plural': '06. Посещения с девайсов за час',
                'db_table': 'statistic_device_visit_hour',
                'ordering': ('-time',),
            },
        ),
        migrations.CreateModel(
            name='DeviceVisitMonth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', timescale.db.models.fields.TimescaleDateTimeField(interval='3 month', verbose_name='Создано')),
                ('app_type', models.CharField(choices=[('app', 'app'), ('tv', 'tv'), ('web', 'web')])),
                ('device_type', models.CharField(choices=[('Smartphone', 'Smartphone'), ('Tablet', 'Tablet'), ('SmartTV', 'SmartTV'), ('Desktop', 'Desktop')])),
                ('os_type', models.CharField(choices=[('Android', 'Android'), ('iOS', 'iOS'), ('Windows', 'Windows'), ('Linux', 'Linux'), ('Tizen', 'Tizen'), ('Web0S', 'Web0S'), ('Mac OS X', 'Mac OS X'), ('Chrome OS', 'Chrome OS'), ('FreeBSD', 'FreeBSD'), ('Ubuntu', 'Ubuntu')])),
                ('country', models.CharField(max_length=32)),
            ],
            options={
                'verbose_name': 'Посещения с девайсов за месяц',
                'verbose_name_plural': '08. Посещения с девайсов за месяц',
                'db_table': 'statistic_device_visit_month',
                'ordering': ('-time',),
            },
        ),
        migrations.RenameModel(
            old_name='DeviceVisit',
            new_name='DeviceVisitDay',
        ),
        migrations.AlterModelOptions(
            name='devicevisitday',
            options={'ordering': ('-time',), 'verbose_name': 'Посещения с девайсов день', 'verbose_name_plural': '07. Посещения с девайсов за день'},
        ),
        migrations.AlterModelTable(
            name='devicevisitday',
            table='statistic_device_visit_day',
        ),
    ]
