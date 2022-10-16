import datetime
import os
from time import gmtime
from time import strftime

from django.db.models import Q, F
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.template import Template, Context
from django.http import HttpResponseNotFound

from wkhtmltopdf.views import PDFTemplateView

from courses.decorators import verify_payment
from courses.forms import SubmissionForm, SubscribeForm
from courses.models import Course, Run, Submission, Lecture, Certificate, SubscriptionLevel
from courses.utils import get_run_chapter_context, submissions_get_video_links

from courses.settings import COURSES_LANDING_PAGE_URL, COURSES_LANDING_PAGE_URL_AUTHORIZED

from courses.app_logic.courses_logic import get_public_courses, get_category, get_course


def index(request):
    if request.user.is_authenticated:
        return redirect(COURSES_LANDING_PAGE_URL_AUTHORIZED)
    return redirect(COURSES_LANDING_PAGE_URL)


def courses(request, category_slug=None):

    context = {}

    if category_slug is not None:
        try:
            category = get_category(category_slug=category_slug)
            context["page_tab_title"] = category.page_title
            context["page_title"] = category.page_title
            context["page_subtitle"] = category.page_subtitle
            context["category_footer"] = category.footer
        except ObjectDoesNotExist as err:
            try:
                course = get_course(course_slug=category_slug)
                # redirect to course if entered slug matches a course slug (mainly legacy reasons)
                return redirect("course_detail", course_slug=category_slug)
            except ObjectDoesNotExist as err:
                return HttpResponseNotFound(_("Specified course category not found."))

    else:
        context["page_tab_title"] = _("Courses")
        context["page_title"] = _("Courses")

    courses = get_public_courses(category_slug)
    context["courses"] = courses

    return render(request, os.path.join("courses", "courses_list.html"), context)


