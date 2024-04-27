# Generated by Django 5.0.2 on 2024-04-24 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0014_invoicemodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoicemodel',
            name='buyer_name',
            field=models.CharField(default=None, max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='invoicemodel',
            name='seller_name',
            field=models.CharField(default=None, max_length=200),
            preserve_default=False,
        ),
    ]
