# Generated by Django 3.2.8 on 2022-01-10 18:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_certificate_uuid'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField(verbose_name='Price')),
                ('title', models.CharField(max_length=250, verbose_name='Title')),
                ('description', models.TextField(blank=True, help_text='Full description of the subscription level.', null=True, verbose_name='Description')),
                ('metadata', models.JSONField(blank=True, help_text='Metadata about uploaded data.', null=True, verbose_name='Metadata')),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.run', verbose_name='Run')),
            ],
            options={
                'verbose_name': 'Subscription Level',
                'verbose_name_plural': 'Subscription Levels',
            },
        ),
        migrations.AddField(
            model_name='runusers',
            name='subscription_level',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='courses.subscriptionlevel', verbose_name='User'),
        ),
    ]
