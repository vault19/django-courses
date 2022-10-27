import uuid

from datetime import datetime, date, timedelta
from time import gmtime
from time import strftime

from django.conf import settings
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from autoslug import AutoSlugField
from embed_video.fields import EmbedVideoField

from courses.validators import FileSizeValidator
from courses import settings as course_settings

from invoices.models import PaymentProfile

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


class CourseManager(models.Manager):
    """
    Manager at pre-select all related items for each query set.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related("creator").prefetch_related("run_set", "chapter_set")


class Category(models.Model):
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    title = models.CharField(verbose_name=_("Title"), max_length=250)
    page_title = models.CharField(verbose_name=_("Page Title"), max_length=250)
    page_subtitle = models.CharField(verbose_name=_("Page Subtitle"), max_length=250, blank=True, null=True)
    slug = AutoSlugField(verbose_name=_("Slug"), populate_from="name", editable=True, unique=True)
    color = models.CharField(verbose_name=_("Color"), help_text=_("#HEX"), max_length=250)
    footer = models.TextField(verbose_name=_("Footer"), blank=True, null=True)

    def __str__(self):
        return f"{self.title}"


class Course(models.Model):
    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")

    objects = CourseManager()
    objects_no_relations = models.Manager()

    title = models.CharField(verbose_name=_("Title"), max_length=250)
    perex = models.TextField(
        verbose_name=_("Perex"),
        blank=True,
        null=True,
        help_text=_(
            "Short description of the course displayed in the list of all courses. If empty description will be used."
        ),
    )
    order = models.IntegerField(default=0, help_text=_("Order in which the course is displayed."))
    categories = models.ManyToManyField(
        "Category",
        verbose_name=_("Categories"),
        blank=True,
        related_name='categories',
    )
    slug = AutoSlugField(verbose_name=_("Slug"), populate_from="name", editable=True, unique=True)
    description = models.TextField(verbose_name=_("Description"), help_text=_("Full description of the course."))
    state = models.CharField(verbose_name=_("State"), max_length=1, choices=STATE, default="D")
    metadata = models.JSONField(
        verbose_name=_("Metadata"), blank=True, null=True, help_text=_("Metadata about course.")
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Creator"),
        on_delete=models.CASCADE,
        help_text=_("Creator of the course, mainly responsible for the content"),
    )
    lecturers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Lecturers"),
        blank=True,
        related_name='lecturers',
    )
    thumbnail = models.ImageField(
        blank=True,
        null=True,
        upload_to='courses/',
        validators=[FileExtensionValidator(["jpg", "jpeg", "png"])],
        help_text=_("Preferred size is 600x450px (4by3)."),
    )
    video = models.CharField(max_length=250, null=True, blank=True)
    tag = models.CharField(max_length=250, null=True, blank=True)
    ribbon = models.CharField(max_length=250, null=True, blank=True)
    course_length = models.CharField(max_length=250, null=True, blank=True)
    required_skills = models.CharField(max_length=250, null=True, blank=True)
    mail_subscription = models.ForeignKey(
        'EmailTemplate',
        help_text=_("Sent after subscription."),
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    mail_certificate_generation = models.ForeignKey(
        'EmailTemplate',
        help_text=_("Sent after Certificate generation."),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="mail_certificate_generation"
    )
    mail_run_started = models.ForeignKey(
        'EmailTemplate',
        help_text=_("Sent right before Run starts."),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="mail_run_started"
    )
    mail_meeting_starts = models.ForeignKey(
        'EmailTemplate',
        help_text=_("Sent right before Meeting starts."),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="mail_meeting_starts"
    )
    certificate_template = models.ForeignKey(
        "CertificateTemplate",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    payment_profile = models.ForeignKey(
        PaymentProfile,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
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

    def get_required_submissions(self, lecture=True, chapter=False):
        required_lectures = []
        required_chapters = []

        for db_chapter in self.chapter_set.all():
            if chapter and db_chapter.require_submission in (
                "C",
                "E",
            ):
                required_chapters.append(db_chapter)

            for db_lecture in db_chapter.lecture_set.all():
                if lecture and db_lecture.require_submission in (
                    "C",
                    "E",
                ):
                    required_lectures.append(db_lecture)

        if chapter and lecture:
            return required_chapters, required_lectures
        elif chapter:
            return required_chapters
        elif lecture:
            return required_lectures
        else:
            return ()

    @property
    def length(self):
        length = 0

        for chapter in self.chapter_set.all():
            length += chapter.length

        return length

    def self_paced(self):
        return self.length == 0


class ChapterManager(models.Manager):
    """
    Manager at pre-select all related items for each query set.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related("course", "previous").prefetch_related("lecture_set")


