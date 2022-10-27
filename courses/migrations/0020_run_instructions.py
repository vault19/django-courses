# Generated by Django 3.2.7 on 2022-10-27 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0019_auto_20221016_1252'),
    ]

    operations = [
        migrations.AddField(
            model_name='run',
            name='instructions',
            field=models.TextField(blank=True, help_text='Instructions displayed in course overview (visible only to registered users).', null=True, verbose_name='Instructions'),
        ),
    ]
