# Generated by Django 3.2.7 on 2022-11-09 15:53

import autoslug.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0021_chapter_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='runusers',
            name='price_before_discount',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250, verbose_name='Title')),
                ('slug', autoslug.fields.AutoSlugField(unique=True, verbose_name='Slug')),
                ('valid_from', models.DateField(help_text='Coupon can be used from this date.')),
                ('valid_to', models.DateField(help_text='Coupon can be used to this date.')),
                ('limit', models.IntegerField(default=0, help_text='How many times the Coupon can be used.')),
                ('discount_type', models.CharField(choices=[('F', 'Flat Discount'), ('P', 'Percentage Discount')], max_length=1, verbose_name='Discount Type')),
                ('discount', models.FloatField(blank=True, help_text='Discount rate in EUR (if FLAT) or in % (if PERCENTAGE).', null=True)),
                ('courses', models.ManyToManyField(blank=True, related_name='courses', to='courses.Course', verbose_name='Courses')),
            ],
        ),
        migrations.AddField(
            model_name='runusers',
            name='discount_coupon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='courses.coupon'),
        ),
    ]