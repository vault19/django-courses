# Generated by Django 3.2.8 on 2022-04-22 21:17

import courses.validators
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0010_auto_20220422_2214'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='This title is for management purposes only, it will not be seen by the users.', max_length=250, verbose_name='Title')),
                ('mail_subject', models.TextField(help_text='Email will be sent with this subject.', verbose_name='Email subject')),
                ('mail_body_plaintext', models.TextField(help_text='Plaintext version of email body.', verbose_name='Email plaintext')),
                ('mail_body_html', models.TextField(help_text='HTML content of email body.', verbose_name='Email html')),
                ('json', models.TextField(blank=True, help_text='JSON source of the email used by Unlayer Editor. Can be blank.', null=True, verbose_name='Source JSON')),
                ('timestamp_added', models.DateTimeField(auto_now_add=True, verbose_name='Added')),
                ('timestamp_modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('creator', models.ForeignKey(blank=True, help_text='Creator of the email template.', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
            ],
        ),
        migrations.CreateModel(
            name='EmailTemplateImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, help_text='The title of the image', max_length=250, null=True, verbose_name='Title')),
                ('data', models.FileField(upload_to='email_template_images', validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'gif', 'png', 'tiff', 'svg']), courses.validators.FileSizeValidator(50)], verbose_name='Data')),
                ('timestamp_added', models.DateTimeField(auto_now_add=True, verbose_name='Added')),
                ('timestamp_modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('creator', models.ForeignKey(help_text='Uploader of the image.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
                ('email_template', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='courses.emailtemplate', verbose_name='Email template')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='mail_subscription',
            field=models.ForeignKey(blank=True, help_text='Sent after subscription.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='courses.emailtemplate'),
        ),
    ]
