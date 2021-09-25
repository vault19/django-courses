from datetime import datetime, date, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from autoslug import AutoSlugField
from embed_video.fields import EmbedVideoField

from courses.validators import FileSizeValidator
from courses.settings import (
    COURSES_ALLOW_ACCESS_TO_PASSED_CHAPTERS,
    EXTENSION_VIDEO,
    EXTENSION_IMAGE,
    EXTENSION_DOCUMENT,
    MAX_FILE_SIZE_UPLOAD,
    MAX_FILE_SIZE_UPLOAD_FRONTEND,
)


STATE = (
    ("D", _("Draft")),
    ("O", _("Open")),
    ("C", _("Closed")),
    ("P", _("Private")),
)

LECTURE_TYPE = (
    ("V", _("Video Lesson")),
    ("T", _("Text to read")),
    ("PF", _("Peer Feedback")),
    ("P", _("Project")),
    ("F", _("Feedback")),
    ("L", _("Live lesson")),
)

SUBMISSION_TYPE = (
    ("D", _("Disabled")),
    ("N", _("Not required")),
    ("C", _("Required for next chapter")),
    ("E", _("Required to end course")),
)


class Course(models.Model):
    title = models.CharField(max_length=250)
    perex = models.TextField(
        blank=True,
        null=True,
        help_text=_(
            "Short description of the course displayed in the list"
            " of all courses. If empty description will be used."
        ),
    )
    slug = AutoSlugField(populate_from="name", editable=True, unique=True)
    description = models.TextField(help_text=_("Full description of the course."))
    state = models.CharField(max_length=1, choices=STATE, default="D")
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text=_("Creaator of the course, mainly responsible for the content"),
    )

    def __str__(self):
        return f"{self.title}"

    def has_active_runs(self):
        return self.get_active_runs().count() > 0

    def get_active_runs(self):
        if self.state == "O":
            return self.run_set.filter(Q(end__gte=datetime.today()) | Q(end=None)).order_by("-start")
        else:
            return self.objects.none()

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
    previous = models.ForeignKey("self", blank=True, null=True, on_delete=models.SET_NULL)
    slug = AutoSlugField(populate_from="title", editable=True, unique=True)
    perex = models.TextField(
        blank=True, null=True, help_text=_("Short description of the chapter displayed in the list" " of all chapters.")
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text=_("Full description of the chapter. Explain what " "will user learn in this lesson."),
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    length = models.IntegerField(
        default=7,
        help_text=_(
            "Number of days that chapter will be open. If all chapters "
            "length is set to 0 course is considered self-paced."
        ),
    )
    require_submission = models.CharField(
        max_length=1,
        choices=SUBMISSION_TYPE,
        default="D",
        help_text=_("A submission can be required either for continuing to the next chapter or to finish the course."),
    )
    require_submission_review = models.CharField(
        max_length=1,
        choices=SUBMISSION_TYPE,
        default="D",
        help_text=_("Submission is accepted only after being accepted by a review."),
    )

    def __str__(self):
        return f"{self.title}"

    @property
    def lecture_types(self):
        lecture_types = set()

        for lecture in self.lecture_set.all():
            lecture_types.update(lecture.lecture_type)

        return lecture_types

    @staticmethod
    def verify_course_dates(start, end):
        if date.today() > end:
            if not COURSES_ALLOW_ACCESS_TO_PASSED_CHAPTERS:
                raise PermissionDenied(
                    _("Chapter has already ended...") + " " + _("Sorry it is not available any more.")
                )

        if date.today() < start:
            raise PermissionDenied(_("Chapter hasnt started yet...") + " " + _("Please come back later."))

    def get_run_dates(self, run, raise_wrong_dates=False):
        total_days = 0
        previous_chapter = self.previous

        while previous_chapter is not None:
            total_days += previous_chapter.length
            previous_chapter = previous_chapter.previous

        start = run.start + timedelta(days=total_days)
        end = run.start + timedelta(days=total_days + self.length - 1)

        if raise_wrong_dates:
            self.verify_course_dates(start, end)

        return start, end

    def clean(self):
        if self.previous and self.previous.course != self.course:
            raise ValidationError({"previous": _("You can not link to chapter in different course!")})


class Lecture(models.Model):
    title = models.CharField(max_length=250)
    slug = AutoSlugField(populate_from="title", editable=True, unique=True)
    subtitle = models.CharField(blank=True, null=True, max_length=250)
    description = models.TextField(
        blank=True, null=True, help_text=_("Introduce the study material, explain what data " "are uploaded.")
    )
    data = models.FileField(
        blank=True,
        null=True,
        upload_to="lectures",
        help_text=_("Upload study material (document, " "video, image)."),
        validators=[
            FileExtensionValidator(["jpg", "jpeg", "gif", "png", "tiff", "svg", "pdf", "mkv", "avi", "mp4", "mov"]),
            FileSizeValidator(MAX_FILE_SIZE_UPLOAD),
        ],
    )
    metadata = models.JSONField(blank=True, null=True, help_text=_("Metadata about uploaded data."))
    video = EmbedVideoField(blank=True, null=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    lecture_type = models.CharField(max_length=2, choices=LECTURE_TYPE, default="V")

    require_submission = models.CharField(
        max_length=1,
        choices=SUBMISSION_TYPE,
        default="N",
        help_text=_("A submission can be required either for continuing to the next chapter or to finish the course."),
    )
    require_submission_review = models.CharField(
        max_length=1,
        choices=SUBMISSION_TYPE,
        default="N",
        help_text=_("Submission is accepted only after being accepted by a review."),
    )
    order = models.IntegerField(default=0, help_text=_("Order number for the lecture in the chapter."))

    def __str__(self):
        return f"{self.chapter.title}: {self.title}"

    @staticmethod
    def check_file_extension(data, alloed_extensions):
        extension = data.name.split(".")[1:]

        if len(extension) == 1 and extension[0].lower() in alloed_extensions:
            return True
        return False

    def clean(self):
        if self.data:
            if self.lecture_type == LECTURE_TYPE[0][0] and not self.check_file_extension(self.data, EXTENSION_VIDEO):
                raise ValidationError(
                    {
                        "data": _(
                            'Lecture type is "%s" but you are not uploading such file. Allowed '
                            "extensions: %s" % (LECTURE_TYPE[0][1], EXTENSION_VIDEO)
                        )
                    }
                )

            if self.lecture_type == LECTURE_TYPE[1][0] and not self.check_file_extension(
                self.data, EXTENSION_IMAGE + EXTENSION_DOCUMENT
            ):
                raise ValidationError(
                    {
                        "data": _(
                            'Lecture type is "%s" but you are not uploading such file. Allowed '
                            "extensions: %s" % (LECTURE_TYPE[1][1], EXTENSION_IMAGE + EXTENSION_DOCUMENT)
                        )
                    }
                )


class Run(models.Model):
    title = models.CharField(max_length=250)
    slug = AutoSlugField(populate_from="title", editable=True, unique=True)
    perex = models.TextField(
        blank=True,
        null=True,
        help_text=_(
            "Short description displayed in course list, use as course perex. If empty " "course perex will be used."
        ),
    )
    start = models.DateField()
    end = models.DateField(
        blank=True,
        null=True,
        help_text=_("Date will be calculated automatically if any of the " "chapter has length set."),
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    state = models.CharField(max_length=1, choices=STATE, default="D")
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through="RunUsers", blank=True)
    price = models.FloatField(
        default=0, help_text=_("Price for the course run that will have to be payed by the " "subscriber.")
    )
    limit = models.IntegerField(
        default=0,
        help_text=_(
            "Max number of attendees, after which registration for the Run "
            "will close. If set to 0 the course will have no limit."
        ),
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="manager",
        help_text=_("Manager of the course run, responsible for the smoothness of the run."),
    )

    def __str__(self):
        return f"{self.course}: {self.title}"

    @property
    def length(self):
        return self.course.length

    @property
    def is_past_due(self):
        return date.today() > self.end

    @property
    def is_full(self):
        if self.limit != 0 and self.limit <= self.users.count():
            return True
        return False

    @property
    def self_paced(self):
        return self.course.self_paced()

    def is_subscribed(self, user, raise_unsubscribed=False):
        if user.id is None:
            # AnonymousUser, a.k.a. not logged in...
            subscriptions = 0
        else:
            subscriptions = self.users.filter(runusers__user=user).count()

        if subscriptions > 0:
            return True
        elif raise_unsubscribed:
            raise PermissionDenied(_("You are not subscribed to this course!"))
        else:
            return False

    def is_subscribed_in_different_active_run(self, user):
        for run in (
            self.course.run_set.filter(Q(end__gte=datetime.today()) | Q(end=None))
            .filter(~Q(id=self.id))
            .order_by("-start")
        ):
            for other_run_user in run.users.all():
                if other_run_user == user:
                    return True
        return False

    def save(self, *args, **kwargs):
        if self.length != 0:
            self.end = self.start + timedelta(days=self.length - 1)

        super().save(*args, **kwargs)


class RunUsers(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment = models.FloatField(default=0)
    timestamp_added = models.DateTimeField(auto_now_add=True)
    timestamp_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.run}_{self.user}: {self.timestamp_added} {self.payment}"

    def clean(self):
        pass
        # Causes error in admin, when limit is one and we want to subscribe one user...
        # if self.run.is_full:
        #     raise ValidationError({"user": _("Subscribed user's limit has been reached.")})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Meeting(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    start = models.DateTimeField()
    end = models.DateTimeField()
    link = models.URLField(max_length=250)
    description = models.TextField(blank=True, null=True)
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leader",
        blank=True,
        null=True,
        help_text=_("Leader of the meeting, eg. lecturer, vip..."),
    )
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organizer",
        help_text=_("Organizer of the meeting, responsible for the meeting."),
    )

    def __str__(self):
        return f"Meeting: {self.run} {self.lecture}: {self.start} {self.end}"

    def clean(self):
        if self.start > self.end:
            raise ValidationError({"end": _("Meeting can not finish before it has started.")})

        # if self.run.start and self.start.date() < self.run.start:
        #     raise ValidationError({'start': _('Meeting is scheduled before the course run starts.')})
        #
        # if self.run.end and self.start.date() > self.run.end:
        #     raise ValidationError({'start': _('Meeting is scheduled after the course run is already finished.')})
        #
        # if self.run.end and self.end.date() > self.run.end:
        #     raise ValidationError({'end': _('Meeting can not end after the course run is already finished.')})

        if self.run.end and self.run.end < date.today():
            raise ValidationError(_("You are not allowed to add meeting to run that has already finished."))

        if self.run not in self.lecture.chapter.course.get_active_runs():
            raise ValidationError({"lecture": _("Lecture does not belong to this course (and its chapters).")})

        start, end = self.lecture.chapter.get_run_dates(self.run)

        if self.start.date() < start:
            raise ValidationError({"start": _(f"Meeting is scheduled before the lecture's chapter starts: {start}.")})

        if self.start.date() > end:
            raise ValidationError(
                {"start": _(f"Meeting is scheduled after the lecture's chapter is already finished: {end}.")}
            )

        if self.end.date() > end:
            raise ValidationError(
                {"end": _(f"Meeting can not end after the lecture's chapter is already finished: {end}.")}
            )


