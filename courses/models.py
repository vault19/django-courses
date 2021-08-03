from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from autoslug import AutoSlugField

COURSE_STATE = (
    ('D', _('Draft')),
    ('O', _('Open')),
    ('C', _('Closed')),
    ('P', _('Private')),
)


class Course(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField()
    state = models.CharField(max_length=1, choices=COURSE_STATE, default='D')

    def __str__(self):
        return f"{self.name}"

    @property
    def length(self):
        length = 0

        for chapter in self.chapter_set.all():
            length += chapter.length

        return length

    def self_paced(self):
        return self.length == 0


class Chapter(models.Model):
    title = models.CharField(max_length=250)
    slug = AutoSlugField(populate_from='title', unique=True)
    description = models.TextField(help_text=_('Explain what will user learn in this lesson.'))
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    length = models.IntegerField(default=7, help_text=_('Number of days that chapter will be open. If all chapters '
                                                        'length is set to 0 course is considered self-paced.'))
    require_submission = models.BooleanField(help_text=_('Next chapter wont be unlocked until submission is provided.'))

    def __str__(self):
        return f"{self.course}: {self.title}"


class Lecture(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True, help_text=_('Introduce the study material, explain what data '
                                                                      'are uploaded.'))
    data = models.FileField(help_text=_('Upload study material (document, video, image).'))
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title}"


class Run(models.Model):
    title = models.CharField(max_length=250)
    slug = AutoSlugField(populate_from='title', unique=True)
    description = models.TextField(blank=True, null=True)
    start = models.DateField()
    end = models.DateField(blank=True, null=True, help_text=_("Date will be calculated automatically if any of the "
                                                              "chapter has length set."))
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title}"

    @property
    def length(self):
        return self.course.length

    def self_paced(self):
        return self.course.self_paced()

    def save(self, *args, **kwargs):
        if self.length != 0:
            self.end = self.start + timedelta(days=self.length)

        super().save(*args, **kwargs)


class Submission(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True, help_text=_('Describe what you have learned.'))
    data = models.FileField(blank=True, null=True, help_text=_('Upload proof of your work (document, video, image).'))
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, blank=True, null=True)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, blank=True, null=True)
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.chapter}: {self.title}"


class Review(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True, help_text=_('Describe your opinion about the artefact.'))
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("submission", "author",)

    def __str__(self):
        return f"{self.title}"

    def clean(self):
        if self.author == self.submission.author:
            raise ValidationError({'author': _('You can not review your own artefact!')})


class Certificate(models.Model):
    data = models.FileField()
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("run", "user",)

    def __str__(self):
        return f"Certificate: {self.run} - {self.user}"
