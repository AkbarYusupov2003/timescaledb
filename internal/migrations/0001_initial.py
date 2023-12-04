# Generated by Django 4.2.7 on 2023-12-02 17:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AllowedSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title_ru', models.CharField(max_length=128, verbose_name='Название')),
                ('title_en', models.CharField(blank=True, max_length=128, verbose_name='Название на английском')),
                ('title_uz', models.CharField(blank=True, max_length=128, verbose_name='Название на узбекском')),
            ],
            options={
                'verbose_name': 'Разрешенная подписка',
                'verbose_name_plural': 'Разрешенные подписки',
            },
        ),
        migrations.CreateModel(
            name='BroadcastCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_ru', models.CharField(max_length=255, verbose_name='Название на русском')),
                ('name_en', models.CharField(blank=True, max_length=255, verbose_name='Название на английском')),
                ('name_uz', models.CharField(blank=True, max_length=255, verbose_name='Название на узбекском')),
            ],
            options={
                'verbose_name': 'Категория телеканалов',
                'verbose_name_plural': 'Категории телеканалов',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_ru', models.CharField(max_length=255, verbose_name='Название на русском')),
                ('name_en', models.CharField(blank=True, max_length=255, verbose_name='Название на английском')),
                ('name_uz', models.CharField(blank=True, max_length=255, verbose_name='Название на узбекском')),
                ('ordering', models.PositiveIntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
                'ordering': ('ordering',),
            },
        ),
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('is_chosen', models.BooleanField(default=False, verbose_name='Выбран')),
            ],
            options={
                'verbose_name': 'Спонсор',
                'verbose_name_plural': 'Спонсоры',
            },
        ),
        migrations.CreateModel(
            name='Broadcast',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('broadcast_id', models.PositiveBigIntegerField(unique=True, verbose_name='ID Телеканала')),
                ('title', models.CharField(blank=True, max_length=255, null=True, verbose_name='Название')),
                ('quality', models.CharField(blank=True, choices=[('sd', 'SD'), ('hd', 'HD'), ('fhd', 'FULL HD')], null=True, verbose_name='Качество')),
                ('allowed_subscriptions', models.ManyToManyField(blank=True, to='internal.allowedsubscription', verbose_name='Разрешенные подписки')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='internal.broadcastcategory', verbose_name='Категории')),
            ],
            options={
                'verbose_name': 'Телеканал',
                'verbose_name_plural': 'Телеканалы',
                'ordering': ('-broadcast_id',),
            },
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title_ru', models.CharField(max_length=255, verbose_name='Название на русском')),
                ('title_en', models.CharField(blank=True, max_length=255, verbose_name='Название на английском')),
                ('title_uz', models.CharField(blank=True, max_length=255, verbose_name='Название на узбекском')),
                ('content_id', models.PositiveIntegerField(verbose_name='ID Контента')),
                ('episode_id', models.PositiveIntegerField(blank=True, null=True, verbose_name='ID Эпизода')),
                ('is_russian', models.BooleanField(default=True, verbose_name='На русском')),
                ('duration', models.PositiveIntegerField(blank=True, null=True, verbose_name='Длительность')),
                ('slug', models.SlugField(unique=True)),
                ('year', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Год')),
                ('allowed_subscriptions', models.ManyToManyField(blank=True, to='internal.allowedsubscription', verbose_name='Разрешенные подписки')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='internal.category', verbose_name='Категории')),
                ('sponsors', models.ManyToManyField(blank=True, to='internal.sponsor', verbose_name='Спонсоры')),
            ],
            options={
                'verbose_name': 'Контент',
                'verbose_name_plural': 'Контенты',
                'unique_together': {('content_id', 'episode_id')},
            },
        ),
    ]
