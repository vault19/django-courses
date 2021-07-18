from django.conf import settings
from django.db import models


COURSE_STATE = (
    ('D', 'Draft'),
    ('O', 'Open'),
    ('P', 'Private'),
)


class Courses(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField()
    state = models.CharField(max_length=1, choices=COURSE_STATE, default='D')


class Curriculums(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField(help_text='Explain what will user learn in this lesson.')
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    length = models.IntegerField(blank=True, null=True, help_text='')


class CurriculumDetails(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True, help_text='Describe study material.')
    data = models.FileField(help_text='Upload study material (document, video, image).')
    curriculum = models.ForeignKey(Curriculums, on_delete=models.CASCADE)


class Runs(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()
    start = models.DateField()
    end = models.DateField(blank=True, null=True)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)


class Artefact(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True, help_text='Describe what you have learned.')
    data = models.FileField(blank=True, null=True, help_text='Upload proof of your work (document, video, image).')
    curriculum = models.ForeignKey(Curriculums, on_delete=models.CASCADE)
    run = models.ForeignKey(Runs, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class PeerReview(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True, help_text='Describe your opinion about the artefact.')
    artefact = models.ForeignKey(Artefact, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Certificates(models.Model):
    data = models.FileField()
    run = models.ForeignKey(Runs, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
