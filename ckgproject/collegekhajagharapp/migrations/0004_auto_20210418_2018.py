# Generated by Django 3.2 on 2021-04-18 14:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('collegekhajagharapp', '0003_auto_20210418_1921'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='order_prefered_date',
            new_name='order_date',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='order_prefered_time',
            new_name='order_time',
        ),
    ]