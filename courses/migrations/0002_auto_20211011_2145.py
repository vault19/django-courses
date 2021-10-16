# Generated by Django 3.2.7 on 2021-10-11 19:45

import autoslug.fields
import courses.validators
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import embed_video.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("courses", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="certificate",
            options={"verbose_name": "Certificate", "verbose_name_plural": "Certificates"},
        ),
        migrations.AlterModelOptions(
            name="chapter",
            options={"verbose_name": "Chapter", "verbose_name_plural": "Chapters"},
        ),
        migrations.AlterModelOptions(
            name="course",
            options={"verbose_name": "Course", "verbose_name_plural": "Courses"},
        ),
        migrations.AlterModelOptions(
            name="lecture",
            options={"verbose_name": "Lecture", "verbose_name_plural": "Lectures"},
        ),
        migrations.AlterModelOptions(
            name="meeting",
            options={"verbose_name": "Meeting", "verbose_name_plural": "Meetings"},
        ),
        migrations.AlterModelOptions(
            name="review",
            options={"verbose_name": "Review", "verbose_name_plural": "Reviews"},
        ),
        migrations.AlterModelOptions(
            name="run",
            options={"verbose_name": "Course Run", "verbose_name_plural": "Course Runs"},
        ),
        migrations.AlterModelOptions(
            name="runusers",
            options={"verbose_name": "Run User", "verbose_name_plural": "Run Users"},
        ),
        migrations.AlterModelOptions(
            name="submission",
            options={"verbose_name": "Submission", "verbose_name_plural": "Submissions"},
        ),
        migrations.AddField(
            model_name="course",
            name="metadata",
            field=models.JSONField(blank=True, help_text="Metadata about course.", null=True, verbose_name="Metadata"),
        ),
        migrations.AddField(
            model_name="meeting",
            name="metadata",
            field=models.JSONField(blank=True, help_text="Metadata about meeting.", null=True, verbose_name="Metadata"),
        ),
        migrations.AddField(
            model_name="run",
            name="metadata",
            field=models.JSONField(blank=True, help_text="Metadata about run.", null=True, verbose_name="Metadata"),
        ),
        migrations.AlterField(
            model_name="certificate",
            name="data",
            field=models.FileField(
                upload_to="certificates",
                validators=[
                    django.core.validators.FileExtensionValidator(["pdf"]),
                    courses.validators.FileSizeValidator(2),
                ],
                verbose_name="Data",
            ),
        ),
        migrations.AlterField(
            model_name="certificate",
            name="run",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="courses.run", verbose_name="Run"),
        ),
        migrations.AlterField(
            model_name="certificate",
            name="timestamp_added",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Added"),
        ),
        migrations.AlterField(
            model_name="certificate",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name="User"
            ),
        ),
        migrations.AlterField(
            model_name="chapter",
            name="course",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="courses.course", verbose_name="Course"
            ),
        ),
        migrations.AlterField(
            model_name="chapter",
            name="description",
            field=models.TextField(
                blank=True,
                help_text="Full description of the chapter. Explain what will user learn in this lesson.",
                null=True,
                verbose_name="Description",
            ),
        ),
        migrations.AlterField(
            model_name="chapter",
            name="length",
            field=models.IntegerField(
                default=7,
                help_text="Number of days that chapter will be open. If all chapters length is set to 0 course is considered self-paced.",
                verbose_name="Length",
            ),
        ),
        migrations.AlterField(
            model_name="chapter",
            name="perex",
            field=models.TextField(
                blank=True,
                help_text="Short description of the chapter displayed in the list of all chapters.",
                null=True,
                verbose_name="Perex",
            ),
        ),
        migrations.AlterField(
            model_name="chapter",
            name="previous",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="courses.chapter",
                verbose_name="Previous chapter",
            ),
        ),
        migrations.AlterField(
            model_name="chapter",
            name="require_submission",
            field=models.CharField(
                choices=[
                    ("D", "Disabled"),
                    ("N", "Not required"),
                    ("C", "Required for next chapter"),
                    ("E", "Required to end course"),
                ],
                default="D",
                help_text="A submission can be required either for continuing to the next chapter or to finish the course.",
                max_length=1,
                verbose_name="Require submission",
            ),
        ),
        migrations.AlterField(
            model_name="chapter",
            name="require_submission_review",
            field=models.CharField(
                choices=[
                    ("D", "Disabled"),
                    ("N", "Not required"),
                    ("C", "Required for next chapter"),
                    ("E", "Required to end course"),
                ],
                default="D",
                help_text="Submission is accepted only after being accepted by a review.",
                max_length=1,
                verbose_name="Require submission review",
            ),
        ),
        migrations.AlterField(
            model_name="chapter",
            name="slug",
            field=autoslug.fields.AutoSlugField(editable=True, populate_from="title", unique=True, verbose_name="Slug"),
        ),
        migrations.AlterField(
            model_name="chapter",
            name="title",
            field=models.CharField(max_length=250, verbose_name="Title"),
        ),
        migrations.AlterField(
            model_name="course",
            name="creator",
            field=models.ForeignKey(
                help_text="Creator of the course, mainly responsible for the content",
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Creator",
            ),
        ),
        migrations.AlterField(
            model_name="course",
            name="description",
            field=models.TextField(help_text="Full description of the course.", verbose_name="Description"),
        ),
        migrations.AlterField(
            model_name="course",
            name="perex",
            field=models.TextField(
                blank=True,
                help_text="Short description of the course displayed in the list of all courses. If empty description will be used.",
                null=True,
                verbose_name="Perex",
            ),
        ),
        migrations.AlterField(
            model_name="course",
            name="slug",
            field=autoslug.fields.AutoSlugField(editable=True, populate_from="name", unique=True, verbose_name="Slug"),
        ),
        migrations.AlterField(
            model_name="course",
            name="state",
            field=models.CharField(
                choices=[("D", "Draft"), ("O", "Open"), ("C", "Closed"), ("P", "Private")],
                default="D",
                max_length=1,
                verbose_name="State",
            ),
        ),
        migrations.AlterField(
            model_name="course",
            name="title",
            field=models.CharField(max_length=250, verbose_name="Title"),
        ),
        migrations.AlterField(
            model_name="lecture",
            name="chapter",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="courses.chapter", verbose_name="Chapter"
            ),
        ),
        migrations.AlterField(
            model_name="lecture",
            name="data",
            field=models.FileField(
                blank=True,
                help_text="Upload study material (document, video, image).",
                null=True,
                upload_to="lectures",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        ["jpg", "jpeg", "gif", "png", "tiff", "svg", "pdf", "mkv", "avi", "mp4", "mov"]
                    ),
                    courses.validators.FileSizeValidator(50),
                ],
                verbose_name="Data",
            ),
        ),
        migrations.AlterField(
            model_name="lecture",
            name="description",
            field=models.TextField(
                blank=True,
                help_text="Introduce the study material, explain what data are uploaded.",
                null=True,
                verbose_name="Description",
            ),
        ),
        migrations.AlterField(
            model_name="lecture",
            name="lecture_type",
            field=models.CharField(
                choices=[
                    ("V", "Video Lesson"),
                    ("T", "Text to read"),
                    ("PF", "Peer Feedback"),
                    ("P", "Project"),
                    ("F", "Feedback"),
                    ("L", "Live lesson"),
                ],
                default="V",
                max_length=2,
                verbose_name="Lecture type",
            ),
        ),
        migrations.AlterField(
            model_name="lecture",
            name="metadata",
            field=models.JSONField(
                blank=True, help_text="Metadata about uploaded data.", null=True, verbose_name="Metadata"
            ),
        ),
        migrations.AlterField(
            model_name="lecture",
            name="require_submission",
            field=models.CharField(
                choices=[
                    ("D", "Disabled"),
                    ("N", "Not required"),
                    ("C", "Required for next chapter"),
                    ("E", "Required to end course"),
                ],
                default="N",
                help_text="A submission can be required either for continuing to the next chapter or to finish the course.",
                max_length=1,
                verbose_name="Require submission",
            ),
        ),
        migrations.AlterField(
            model_name="lecture",
            name="require_submission_review",
            field=models.CharField(
                choices=[
                    ("D", "Disabled"),
                    ("N", "Not required"),
                    ("C", "Required for next chapter"),
                    ("E", "Required to end course"),
                ],
                default="N",
                help_text="Submission is accepted only after being accepted by a review.",
                max_length=1,
                verbose_name="Require submission review",
            ),
        ),
        migrations.AlterField(
            model_name="lecture",
            name="slug",
            field=autoslug.fields.AutoSlugField(editable=True, populate_from="title", unique=True, verbose_name="Slug"),
        ),
        migrations.AlterField(
            model_name="lecture",
            name="subtitle",
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name="Subtitle"),
        ),
        migrations.AlterField(
            model_name="lecture",
            name="title",
            field=models.CharField(max_length=250, verbose_name="Title"),
        ),
        migrations.AlterField(
            model_name="lecture",
            name="video",
            field=embed_video.fields.EmbedVideoField(blank=True, null=True, verbose_name="Video"),
        ),
        migrations.AlterField(
            model_name="meeting",
            name="description",
            field=models.TextField(blank=True, null=True, verbose_name="Description"),
        ),
        migrations.AlterField(
            model_name="meeting",
            name="end",
            field=models.DateTimeField(verbose_name="End"),
        ),
        migrations.AlterField(
            model_name="meeting",
            name="leader",
            field=models.ForeignKey(
                blank=True,
                help_text="Leader of the meeting, eg. lecturer, vip...",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="leader",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Leader",
            ),
        ),
        migrations.AlterField(
            model_name="meeting",
            name="lecture",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="courses.lecture", verbose_name="Lecture"
            ),
        ),
        migrations.AlterField(
            model_name="meeting",
            name="link",
            field=models.URLField(max_length=250, verbose_name="Link"),
        ),
        migrations.AlterField(
            model_name="meeting",
            name="organizer",
            field=models.ForeignKey(
                help_text="Organizer of the meeting, responsible for the meeting.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="organizer",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Organizer",
            ),
        ),
        migrations.AlterField(
            model_name="meeting",
            name="run",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="courses.run", verbose_name="Run"),
        ),
        migrations.AlterField(
            model_name="meeting",
            name="start",
            field=models.DateTimeField(verbose_name="Start"),
        ),
        migrations.AlterField(
            model_name="review",
            name="accepted",
            field=models.BooleanField(
                help_text="Check if the submission if acceptable. If not, the reviewee will have to submit a new submission.",
                verbose_name="Accepted",
            ),
        ),
        migrations.AlterField(
            model_name="review",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name="Author"
            ),
        ),
        migrations.AlterField(
            model_name="review",
            name="description",
            field=models.TextField(
                blank=True,
                help_text="Describe your opinion about the submission.",
                null=True,
                verbose_name="Description",
            ),
        ),
        migrations.AlterField(
            model_name="review",
            name="submission",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="courses.submission", verbose_name="Submission"
            ),
        ),
        migrations.AlterField(
            model_name="review",
            name="timestamp_added",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Added"),
        ),
        migrations.AlterField(
            model_name="review",
            name="timestamp_modified",
            field=models.DateTimeField(auto_now=True, verbose_name="Modified"),
        ),
        migrations.AlterField(
            model_name="review",
            name="title",
            field=models.CharField(max_length=250, verbose_name="Title"),
        ),
        migrations.AlterField(
            model_name="run",
            name="course",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="courses.course", verbose_name="Course"
            ),
        ),
        migrations.AlterField(
            model_name="run",
            name="end",
            field=models.DateField(
                blank=True,
                help_text="Date will be calculated automatically if any of the chapter has length set.",
                null=True,
                verbose_name="End",
            ),
        ),
        migrations.AlterField(
            model_name="run",
            name="limit",
            field=models.IntegerField(
                default=0,
                help_text="Max number of attendees, after which registration for the Run will close. If set to 0 the course will have no limit.",
                verbose_name="Limit",
            ),
        ),
        migrations.AlterField(
            model_name="run",
            name="manager",
            field=models.ForeignKey(
                help_text="Manager of the course run, responsible for the smoothness of the run.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="manager",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Manager",
            ),
        ),
        migrations.AlterField(
            model_name="run",
            name="perex",
            field=models.TextField(
                blank=True,
                help_text="Short description displayed in course list, use as course perex. If empty course perex will be used.",
                null=True,
                verbose_name="Perex",
            ),
        ),
        migrations.AlterField(
            model_name="run",
            name="price",
            field=models.FloatField(
                default=0,
                help_text="Price for the course run that will have to be payed by the subscriber.",
                verbose_name="Price",
            ),
        ),
        migrations.AlterField(
            model_name="run",
            name="slug",
            field=autoslug.fields.AutoSlugField(editable=True, populate_from="title", unique=True, verbose_name="Slug"),
        ),
        migrations.AlterField(
            model_name="run",
            name="start",
            field=models.DateField(verbose_name="Start"),
        ),
        migrations.AlterField(
            model_name="run",
            name="state",
            field=models.CharField(
                choices=[("D", "Draft"), ("O", "Open"), ("C", "Closed"), ("P", "Private")],
                default="D",
                max_length=1,
                verbose_name="State",
            ),
        ),
        migrations.AlterField(
            model_name="run",
            name="title",
            field=models.CharField(max_length=250, verbose_name="Title"),
        ),
        migrations.AlterField(
            model_name="run",
            name="users",
            field=models.ManyToManyField(
                blank=True, through="courses.RunUsers", to=settings.AUTH_USER_MODEL, verbose_name="Users"
            ),
        ),
        migrations.AlterField(
            model_name="runusers",
            name="payment",
            field=models.FloatField(default=0, verbose_name="Payment"),
        ),
        migrations.AlterField(
            model_name="runusers",
            name="run",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="courses.run", verbose_name="Run"),
        ),
        migrations.AlterField(
            model_name="runusers",
            name="timestamp_added",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Added"),
        ),
        migrations.AlterField(
            model_name="runusers",
            name="timestamp_modified",
            field=models.DateTimeField(auto_now=True, verbose_name="Modified"),
        ),
        migrations.AlterField(
            model_name="runusers",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name="User"
            ),
        ),
        migrations.AlterField(
            model_name="submission",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name="Author"
            ),
        ),
        migrations.AlterField(
            model_name="submission",
            name="chapter",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="courses.chapter",
                verbose_name="Chapter",
            ),
        ),
        migrations.AlterField(
            model_name="submission",
            name="data",
            field=models.FileField(
                blank=True,
                help_text="Upload proof of your work (document, video, image).",
                null=True,
                upload_to="submissions",
                validators=[
                    django.core.validators.FileExtensionValidator(["jpg", "jpeg", "png", "pdf", "doc", "docx", "txt"]),
                    courses.validators.FileSizeValidator(2),
                ],
                verbose_name="Data",
            ),
        ),
        migrations.AlterField(
            model_name="submission",
            name="description",
            field=models.TextField(
                blank=True, help_text="Describe what you have learned.", null=True, verbose_name="Description"
            ),
        ),
        migrations.AlterField(
            model_name="submission",
            name="lecture",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="courses.lecture",
                verbose_name="Lecture",
            ),
        ),
        migrations.AlterField(
            model_name="submission",
            name="metadata",
            field=models.JSONField(
                blank=True, help_text="Metadata about submission.", null=True, verbose_name="Metadata"
            ),
        ),
        migrations.AlterField(
            model_name="submission",
            name="run",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="courses.run", verbose_name="Run"),
        ),
        migrations.AlterField(
            model_name="submission",
            name="timestamp_added",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Added"),
        ),
        migrations.AlterField(
            model_name="submission",
            name="timestamp_modified",
            field=models.DateTimeField(auto_now=True, verbose_name="Modified"),
        ),
        migrations.AlterField(
            model_name="submission",
            name="title",
            field=models.CharField(max_length=250, verbose_name="Title"),
        ),
    ]