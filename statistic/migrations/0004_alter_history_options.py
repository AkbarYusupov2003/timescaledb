# Generated by Django 4.2.7 on 2023-11-24 15:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statistic', '0003_alter_contenthour_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='history',
            options={'ordering': ('time',), 'verbose_name': 'История просмотра', 'verbose_name_plural': 'Истории просмотров'},
        ),
    ]