def course_detail(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    context = {
        "course": course,
        "questions": course.faq_set.filter(state__in=("C", "B")).all(),
        "course_runs": course.run_set.filter(state="O"),
        "breadcrumbs": [
            {
                "url": reverse("courses"),
                "title": _("Courses"),
            },
            {
                "title": course.title,
            },
        ],
        "chapters": [],
        "page_tab_title": course.title,
    }

    total_lecture_count = 0
    video_lecture_count = 0
    total_video_lecture_duration = 0

    for chapter in course.chapter_set.order_by(F("previous").asc(nulls_first=True)).all():
        context["chapters"].append(
            {
                "lecture_set": chapter.lecture_set.order_by("order", "title"),
                "title": chapter.title,
            }
        )
        total_lecture_count += chapter.lecture_set.count()
        video_lecture_count += chapter.lecture_set.filter(lecture_type="V").count()

        for lecture in chapter.lecture_set.all():
            total_video_lecture_duration += lecture.video_duration_seconds()

    context['total_lecture_count'] = total_lecture_count
    context['video_lecture_count'] = video_lecture_count
    context['total_video_lecture_duration'] = strftime("%-Hh %-Mm %Ss", gmtime(total_video_lecture_duration))

    return render(request, "courses/course_detail.html", context)


@login_required
def all_active_runs(request):
    course_runs = (
        Run.objects.filter(course__state="O")
        .filter(Q(end__gte=datetime.datetime.today()) | Q(end=None))
        .order_by("start")
    )
    context = {
        "runs": course_runs,
        "breadcrumbs": [
            {
                "url": reverse("courses"),
                "title": _("Courses"),
            },
            {
                "title": _("Open courses"),
            },
        ],
    }

    return render(request, "courses/runs_list.html", context)


@login_required
def all_subscribed_runs(request):
    course_runs = (
        Run.objects.filter(runusers__user=request.user)
        .order_by("start")
    )
    context = {
        "runs": course_runs,
        "breadcrumbs": [
            {
                "url": reverse("courses"),
                "title": _("Courses"),
            },
            {
                "title": _("My courses"),
            },
        ],
        "page_tab_title": _("My courses"),
    }

    return render(request, "courses/runs_list.html", context)


@login_required
def all_subscribed_active_runs(request):
    course_runs = (
        Run.objects.filter(course__state="O")
        .filter(Q(end__gte=datetime.datetime.today()) | Q(end=None))
        .filter(runusers__user=request.user)
        .order_by("start")
    )
    context = {
        "runs": course_runs,
        "breadcrumbs": [
            {
                "url": reverse("courses"),
                "title": _("Courses"),
            },
            {
                "url": reverse("all_active_runs"),
                "title": _("Open courses"),
            },
            {
                "title": _("Subscribed courses"),
            },
        ],
    }

    return render(request, "courses/runs_list.html", context)


@login_required
def all_subscribed_closed_runs(request):
    course_runs = (
        Run.objects.filter(Q(course__state="O") | Q(course__state="C"))
        .filter(Q(end__lt=datetime.datetime.today()))
        .filter(runusers__user=request.user)
        .order_by("-start")
    )
    context = {
        "runs": course_runs,
        "breadcrumbs": [
            {
                "url": reverse("courses"),
                "title": _("Courses"),
            },
            {
                "title": _("Subscribed closed courses"),
            },
        ],
    }

    return render(request, "courses/runs_list.html", context)


@login_required
def all_closed_runs(request):
    if not request.user.is_staff:
        raise PermissionDenied(_("You are not allowed to visit this page."))

    course_runs = (
        Run.objects.filter(Q(course__state="O") | Q(course__state="C"))
        .filter(Q(end__lt=datetime.datetime.today()))
        .order_by("-start")
    )
    context = {
        "runs": course_runs,
        "breadcrumbs": [
            {
                "url": reverse("courses"),
                "title": _("Courses"),
            },
            {
                "title": _("Closed courses"),
            },
        ],
    }

    return render(request, "courses/runs_list.html", context)


def course_run_detail(request, run_slug):
    run = get_object_or_404(Run, slug=run_slug)
    subscription_levels = SubscriptionLevel.objects.filter(run=run)
    form = SubscribeForm(
        initial={"sender": request.user.username, "run_slug": run_slug},
        subscription_levels=subscription_levels.values_list("id", "title"),
    )

    context = {
        "run": run,
        "subscription_levels": subscription_levels.all(),
        "chapters": [],
        "form": form,
        "subscribed": run.is_subscribed(request.user),
        "breadcrumbs": [
            {
                "url": reverse("courses"),
                "title": _("Courses"),
            },
            {
                "url": reverse("course_detail", args=(run.course.slug,)),
                "title": run.course.title,
            },
            {
                "title": run.title.upper(),
            },
        ],
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

    return render(request, "courses/run_detail.html", context)


@login_required
@verify_payment
def chapter_detail(request, run_slug, chapter_slug):
    context = get_run_chapter_context(request, run_slug, chapter_slug)

    return render(request, "courses/chapter_detail.html", context)


@login_required
@verify_payment
def chapter_submission(request, run_slug, chapter_slug):
    context = get_run_chapter_context(request, run_slug, chapter_slug)

    if context["chapter"].require_submission == "D":
        raise PermissionDenied(_("Submission is not allowed."))

    context["breadcrumbs"][3]["url"] = reverse("chapter_detail", args=(run_slug, chapter_slug))
    context["breadcrumbs"].append({"title": _("Chapter Submission")})

    user_submissions = (
        Submission.objects.filter(author=request.user)
        .filter(run=context["run"])
        .filter(chapter=context["chapter"])
        .all()
    )

    if request.method == "POST":
        if datetime.date.today() > context["end"] and not context["run"].get_setting(
            "COURSES_ALLOW_SUBMISSION_TO_PASSED_CHAPTERS"
        ):
            raise PermissionDenied(_("Chapter has already ended...") + " " + _("Submission is not allowed."))

        if len(user_submissions) == 1:
            submission = user_submissions[0]
        else:
            submission = Submission(chapter=context["chapter"], run=context["run"], author=request.user)

        form = SubmissionForm(request.POST, request.FILES, instance=submission)

        if form.is_valid():
            form.save()

            messages.success(request, _("Your submission has been saved."))
            return redirect("chapter_submission", run_slug=run_slug, chapter_slug=chapter_slug)
        else:
            messages.error(request, _("Please correct form errors."))

    elif datetime.date.today() > context["end"] and not context["run"].get_setting(
        "COURSES_ALLOW_SUBMISSION_TO_PASSED_CHAPTERS"
    ):
        context["user_submissions"] = user_submissions
        form = None
    elif len(user_submissions) == 1:
        submission = user_submissions[0]
        form = SubmissionForm(instance=submission)
    else:
        form = SubmissionForm()

    context["form"] = form

    return render(request, "courses/chapter_submission.html", context)


@login_required
@verify_payment
def chapter_lecture_types(request, run_slug, chapter_slug, lecture_type):
    context = get_run_chapter_context(request, run_slug, chapter_slug)
    context["breadcrumbs"][3]["url"] = reverse("chapter_detail", args=(run_slug, chapter_slug))
    context["breadcrumbs"].append({"title": _("Videos")})
    context["lectures"] = context["chapter"].lecture_set.filter(lecture_type=lecture_type).all()
    context["filter_lecture_type"] = lecture_type

    return render(request, "courses/chapter_detail.html", context)


@login_required
@verify_payment
def lecture_detail(request, run_slug, chapter_slug, lecture_slug):
    lecture = get_object_or_404(Lecture, slug=lecture_slug)
    # TODO: verify url mix and match of run and course
    # TODO: verify url mix and match of lecture and course

    context = get_run_chapter_context(request, run_slug, chapter_slug)

    if context["run"].get_setting("COURSES_DISPLAY_CHAPTER_DETAILS"):
        context["breadcrumbs"][3]["url"] = reverse("chapter_detail", args=(run_slug, chapter_slug))

    context["breadcrumbs"].append({"title": lecture.title})
    context["lecture"] = lecture

    user_submissions = (
        Submission.objects.filter(author=request.user).filter(run=context["run"]).filter(lecture=lecture).all()
    )

    if request.method == "POST":
        if lecture.require_submission == "D":
            raise PermissionDenied(_("Submission is not allowed."))

        if datetime.date.today() > context["end"] and not context["run"].get_setting(
            "COURSES_ALLOW_SUBMISSION_TO_PASSED_CHAPTERS"
        ):
            raise PermissionDenied(_("Chapter has already ended...") + " " + _("Submission is not allowed."))

        if len(user_submissions) == 1:
            submission = user_submissions[0]
        else:
            submission = Submission(lecture=lecture, run=context["run"], author=request.user)

        form = SubmissionForm(request.POST, request.FILES, instance=submission)

        if form.is_valid():
            form.save()

            messages.success(request, _("Your submission has been saved."))
            return redirect("lecture_detail", run_slug=run_slug, chapter_slug=chapter_slug, lecture_slug=lecture_slug)
        else:
            messages.error(request, _("Please correct form errors."))

    elif datetime.date.today() > context["end"] and not context["run"].get_setting(
        "COURSES_ALLOW_SUBMISSION_TO_PASSED_CHAPTERS"
    ):
        form = None
    elif len(user_submissions) == 1:
        submission = user_submissions[0]
        form = SubmissionForm(instance=submission)
    else:
        form = SubmissionForm()

    context["user_submissions"] = submissions_get_video_links(user_submissions)
    context["form"] = form
    context["page_tab_title"] = lecture.title

    return render(request, "courses/lecture_detail.html", context)


@login_required
@verify_payment
def certificate(request, uuid):
    cert = get_object_or_404(Certificate, uuid=uuid)

    if not cert.certificate_template:
        return HttpResponseNotFound(_("Certificate template not specified!"))

    template = Template(cert.certificate_template.html)
    context = Context({"cert": cert})
    cert_content = template.render(context)

    return render(request, "courses/certificate.html", {"cert_content": cert_content})


class CertificatePDF(PDFTemplateView):
    filename = "certifikat.pdf"
    template_name = "courses/certificate.html"  # only a "blank" template where the real template is later inserter
    cmd_options = {
        "margin-top": 3,
    }

    def get(self, request, uuid, *args, **kwargs):
        cert = get_object_or_404(Certificate, uuid=uuid)

        if not cert.certificate_template:
            return HttpResponseNotFound(_("Certificate template not specified!"))

        # The actual template rendering happens here, it is later inserted in to a wrapper template
        template = Template(cert.certificate_template.html)
        context = Context({"cert": cert})
        cert_content = template.render(context)

        return super().get(request, *args, cert=cert, cert_content=cert_content, **kwargs)
