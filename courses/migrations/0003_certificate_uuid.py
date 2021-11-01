# Generated by Django 3.2.8 on 2021-10-30 04:02

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0002_auto_20211011_2145"),
    ]

    operations = [
        migrations.AddField(
            model_name="certificate",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]