# Generated by Django 4.2.7 on 2023-11-27 10:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('internal', '0004_alter_category_ordering'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='allowedsubscription',
            name='sub_id',
        ),
    ]
