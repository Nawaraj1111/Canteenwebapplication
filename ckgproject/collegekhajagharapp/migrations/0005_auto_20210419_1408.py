# Generated by Django 3.2 on 2021-04-19 08:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collegekhajagharapp', '0004_auto_20210418_2018'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='order_date',
        ),
        migrations.RemoveField(
            model_name='order',
            name='order_time',
        ),
    ]