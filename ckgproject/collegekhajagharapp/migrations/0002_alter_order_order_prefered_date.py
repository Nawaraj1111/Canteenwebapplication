# Generated by Django 3.2 on 2021-04-18 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collegekhajagharapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_prefered_date',
            field=models.DateTimeField(blank=True),
        ),
    ]