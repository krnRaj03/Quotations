# Generated by Django 5.0.2 on 2024-05-08 07:47

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0016_invoicemodel_invoice_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
