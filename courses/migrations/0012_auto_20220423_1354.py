# Generated by Django 3.2.8 on 2022-04-23 11:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0011_auto_20220422_2317'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailtemplate',
            name='mail_body_plaintext',
        ),
        migrations.AddField(
            model_name='chapter',
            name='mail_chapter_open',
            field=models.ForeignKey(blank=True, help_text='Sent when the Chapter opens.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='courses.emailtemplate'),
        ),
        migrations.AddField(
            model_name='course',
            name='mail_certificate_generation',
            field=models.ForeignKey(blank=True, help_text='Sent after Certificate generation.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mail_certificate_generation', to='courses.emailtemplate'),
        ),
        migrations.AddField(
            model_name='course',
            name='mail_meeting_starts',
            field=models.ForeignKey(blank=True, help_text='Sent right before Meeting starts.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mail_meeting_starts', to='courses.emailtemplate'),
        ),
        migrations.AddField(
            model_name='course',
            name='mail_run_started',
            field=models.ForeignKey(blank=True, help_text='Sent right before Run starts.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mail_run_started', to='courses.emailtemplate'),
        ),
    ]