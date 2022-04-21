import datetime
import re

from django.db.models import Q, F
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from wkhtmltopdf.views import PDFTemplateView

from courses.decorators import verify_payment
from courses.forms import SubmissionForm, SubscribeForm
from courses.models import Course, Run, Submission, Lecture, Certificate, SubscriptionLevel
from courses.utils import get_run_chapter_context

from courses.settings import COURSES_LANDING_PAGE_URL, COURSES_LANDING_PAGE_URL_AUTHORIZED


@login_required
def course_run_overview(request, run_slug):
    run = get_object_or_404(Run, slug=run_slug)

    context = {
        "run": run,
        "chapters": [],
        "subscribed": run.is_subscribed(request.user),
        "page_tab_title": run.title,
    }

    if request.GET.get('partial', False):
        return render(request, "courses/run/partial/overview.html", context)
    else:
        return render(request, "courses/run/overview.html", context)


@login_required
def course_run_chapters(request, run_slug):
    run = get_object_or_404(Run, slug=run_slug)

    context = {
        "run": run,
        "chapters": [],
        "subscribed": run.is_subscribed(request.user),
        "page_tab_title": run.title,
    }

    for chapter in run.course.chapter_set.order_by(F("previous").asc(nulls_first=True)).all():
        start, end = chapter.get_run_dates(run=run)

        if (run.get_setting("COURSES_SHOW_FUTURE_CHAPTERS") or start <= datetime.date.today()) and (
            run.get_setting("COURSES_ALLOW_ACCESS_TO_PASSED_CHAPTERS") or end > datetime.date.today()
        ):
            context["chapters"].append(
                {
                    "lecture_set": chapter.lecture_set.order_by("order", "title"),
                    "start": start,
                    "end": end,
                    "title": chapter.title,
                    "slug": chapter.slug,
                    "perex": chapter.perex,
                    "description": chapter.description,
                    "course": chapter.course,
                    "length": chapter.length,
                    "active": start <= datetime.date.today() <= end,
                    "passed": end < datetime.date.today(),
                }
            )

    if request.GET.get('partial', False):
        return render(request, "courses/run/partial/chapters.html", context)
    else:
        return render(request, "courses/run/chapters.html", context)


@login_required
def course_run_group(request, run_slug):
    run = get_object_or_404(Run, slug=run_slug)

    context = {
        "run": run,
        "chapters": [],
        "subscribed": run.is_subscribed(request.user),
        "page_tab_title": run.title,
    }

    submissions = Submission.objects.filter(run__slug=run_slug)\
        .filter(lecture__public_submission=True).filter(lecture__lecture_type="P")\
        .filter(run__allow_public_submission=True).order_by("-timestamp_added")

    regex = re.compile(
        r'.*(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)'
        r'/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11}).*', re.DOTALL
    )

    for submission in submissions:

        if not submission.video_link:
            match = regex.match(submission.description)

            if match:
                submission.video_link = match.group('id')

    context["submissions"] = submissions

    if request.GET.get('partial', False):
        return render(request, "courses/run/partial/group.html", context)
    else:
        return render(request, "courses/run/group.html", context)


@login_required
def course_run_help(request, run_slug):
    run = get_object_or_404(Run, slug=run_slug)

    context = {
        "run": run,
        "chapters": [],
        "subscribed": run.is_subscribed(request.user),
        "page_tab_title": run.title,
    }

    if request.GET.get('partial', False):
        return render(request, "courses/run/partial/help.html", context)
    else:
        return render(request, "courses/run/help.html", context)


@login_required
def course_faq(request, run_slug):
    run = get_object_or_404(Run, slug=run_slug)

    context = {
        "run": run,
        "questions": run.course.faq_set.filter(state__in=("S", "B")).all(),
        "chapters": [],
        "subscribed": run.is_subscribed(request.user),
        "page_tab_title": run.title,
    }

    if request.GET.get('partial', False):
        return render(request, "courses/run/partial/faq.html", context)
    else:
        return render(request, "courses/run/faq.html", context)
