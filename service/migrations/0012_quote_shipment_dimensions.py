# Generated by Django 5.0.2 on 2024-03-14 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0011_quote_profit'),
    ]

    operations = [
        migrations.AddField(
            model_name='quote',
            name='shipment_dimensions',
            field=models.CharField(default=None, max_length=50),
            preserve_default=False,
        ),
    ]