# class Subscription(models.Model):
#     models.ForeignKey(Lecture, on_delete=models.CASCADE, null=True, blank=True)


class Submission(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True, help_text=_("Describe what you have learned."))
    data = models.FileField(
        blank=True,
        null=True,
        upload_to="submissions",
        help_text=_("Upload proof of your work " "(document, video, image)."),
        validators=[
            FileExtensionValidator(["jpg", "jpeg", "png", "pdf", "doc", "docx", "txt"]),
            FileSizeValidator(MAX_FILE_SIZE_UPLOAD_FRONTEND),
        ],
    )
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, null=True, blank=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, null=True, blank=True)
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    metadata = models.JSONField(blank=True, null=True, help_text=_("Metadata about submission."))
    timestamp_added = models.DateTimeField(auto_now_add=True)
    timestamp_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.lecture}: {self.title}"

    def clean(self):
        if self.chapter:

            if self.chapter not in self.run.course.chapter_set.all():
                raise ValidationError({"chapter": _("Selected chapter does not belong to submission's course.")})

            if self.lecture and self.lecture not in self.chapter.lecture_set.all():
                raise ValidationError({"lecture": _("Selected lecture does not belong to selected chapter.")})

        elif self.lecture:
            selected = False

            for chapter in self.run.course.chapter_set.all():
                if self.lecture in chapter.lecture_set.all():
                    selected = True

            if not selected:
                raise ValidationError({"lecture": _("Selected lecture does not belong to submission's course.")})


class Review(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True, help_text=_("Describe your opinion about the submission."))
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    accepted = models.BooleanField(
        help_text=_("Check if the submission if acceptable. If not, the reviewee will have to submit a new submission.")
    )
    timestamp_added = models.DateTimeField(auto_now_add=True)
    timestamp_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            "submission",
            "author",
        )

    def __str__(self):
        return f"{self.title}"

    def clean(self):
        if self.author == self.submission.author:
            raise ValidationError({"author": _("You can not review your own submission!")})


class Certificate(models.Model):
    data = models.FileField(
        upload_to="certificates",
        validators=[FileExtensionValidator(["pdf"]), FileSizeValidator(MAX_FILE_SIZE_UPLOAD_FRONTEND)],
    )
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "run",
            "user",
        )

    def __str__(self):
        return f"Certificate: {self.run} - {self.user}"