class Chapter(models.Model):
    class Meta:
        verbose_name = _("Chapter")
        verbose_name_plural = _("Chapters")

    objects = ChapterManager()
    objects_no_relations = models.Manager()

    title = models.CharField(verbose_name=_("Title"), max_length=250)
    previous = models.ForeignKey(
        "self", verbose_name=_("Previous chapter"), blank=True, null=True, on_delete=models.SET_NULL
    )
    slug = AutoSlugField(verbose_name=_("Slug"), populate_from="title", editable=True, unique=True)
    perex = models.TextField(
        verbose_name=_("Perex"),
        blank=True,
        null=True,
        help_text=_("Short description of the chapter displayed in the list" " of all chapters."),
    )
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
        null=True,
        help_text=_("Full description of the chapter. Explain what " "will user learn in this lesson."),
    )
    course = models.ForeignKey(Course, verbose_name=_("Course"), on_delete=models.CASCADE)
    length = models.IntegerField(
        verbose_name=_("Length"),
        default=7,
        help_text=_(
            "Number of days that chapter will be open. If all chapters "
            "length is set to 0 course is considered self-paced."
        ),
    )
    require_submission = models.CharField(
        verbose_name=_("Require submission"),
        max_length=1,
        choices=SUBMISSION_TYPE,
        default="D",
        help_text=_("A submission can be required either for continuing to the next chapter or to finish the course."),
    )
    require_submission_review = models.CharField(
        verbose_name=_("Require submission review"),
        max_length=1,
        choices=SUBMISSION_TYPE,
        default="D",
        help_text=_("Submission is accepted only after being accepted by a review."),
    )
    mail_chapter_open = models.ForeignKey(
        'EmailTemplate',
        help_text=_("Sent when the Chapter opens."),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
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
            if not course_settings.COURSES_ALLOW_ACCESS_TO_PASSED_CHAPTERS:
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


class LectureManager(models.Manager):
    """
    Manager at pre-select all related items for each query set.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related("chapter")


class Lecture(models.Model):
    class Meta:
        verbose_name = _("Lecture")
        verbose_name_plural = _("Lectures")

    objects = LectureManager()
    objects_no_relations = models.Manager()

    title = models.CharField(verbose_name=_("Title"), max_length=250)
    slug = AutoSlugField(verbose_name=_("Slug"), populate_from="title", editable=True, unique=True)
    subtitle = models.CharField(verbose_name=_("Subtitle"), blank=True, null=True, max_length=250)
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
        null=True,
        help_text=_("Introduce the study material, explain what data " "are uploaded."),
    )
    data = models.FileField(
        verbose_name=_("Data"),
        blank=True,
        null=True,
        upload_to="lectures",
        help_text=_("Upload study material (document, " "video, image)."),
        validators=[
            FileExtensionValidator(["jpg", "jpeg", "gif", "png", "tiff", "svg", "pdf", "mkv", "avi", "mp4", "mov"]),
            FileSizeValidator(course_settings.MAX_FILE_SIZE_UPLOAD),
        ],
    )
    metadata = models.JSONField(
        verbose_name=_("Metadata"), blank=True, null=True, help_text=_("Metadata about uploaded data.")
    )
    video = EmbedVideoField(verbose_name=_("Video"), blank=True, null=True)
    chapter = models.ForeignKey(Chapter, verbose_name=_("Chapter"), on_delete=models.CASCADE)
    lecture_type = models.CharField(verbose_name=_("Lecture type"), max_length=2, choices=LECTURE_TYPE, default="V")
    require_submission = models.CharField(
        verbose_name=_("Require submission"),
        max_length=1,
        choices=SUBMISSION_TYPE,
        default="N",
        help_text=_("A submission can be required either for continuing to the next chapter or to finish the course."),
    )
    public_submission = models.BooleanField(
        verbose_name=_("Make submissions public within Group"),
        default=False,
    )
    require_submission_review = models.CharField(
        verbose_name=_("Require submission review"),
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
            if self.lecture_type == LECTURE_TYPE[0][0] and not self.check_file_extension(
                self.data, course_settings.EXTENSION_VIDEO
            ):
                raise ValidationError(
                    {
                        "data": _(
                            'Lecture type is "%(lecture_type)s" but you are not uploading such file. Allowed '
                            "extensions: %(file_format)s"
                            % {"lecture_type": LECTURE_TYPE[0][1], "file_format": course_settings.EXTENSION_VIDEO}
                        )
                    }
                )

            if self.lecture_type == LECTURE_TYPE[1][0] and not self.check_file_extension(
                self.data, course_settings.EXTENSION_IMAGE + course_settings.EXTENSION_DOCUMENT
            ):
                raise ValidationError(
                    {
                        "data": _(
                            'Lecture type is "%(lecture_type)s" but you are not uploading such file. Allowed '
                            "extensions: %(file_format)s"
                            % {
                                "lecture_type": LECTURE_TYPE[1][1],
                                "file_format": course_settings.EXTENSION_IMAGE + course_settings.EXTENSION_DOCUMENT,
                            }
                        )
                    }
                )

    def video_duration(self):
        if self.metadata and self.metadata.get("video_duration", None):
            return strftime("%-Mm %Ss", gmtime(self.metadata.get("video_duration")))
        return None

    def video_duration_seconds(self):
        if self.metadata:
            return self.metadata.get("video_duration", 0)
        return 0


class RunManager(models.Manager):
    """
    Manager at pre-select all related items for each query set.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related("course", "manager").prefetch_related("meeting_set")


class Run(models.Model):
    class Meta:
        verbose_name = _("Course Run")
        verbose_name_plural = _("Course Runs")

    objects = RunManager()
    objects_no_relations = models.Manager()

    title = models.CharField(verbose_name=_("Title"), max_length=250)
    slug = AutoSlugField(verbose_name=_("Slug"), populate_from="title", editable=True, unique=True)
    perex = models.TextField(
        verbose_name=_("Perex"),
        blank=True,
        null=True,
        help_text=_(
            "Short description displayed in course list, use as course perex. If empty course perex will be used."
        ),
    )
    start = models.DateField(verbose_name=_("Start"))
    end = models.DateField(
        verbose_name=_("End"),
        blank=True,
        null=True,
        help_text=_("Date will be calculated automatically if any of the chapter has length set."),
    )
    course = models.ForeignKey(Course, verbose_name=_("Course"), on_delete=models.CASCADE)
    state = models.CharField(verbose_name=_("State"), max_length=1, choices=STATE, default="D")
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_("Users"), through="RunUsers", blank=True)
    price = models.FloatField(
        verbose_name=_("Price"),
        default=0,
        help_text=_("Price for the course run that will have to be payed by the subscriber."),
    )
    limit = models.IntegerField(
        verbose_name=_("Limit"),
        default=0,
        help_text=_(
            "Max number of attendees, after which registration for the Run will close. If set to 0 the course will "
            "have no limit."
        ),
    )
    metadata = models.JSONField(verbose_name=_("Metadata"), blank=True, null=True, help_text=_("Metadata about run."))
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Manager"),
        on_delete=models.CASCADE,
        related_name="manager",
        help_text=_("Manager of the course run, responsible for the smoothness of the run."),
    )
    allow_public_submission = models.BooleanField(
        verbose_name=_("Allow public submissions within Group (has to be set per course lecture)"),
        default=False,
    )
    instructions = models.TextField(
        verbose_name=_("Instructions"),
        blank=True,
        null=True,
        help_text=_(
            "Instructions displayed in course overview (visible only to registered users)."
        ),
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

    def passed(self, user_id):
        passed = True
        required_chapters, required_lectures = self.course.get_required_submissions(lecture=True, chapter=True)
        submissions = self.submission_set.filter(author_id=user_id).all()

        for chapter in required_chapters:
            has_submissoin = False

            for submission in submissions:
                if chapter == submission.lecture:
                    has_submissoin = True

            if not has_submissoin:
                passed = False

        for lecture in required_lectures:
            has_submissoin = False

            for submission in submissions:
                if lecture == submission.lecture:
                    has_submissoin = True

            if not has_submissoin:
                passed = False

        return passed

    def get_setting(self, option):
        if self.metadata and "options" in self.metadata and option in self.metadata["options"]:
            option_value = self.metadata["options"][option]
        elif self.course.metadata and "options" in self.course.metadata and option in self.course.metadata["options"]:
            option_value = self.course.metadata["options"][option]
        else:
            option_value = getattr(course_settings, option, "__NOT_FOUND__")

            if option_value == "__NOT_FOUND__":
                raise ValueError("Unknown setting!")

        return option_value

    def get_subscription_level(self, user):
        level = []

        for run_user in self.users.through.objects.filter(run=self).filter(user=user).all():
            if run_user.subscription_level:
                level.append((run_user.id, run_user.subscription_level))

        return level

    def user_payment(self, user):
        total = 0

        for run_user in self.users.through.objects.filter(run=self).filter(user=user).all():
            if run_user.payment:
                total += run_user.payment

        return total

    def save(self, *args, **kwargs):
        if self.length != 0:
            self.end = self.start + timedelta(days=self.length - 1)

        super().save(*args, **kwargs)


class Faq(models.Model):
    STATE = (
        ("D", _("Draft")),
        ("C", _("Course")),
        ("S", _("Subscribed Course")),
        ("B", _("Both")),
    )

    class Meta:
        verbose_name = _("Frequently asked question")
        verbose_name_plural = _("Frequently asked questions")

    question = models.CharField(verbose_name=_("Question"), max_length=250)
    answer = models.TextField(verbose_name=_("Description"), help_text=_("Full description of the question."))
    order = models.IntegerField(default=0, help_text=_("Order number for the question."))
    state = models.CharField(verbose_name=_("State"), max_length=1, choices=STATE, default="D")
    course = models.ForeignKey(Course, verbose_name=_("Course"), on_delete=models.CASCADE)
    run = models.ForeignKey(Run, verbose_name=_("Run"), on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.order}. {self.question}"


class SubscriptionLevel(models.Model):
    class Meta:
        verbose_name = _("Subscription Level")
        verbose_name_plural = _("Subscription Levels")

    run = models.ForeignKey(Run, verbose_name=_("Run"), on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey(Course, verbose_name=_("Course"), on_delete=models.CASCADE, null=True, blank=True)
    price = models.FloatField(verbose_name=_("Price"))
    title = models.CharField(verbose_name=_("Title"), max_length=250)
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
        null=True,
        help_text=_("Full description of the subscription level."),
    )
    metadata = models.JSONField(
        verbose_name=_("Metadata"), blank=True, null=True, help_text=_("Metadata about uploaded data.")
    )

    def __str__(self):
        if self.run:
            return f"{self.run}: {self.title} ({self.price})"
        elif self.course:
            return f"{self.course}: {self.title} ({self.price})"
        else:
            return f"{self.title} ({self.price})"


class RunUsers(models.Model):
    class Meta:
        verbose_name = _("Run User")
        verbose_name_plural = _("Run Users")

    run = models.ForeignKey(Run, verbose_name=_("Run"), on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=models.CASCADE)
    subscription_level = models.ForeignKey(
        SubscriptionLevel, verbose_name=_("Subscription Level"), on_delete=models.CASCADE, blank=True, null=True
    )
    payment = models.FloatField(verbose_name=_("Payment"), default=0)
    price = models.FloatField(verbose_name=_("Price"))
    metadata = models.JSONField(
        verbose_name=_("Metadata"), blank=True, null=True, help_text=_("Metadata about RunUser.")
    )
    timestamp_added = models.DateTimeField(verbose_name=_("Added"), auto_now_add=True)
    timestamp_modified = models.DateTimeField(verbose_name=_("Modified"), auto_now=True)
    note = models.TextField(
        verbose_name=_("Note"), help_text=_("Visible only to admins"), null=True, blank=True
    )

    def __str__(self):
        return f"{self.run}_{self.user}: {self.timestamp_added} {self.payment}"

    def clean(self):
        pass
        # TODO: validate: subscription_level.run == run

        # Causes error in admin, when limit is one and we want to subscribe one user...
        # if self.run.is_full:
        #     raise ValidationError({"user": _("Subscribed user's limit has been reached.")})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class MeetingManager(models.Manager):
    """
    Manager at pre-select all related items for each query set.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related("run", "lecture", "leader", "organizer")


class Meeting(models.Model):
    class Meta:
        verbose_name = _("Meeting")
        verbose_name_plural = _("Meetings")

    objects = MeetingManager()
    objects_no_relations = models.Manager()

    run = models.ForeignKey(Run, verbose_name=_("Run"), on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, verbose_name=_("Lecture"), on_delete=models.CASCADE)
    start = models.DateTimeField(verbose_name=_("Start"))
    end = models.DateTimeField(verbose_name=_("End"))
    link = models.URLField(verbose_name=_("Link"), max_length=250)
    description = models.TextField(verbose_name=_("Description"), blank=True, null=True)
    metadata = models.JSONField(
        verbose_name=_("Metadata"), blank=True, null=True, help_text=_("Metadata about meeting.")
    )
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Leader"),
        on_delete=models.CASCADE,
        related_name="leader",
        blank=True,
        null=True,
        help_text=_("Leader of the meeting, eg. lecturer, vip..."),
    )
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Organizer"),
        on_delete=models.CASCADE,
        related_name="organizer",
        help_text=_("Organizer of the meeting, responsible for the meeting."),
    )

    def __str__(self):
        return _("Meeting") + f": {self.run} {self.lecture}: {self.start} {self.end}"

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

        # Commented because it prevented editing the Run after it has ended (which is sometimes necessary)
        # if self.run.end and self.run.end < date.today():
        #     raise ValidationError(_("You are not allowed to add meeting to run that has already finished."))

        # Commented because it prevented editing the Run after it has ended (which is sometimes necessary)
        # if self.run not in self.lecture.chapter.course.get_active_runs():
        #     raise ValidationError({"lecture": _("Lecture does not belong to this course (and its chapters).")})

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


class SubmissionManager(models.Manager):
    """
    Manager at pre-select all related items for each query set.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related("lecture", "chapter", "run", "author").prefetch_related("review_set")


class Submission(models.Model):
    class Meta:
        verbose_name = _("Submission")
        verbose_name_plural = _("Submissions")

    objects = SubmissionManager()
    objects_no_relations = models.Manager()

    title = models.CharField(verbose_name=_("Title"), max_length=250)
    description = models.TextField(
        verbose_name=_("Description"), blank=True, null=True, help_text=_("Describe what you have learned.")
    )
    data = models.FileField(
        verbose_name=_("Attachment"),
        blank=True,
        null=True,
        upload_to="submissions",
        help_text=_("Upload an attachment."),
        validators=[
            FileExtensionValidator(["jpg", "jpeg", "png", "gif", "webp", "svg", "pdf", "doc", "docx", "txt", "hex", "zip"]),
            FileSizeValidator(course_settings.MAX_FILE_SIZE_UPLOAD_FRONTEND),
        ],
    )
    image = models.FileField(
        verbose_name=_("Image"),
        blank=True,
        null=True,
        upload_to="submissions",
        help_text=_("Upload an image of your work."),
        validators=[
            FileExtensionValidator(["jpg", "jpeg", "png", "gif", "webp", "svg"]),
            FileSizeValidator(course_settings.MAX_FILE_SIZE_UPLOAD_FRONTEND),
        ],
    )
    video_link = models.CharField(verbose_name=_("Video link"), max_length=250, null=True, blank=True)
    lecture = models.ForeignKey(Lecture, verbose_name=_("Lecture"), on_delete=models.CASCADE, null=True, blank=True)
    chapter = models.ForeignKey(Chapter, verbose_name=_("Chapter"), on_delete=models.CASCADE, null=True, blank=True)
    run = models.ForeignKey(Run, verbose_name=_("Run"), on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Author"), on_delete=models.CASCADE)
    metadata = models.JSONField(
        verbose_name=_("Metadata"), blank=True, null=True, help_text=_("Metadata about submission.")
    )
    timestamp_added = models.DateTimeField(verbose_name=_("Added"), auto_now_add=True)
    timestamp_modified = models.DateTimeField(verbose_name=_("Modified"), auto_now=True)

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


class ReviewManager(models.Manager):
    """
    Manager at pre-select all related items for each query set.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related("submission", "author")


class Review(models.Model):
    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")

        unique_together = (
            "submission",
            "author",
        )

    objects = ReviewManager()
    objects_no_relations = models.Manager()

    title = models.CharField(verbose_name=_("Title"), max_length=250)
    description = models.TextField(
        verbose_name=_("Description"), blank=True, null=True, help_text=_("Describe your opinion about the submission.")
    )
    submission = models.ForeignKey(Submission, verbose_name=_("Submission"), on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Author"), on_delete=models.CASCADE)
    accepted = models.BooleanField(
        verbose_name=_("Accepted"),
        help_text=_(
            "Check if the submission if acceptable. If not, the reviewee will have to submit a new submission."
        ),
    )
    timestamp_added = models.DateTimeField(verbose_name=_("Added"), auto_now_add=True)
    timestamp_modified = models.DateTimeField(verbose_name=_("Modified"), auto_now=True)

    def __str__(self):
        return f"{self.title}"

    def clean(self):
        if self.author == self.submission.author:
            raise ValidationError({"author": _("You can not review your own submission!")})


class CertificateManager(models.Manager):
    """
    Manager at pre-select all related items for each query set.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related("run", "user")


class Certificate(models.Model):
    class Meta:
        verbose_name = _("Certificate")
        verbose_name_plural = _("Certificates")

        unique_together = (
            "run",
            "user",
        )

    objects = CertificateManager()
    objects_no_relations = models.Manager()

    uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    data = models.FileField(
        verbose_name=_("Data"),
        upload_to="certificates",
        validators=[FileExtensionValidator(["pdf"]), FileSizeValidator(course_settings.MAX_FILE_SIZE_UPLOAD_FRONTEND)],
        null=True,
        blank=True,
        help_text=_("Field not used for now. Please ignore it."),
    )
    run = models.ForeignKey(Run, verbose_name=_("Run"), on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=models.CASCADE)
    timestamp_added = models.DateTimeField(verbose_name=_("Added"), auto_now_add=True)

    certificate_template = models.ForeignKey(
        "CertificateTemplate",
        on_delete=models.SET_NULL,
        null=True,
    )

    def __str__(self):
        return _("Certificate") + f": {self.run} - {self.user}"


class EmailTemplate(models.Model):
    title = models.CharField(
        verbose_name=_("Title"),
        max_length=250,
        help_text=_("This title is for management purposes only, it will not be seen by the users."),
    )
    mail_subject = models.TextField(
        verbose_name=_("Email subject"),
        help_text=_("Email will be sent with this subject."),
    )
    mail_body_html = models.TextField(
        verbose_name=_("Email html"),
        help_text=_("HTML content of email body."),
    )
    json = models.TextField(
        verbose_name=_("Source JSON"),
        help_text=_("JSON source of the email used by Unlayer Editor. Can be blank."),
        blank=True,
        null=True,
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Creator"),
        on_delete=models.SET_NULL,
        help_text=_("Creator of the email template."),
        null=True,
        blank=True,
    )
    timestamp_added = models.DateTimeField(verbose_name=_("Added"), auto_now_add=True)
    timestamp_modified = models.DateTimeField(verbose_name=_("Modified"), auto_now=True)

    def __str__(self):
        return self.title

    def get_template(self):
        return {"subject": self.mail_subject, "html": self.mail_body_html, "plaintext": self.mail_body_plaintext}


class EmailTemplateImage(models.Model):
    title = models.CharField(
        verbose_name=_("Title"),
        max_length=250,
        help_text=_("The title of the image"),
        blank=True,
        null=True,
    )
    data = models.FileField(
        verbose_name=_("Data"),
        upload_to="email_template_images",
        validators=[
            FileExtensionValidator(["jpg", "jpeg", "gif", "png", "tiff", "svg",]),
            FileSizeValidator(course_settings.MAX_FILE_SIZE_UPLOAD),
        ],
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Creator"),
        on_delete=models.CASCADE,
        help_text=_("Uploader of the image."),
    )
    email_template = models.ForeignKey(
        EmailTemplate,
        verbose_name=_("Email template"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    timestamp_added = models.DateTimeField(verbose_name=_("Added"), auto_now_add=True)
    timestamp_modified = models.DateTimeField(verbose_name=_("Modified"), auto_now=True)


class CertificateTemplate(models.Model):
    intended_course = models.ForeignKey(
        Course,
        verbose_name=_("Intended course"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_("Only for informational admin purposes, can be used by multiple courses or none"),
    )
    title = models.CharField(
        max_length=250,
        verbose_name=_("Title"),
        help_text=_("Only for informational admin purposes, this field is not shown on the certificate")
    )
    html = models.TextField(
        verbose_name=_("HTML"),
        help_text=_("HTML template of the Certificate"),
    )
    timestamp_added = models.DateTimeField(verbose_name=_("Added"), auto_now_add=True)
    timestamp_modified = models.DateTimeField(verbose_name=_("Modified"), auto_now=True)

    def __str__(self):
        return self.title