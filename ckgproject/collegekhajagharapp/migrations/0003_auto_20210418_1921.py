# Generated by Django 3.2 on 2021-04-18 13:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('collegekhajagharapp', '0002_alter_order_order_prefered_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_prefered_time',
            field=models.TimeField(blank=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='order_prefered_date',
            field=models.DateField(),
        ),
    ]
