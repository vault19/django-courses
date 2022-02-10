# Generated by Django 3.2.8 on 2022-02-10 20:45

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0005_faq'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='lecturers',
            field=models.ManyToManyField(blank=True, related_name='lecturers', to=settings.AUTH_USER_MODEL, verbose_name='Lecturers'),
        ),
        migrations.AddField(
            model_name='course',
            name='ribbon',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='course',
            name='tag',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='course',
            name='thumbnail',
            field=models.ImageField(blank=True, help_text='Preferred size is 600x450px (4by3).', null=True, upload_to='courses/', validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png'])]),
        ),
        migrations.AddField(
            model_name='course',
            name='video',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='subscriptionlevel',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='courses.course', verbose_name='Course'),
        ),
        migrations.AlterField(
            model_name='subscriptionlevel',
            name='run',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='courses.run', verbose_name='Run'),
        ),
    ]