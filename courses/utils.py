import re

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from courses.settings import COURSES_EMAIL_SUBJECT_PREFIX
from courses.models import Chapter, Run, Certificate
from courses.settings import (
    COURSES_ALLOW_SUBMISSION_TO_CHAPTERS,
    COURSES_ALLOW_SUBMISSION_TO_LECTURES,
    COURSES_DISPLAY_CHAPTER_DETAILS,
)


def get_run_chapter_context(request, run_slug, chapter_slug, raise_unsubscribed=True, raise_wrong_dates=True):
    run = get_object_or_404(Run, slug=run_slug)
    chapter = get_object_or_404(Chapter, slug=chapter_slug)

    if raise_unsubscribed:
        if request.user.is_staff:
            raise_unsubscribed = False

        run.is_subscribed(request.user, raise_unsubscribed=raise_unsubscribed)

    start, end = chapter.get_run_dates(run=run, raise_wrong_dates=raise_wrong_dates)

    breadcrumbs = [
        {
            "url": reverse("courses"),
            "title": _("Courses"),
        },
        {
            "url": reverse("course_detail", args=(run.course.slug,)),
            "title": run.course.title,
        },
        {
            "url": reverse("course_run_detail", args=(run_slug,)),
            "title": run.title.upper(),
        },
        {
            "title": chapter.title,
        },
    ]

    context = {
        "run": run,
        "chapter": chapter,
        "lectures": chapter.lecture_set.all().order_by("order", "title"),
        "start": start,
        "end": end,
        "subscribed": run.is_subscribed(request.user),
        "breadcrumbs": breadcrumbs,
        "COURSES_DISPLAY_CHAPTER_DETAILS": COURSES_DISPLAY_CHAPTER_DETAILS,
        "COURSES_ALLOW_SUBMISSION_TO_CHAPTERS": COURSES_ALLOW_SUBMISSION_TO_CHAPTERS,
        "COURSES_ALLOW_SUBMISSION_TO_LECTURES": COURSES_ALLOW_SUBMISSION_TO_LECTURES,
    }

    return context


def send_email(
    user, mail_subject, mail_body, mail_body_html, email, mail_template_variables=dict(), subject=None, message=None
):
    if user:
        mail_template_variables["user"] = user
        email = user.email

    if subject is None:
        subject = COURSES_EMAIL_SUBJECT_PREFIX + render_to_string(mail_subject, mail_template_variables)
        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines())

    if message is None:
        message = render_to_string(mail_body, mail_template_variables)

    email_message = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

    if mail_body_html:
        try:
            message_html = render_to_string(mail_body_html, mail_template_variables)
        except TemplateDoesNotExist:
            pass
        else:
            email_message.attach_alternative(message_html, "text/html")

    email_message.send()


def generate_certificate(run, user, notify=True):
    # TODO: check user is subscribed to this run!
    user_certificates = Certificate.objects.filter(run=run).filter(user=user)

    if user_certificates.count() == 0:
        cert = Certificate(run=run, user=user)
        cert.save()

        if notify:
            mail_template_variables = {
                "certificate": cert,
                "course_run": run,
                "user": user,
            }
            mail_subject = run.get_setting("COURSES_NOTIFY_CERTIFICATE_EMAIL_SUBJECT")
            mail_body = run.get_setting("COURSES_NOTIFY_CERTIFICATE_EMAIL_BODY")
            mail_body_html = run.get_setting("COURSES_NOTIFY_CERTIFICATE_EMAIL_HTML")

            send_email(
                user,
                email=user.email,
                mail_subject=mail_subject,
                mail_body=mail_body,
                mail_body_html=mail_body_html,
                mail_template_variables=mail_template_variables,
            )

        return True

    return False


def array_partition(array, start, end):
    pivot_index = start

    for i in range(start, end):
        if array[i][0] <= array[end][0]:
            array[i], array[pivot_index] = array[pivot_index], array[i]
            pivot_index += 1

    array[end], array[pivot_index] = array[pivot_index], array[end]

    return pivot_index


def array_quicksort(array, start, end):
    if start < end:
        partition_index = array_partition(array, start, end)
        array_quicksort(array, start, partition_index - 1)
        array_quicksort(array, partition_index + 1, end)


def array_merge(intervals):
    """
    Helper function to sort and merge list of intervals
    :type intervals: list[interval]
    :rtype: list[interval]
    """
    if len(intervals) == 0:
        return []

    array_quicksort(intervals, 0, len(intervals) - 1)
    stack = []
    stack.append(intervals[0])

    for i in range(1, len(intervals)):
        last_element = stack[len(stack) - 1]

        if last_element[1] >= intervals[i][0]:
            last_element[1] = max(intervals[i][1], last_element[1])
            stack.pop(len(stack) - 1)
            stack.append(last_element)
        else:
            stack.append(intervals[i])

    return stack


def submissions_get_video_links(submissions):
    """
    Runs through submissions and finds YouTube video link tags,
    which are then added to the original object
    """
    # TODO: Add support for other platforms (such as Vimeo, OneDrive, ...)

    regex = re.compile(
        r'.*(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)'
        r'/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11}).*', re.DOTALL
    )

    for submission in submissions:

        # If there is not a vide link specified, try to find one in the submission description
        if not submission.video_link:
            match = regex.match(submission.description)
            if match:
                submission.video_link_tag = match.group('id')
                submission.video_link = f"https://youtu.be/{submission.video_link_tag}"

        # If a video link is specified, extract the youtube tag/ID of the video
        else:
            match = regex.match(submission.video_link)
            if match:
                submission.video_link_tag = match.group('id')

    return submissions
