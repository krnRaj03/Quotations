# Generated by Django 5.0.2 on 2024-02-29 11:27

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0006_remove_product_product_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quote',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
