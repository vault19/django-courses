from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

COURSE_STATE = (
    ('D', _('Draft')),
    ('O', _('Open')),
    ('P', _('Private')),
)


class Courses(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField()
    state = models.CharField(max_length=1, choices=COURSE_STATE, default='D')

    def __str__(self):
        return f"{self.name}"


class Curriculums(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField(help_text=_('Explain what will user learn in this lesson.'))
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    length = models.IntegerField(blank=True, null=True, help_text='')

    def __str__(self):
        return f"{self.title}"


class CurriculumDetails(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True, help_text=_('Describe study material.'))
    data = models.FileField(help_text=_('Upload study material (document, video, image).'))
    curriculum = models.ForeignKey(Curriculums, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title}"


class Runs(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()
    start = models.DateField()
    end = models.DateField(blank=True, null=True)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title}"


class Artefact(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True, help_text=_('Describe what you have learned.'))
    data = models.FileField(blank=True, null=True, help_text=_('Upload proof of your work (document, video, image).'))
    curriculum = models.ForeignKey(Curriculums, on_delete=models.CASCADE)
    run = models.ForeignKey(Runs, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title}"


class PeerReview(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True, help_text=_('Describe your opinion about the artefact.'))
    artefact = models.ForeignKey(Artefact, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("artefact", "author",)

    def __str__(self):
        return f"{self.title}"


class Certificates(models.Model):
    data = models.FileField()
    run = models.ForeignKey(Runs, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("run", "user",)

    def __str__(self):
        return f"Certificate: {self.run} - {self.user}"
