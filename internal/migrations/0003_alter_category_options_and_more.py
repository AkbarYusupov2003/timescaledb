# Generated by Django 4.2.7 on 2023-11-27 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internal', '0002_alter_allowedperiod_name_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ('ordering',), 'verbose_name': 'Категория', 'verbose_name_plural': 'Категории'},
        ),
        migrations.RenameField(
            model_name='category',
            old_name='title_en',
            new_name='name_en',
        ),
        migrations.RenameField(
            model_name='category',
            old_name='title_ru',
            new_name='name_ru',
        ),
        migrations.RenameField(
            model_name='category',
            old_name='title_uz',
            new_name='name_uz',
        ),
        migrations.AddField(
            model_name='category',
            name='ordering',
            field=models.PositiveIntegerField(blank=True, default=1),
            preserve_default=False,
        ),
    ]
