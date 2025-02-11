# Generated by Django 4.2.7 on 2024-11-13 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nippo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Koban',
            fields=[
                ('name', models.TextField(primary_key=True, serialize=False)),
                ('koban1', models.TextField(blank=True, null=True)),
                ('koban2', models.TextField(blank=True, null=True)),
                ('koban3', models.TextField(blank=True, null=True)),
                ('koban4', models.TextField(blank=True, null=True)),
                ('koban5', models.TextField(blank=True, null=True)),
                ('koban6', models.TextField(blank=True, null=True)),
                ('koban7', models.TextField(blank=True, null=True)),
                ('koban8', models.TextField(blank=True, null=True)),
                ('koban9', models.TextField(blank=True, null=True)),
                ('koban10', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'koban',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='nippo',
            fields=[
                ('idx', models.AutoField(primary_key=True, serialize=False)),
                ('userid', models.TextField(blank=True, null=True)),
                ('date', models.TextField(blank=True, null=True)),
                ('start', models.TextField(blank=True, null=True)),
                ('end', models.TextField(blank=True, null=True)),
                ('zangyo', models.TextField(blank=True, null=True)),
                ('total_time', models.TextField(blank=True, null=True)),
                ('total_break', models.TextField(blank=True, null=True)),
                ('koban', models.TextField(blank=True, null=True)),
                ('add_time', models.DateTimeField(auto_now_add=True, verbose_name='add_time')),
                ('status', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'nippo',
                'managed': False,
            },
        ),
        migrations.DeleteModel(
            name='NippoModel',
        ),
    ]
