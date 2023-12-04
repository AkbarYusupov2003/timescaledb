# Generated by Django 4.2.7 on 2023-12-04 15:39

from django.db import migrations, models
import timescale.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('statistic', '0006_alter_categoryviewhour_category_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyTotalView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', timescale.db.models.fields.TimescaleDateTimeField(interval='3 month', verbose_name='Создано')),
                ('category_id', models.PositiveSmallIntegerField(verbose_name='ID Категории')),
                ('age_group', models.CharField(choices=[('0', '0-6'), ('1', '7-12'), ('2', '13-15'), ('3', '16-18'), ('4', '19-21'), ('5', '22-28'), ('6', '29-36'), ('7', '37-46'), ('8', '47-54'), ('9', '55+')], verbose_name='Возрастная группа')),
                ('gender', models.CharField(choices=[('M', 'Мужчина'), ('W', 'Женщина')], verbose_name='Пол')),
                ('total_views', models.PositiveIntegerField(default=0, verbose_name='Количество просмотров')),
            ],
            options={
                'verbose_name': 'Общий просмотр за день',
                'verbose_name_plural': '13. Общие просмотры за день',
                'ordering': ('-time',),
            },
        ),
        migrations.AlterField(
            model_name='history',
            name='time',
            field=timescale.db.models.fields.TimescaleDateTimeField(interval='1 month', verbose_name='Создано'),
        ),
    ]
