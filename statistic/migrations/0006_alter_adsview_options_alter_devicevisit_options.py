# Generated by Django 4.2.7 on 2023-12-05 11:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statistic', '0005_adsview'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='adsview',
            options={'ordering': ('-time',), 'verbose_name': 'Просмотр рекламы', 'verbose_name_plural': '11. Просмотры реклам'},
        ),
        migrations.AlterModelOptions(
            name='devicevisit',
            options={'ordering': ('-time',), 'verbose_name': 'Посещения с девайса', 'verbose_name_plural': '04. Посещения с девайсов'},
        ),
    ]
