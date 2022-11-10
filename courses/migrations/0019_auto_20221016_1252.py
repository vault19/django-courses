# Generated by Django 3.2.7 on 2022-10-16 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0018_course_payment_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='footer',
            field=models.TextField(blank=True, null=True, verbose_name='Footer'),
        ),
        migrations.AlterField(
            model_name='course',
            name='categories',
            field=models.ManyToManyField(blank=True, related_name='categories', to='courses.Category', verbose_name='Categories'),
        ),
    ]