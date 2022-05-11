import re
import html2text

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404
from django.template import TemplateDoesNotExist, Template, Context
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


# TODO: This function is being replaced by construct_templated_email and send_templated_email and should be deleted soon
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


def construct_templated_email(user, mail_subject, mail_body_html, template_variables=dict()):
    """
    Construct an EmailMultiAlternatives object based on the specified HTML email template.
    """
    template_variables["user"] = user
    email = user.email

    # Render Subject and HTML Body of the message
    subject = Template(mail_subject).render(Context(template_variables))
    body_html = Template(mail_body_html).render(Context(template_variables))

    # Generate plaintext version from HTML body
    h = html2text.HTML2Text()
    body_plaintext = h.handle(body_html)

    # Create the email with the plaintext body and attach the HTML body
    email_message = EmailMultiAlternatives(subject, body_plaintext, settings.DEFAULT_FROM_EMAIL, [email])
    email_message.attach_alternative(body_html, "text/html")

    return email_message


def send_templated_email(*args, **kwargs):
    """
    Calls a function to construct an EmailMultiAlternatives object and sends it to the recipient.
    """
    email_message = construct_templated_email(*args, **kwargs)
    email_message.send()


def generate_certificate(run, user, certificate_template, notify=True):
    # TODO: check user is subscribed to this run!
    user_certificates = Certificate.objects.filter(run=run).filter(user=user)

    if user_certificates.count() == 0:
        cert = Certificate(run=run, user=user, certificate_template=certificate_template)
        cert.save()

        if notify:
            mail_template_variables = {
                "certificate": cert,
                "course_run": run,
                "user": user,
                "course": run.course,
            }

            mail_template = run.course.mail_certificate_generation

            # If the mail_template is specified, send a subscription email
            if mail_template:
                send_templated_email(
                    user,
                    mail_subject=mail_template.mail_subject,
                    mail_body_html=mail_template.mail_body_html,
                    template_variables=mail_template_variables,
                )
            # If the mail_template is not specified, notify the Course creator
            else:
                send_templated_email(
                    run.course.creator,
                    mail_subject="Course mail_certificate_generation not specified!",
                    mail_body_html="The mail_certificate_generation template is missing for {{ course|safe }}!\n\n"
                                   "The user {{ user|safe }} did not receive an Certificate Generation email.",
                    template_variables=mail_template_variables,
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
