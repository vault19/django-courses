# Generated by Django 3.2.8 on 2022-10-13 12:45

import autoslug.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0016_alter_runusers_metadata'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250, verbose_name='Title')),
                ('page_title', models.CharField(max_length=250, verbose_name='Page Title')),
                ('page_subtitle', models.CharField(blank=True, max_length=250, null=True, verbose_name='Page Subtitle')),
                ('slug', autoslug.fields.AutoSlugField(editable=True, populate_from='name', unique=True, verbose_name='Slug')),
                ('color', models.CharField(help_text='#HEX', max_length=250, verbose_name='Color')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.AddField(
            model_name='course',
            name='order',
            field=models.IntegerField(default=0, help_text='Order in which the course is displayed.'),
        ),
        migrations.AddField(
            model_name='course',
            name='categories',
            field=models.ManyToManyField(blank=True, null=True, related_name='categories', to='courses.Category', verbose_name='Categories'),
        ),
    ]
