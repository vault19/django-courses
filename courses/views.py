import datetime

from django.db.models import Q
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.urls import reverse

from courses.forms import SubmissionForm, SubscribeForm
from courses.models import Course, Run, Submission, Lecture
from courses.utils import get_run_chapter_context
from courses.settings import (
    COURSES_LANDING_PAGE_URL,
    COURSES_SHOW_FUTURE_CHAPTERS,
    COURSES_ALLOW_SUBSCRIPTION_TO_RUNNING_COURSE,
    COURSES_ALLOW_USER_UNSUBSCRIBE,
    COURSES_ALLOW_SUBMISSION_TO_PASSED_CHAPTERS,
    COURSES_ALLOW_ACCESS_TO_PASSED_CHAPTERS,
    COURSES_DISPLAY_CHAPTER_DETAILS,
    COURSES_EMAIL_SUBJECT_PREFIX,
    COURSES_SUBSCRIBED_EMAIL_SUBJECT,
    COURSES_SUBSCRIBED_EMAIL_BODY,
    COURSES_SUBSCRIBED_EMAIL_HTML,
)


def index(request):
    return redirect(COURSES_LANDING_PAGE_URL)


def courses(request):
    courses = Course.objects.filter(state="O").order_by("title")
    context = {"courses": courses}

    return render(request, "courses/courses_list.html", context)


def course_detail(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    context = {
        "course": course,
        "course_runs": course.run_set.all(),
        "breadcrumbs": [
            {
                "url": reverse("courses"),
                "title": _("Courses"),
            },
            {
                "title": course.title,
            },
        ],
    }

    return render(request, "courses/course_detail.html", context)


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
    context = {
        "run": run,
        "chapters": [],
        "form": SubscribeForm(initial={"sender": request.user.username, "run_slug": run_slug}),
        "subscribed": run.is_subscribed(request.user),
        "COURSES_DISPLAY_CHAPTER_DETAILS": COURSES_DISPLAY_CHAPTER_DETAILS,
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

    for chapter in run.course.chapter_set.all():
        start, end = chapter.get_run_dates(run=run)

        if (COURSES_SHOW_FUTURE_CHAPTERS or start <= datetime.date.today()) and (
            COURSES_ALLOW_ACCESS_TO_PASSED_CHAPTERS or end > datetime.date.today()
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
def chapter_detail(request, run_slug, chapter_slug):
    context = get_run_chapter_context(request, run_slug, chapter_slug)

    return render(request, "courses/chapter_detail.html", context)


@login_required
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
        if datetime.date.today() > context["end"] and not COURSES_ALLOW_SUBMISSION_TO_PASSED_CHAPTERS:
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

    elif datetime.date.today() > context["end"] and not COURSES_ALLOW_SUBMISSION_TO_PASSED_CHAPTERS:
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
def chapter_lecture_types(request, run_slug, chapter_slug, lecture_type):
    context = get_run_chapter_context(request, run_slug, chapter_slug)
    context["breadcrumbs"][3]["url"] = reverse("chapter_detail", args=(run_slug, chapter_slug))
    context["breadcrumbs"].append({"title": _("Videos")})
    context["lectures"] = context["chapter"].lecture_set.filter(lecture_type=lecture_type).all()
    context["filter_lecture_type"] = lecture_type

    return render(request, "courses/chapter_detail.html", context)


@login_required
def subscribe_to_run(request, run_slug):
    if request.method == "POST":
        run = get_object_or_404(Run, slug=run_slug)

        if run.is_full:
            messages.error(request, _("Subscribed user's limit has been reached."))
        elif not COURSES_ALLOW_SUBSCRIPTION_TO_RUNNING_COURSE and run.start <= timezone.now().date():
            messages.error(request, _("You are not allowed to subscribe to course that has already started."))
        elif run.end < timezone.now().date():
            messages.error(request, _("You are not allowed to subscribe to course that has already finished."))
        elif run.is_subscribed(request.user):
            messages.warning(request, _("You are already subscribed to course: %(run)s.") % {"run": run})
        elif run.is_subscribed_in_different_active_run(request.user):
            messages.error(request, _("You are already subscribed in different course run."))
        else:
            run.users.add(request.user)  # in M2M add will store to DB!
            # run.save()  # No need to save run
            messages.success(request, _("You have been subscribed to course: %(run)s.") % {"run": run})

            ctx_dict = {
                "user": request.user,
                "course_run": run,
            }
            subject = COURSES_EMAIL_SUBJECT_PREFIX + render_to_string(
                COURSES_SUBSCRIBED_EMAIL_SUBJECT, ctx_dict, request=request
            )
            # Email subject *must not* contain newlines
            subject = "".join(subject.splitlines())
            message = render_to_string(COURSES_SUBSCRIBED_EMAIL_BODY, ctx_dict, request=request)

            email_message = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [request.user.email])

            if COURSES_SUBSCRIBED_EMAIL_HTML:
                try:
                    message_html = render_to_string(COURSES_SUBSCRIBED_EMAIL_HTML, ctx_dict, request=request)
                except TemplateDoesNotExist:
                    pass
                else:
                    email_message.attach_alternative(message_html, "text/html")

            email_message.send()
    else:
        messages.warning(request, _("You need to submit subscription form in order to subscribe!"))

    return redirect("course_run_detail", run_slug=run_slug)


@login_required
def unsubscribe_from_run(request, run_slug):
    if request.method == "POST":
        run = get_object_or_404(Run, slug=run_slug)

        if not COURSES_ALLOW_USER_UNSUBSCRIBE:
            messages.warning(request, _("You are not allowed to unsubscribe from the course: %(run)s.") % {"run": run})
        elif run.is_subscribed(request.user):
            run.users.remove(request.user)  # in M2M remove will store to DB!
            # run.save()  # No need to save run
            messages.success(request, _("You have been unsubscribed from course: %(run)s.") % {"run": run})
        else:
            messages.warning(request, _("You are not subscribed to the course: %(run)s.") % {"run": run})
    else:
        messages.warning(request, _("You need to submit subscription form in order to unsubscribe!"))

    return redirect("course_run_detail", run_slug=run_slug)


@login_required
def lecture_detail(request, run_slug, chapter_slug, lecture_slug):
    lecture = get_object_or_404(Lecture, slug=lecture_slug)
    # TODO: verify url mix and match of run and course
    # TODO: verify url mix and match of lecture and course
    context = get_run_chapter_context(request, run_slug, chapter_slug)

    if COURSES_DISPLAY_CHAPTER_DETAILS:
        context["breadcrumbs"][3]["url"] = reverse("chapter_detail", args=(run_slug, chapter_slug))

    context["breadcrumbs"].append({"title": lecture.title})
    context["lecture"] = lecture

    return render(request, "courses/lecture_detail.html", context)


@login_required
def lecture_submission(request, run_slug, chapter_slug, lecture_slug):
    lecture = get_object_or_404(Lecture, slug=lecture_slug)

    if lecture.require_submission == "D":
        raise PermissionDenied(_("Submission is not allowed."))

    context = get_run_chapter_context(request, run_slug, chapter_slug)

    if COURSES_DISPLAY_CHAPTER_DETAILS:
        context["breadcrumbs"][3]["url"] = reverse("chapter_detail", args=(run_slug, chapter_slug))

    context["breadcrumbs"].append({"title": lecture.title, "url": "#"})
    context["breadcrumbs"].append({"title": _("Lecture submission")})

    context["lecture"] = lecture

    user_submissions = (
        Submission.objects.filter(author=request.user).filter(run=context["run"]).filter(lecture=lecture).all()
    )

    if request.method == "POST":
        if datetime.date.today() > context["end"] and not COURSES_ALLOW_SUBMISSION_TO_PASSED_CHAPTERS:
            raise PermissionDenied(_("Chapter has already ended...") + " " + _("Submission is not allowed."))

        if len(user_submissions) == 1:
            submission = user_submissions[0]
        else:
            submission = Submission(lecture=lecture, run=context["run"], author=request.user)

        form = SubmissionForm(request.POST, request.FILES, instance=submission)

        if form.is_valid():
            form.save()

            messages.success(request, _("Your submission has been saved."))
            return redirect(
                "lecture_submission", run_slug=run_slug, chapter_slug=chapter_slug, lecture_slug=lecture_slug
            )
        else:
            messages.error(request, _("Please correct form errors."))

    elif datetime.date.today() > context["end"] and not COURSES_ALLOW_SUBMISSION_TO_PASSED_CHAPTERS:
        context["user_submissions"] = user_submissions
        form = None
    elif len(user_submissions) == 1:
        submission = user_submissions[0]
        form = SubmissionForm(instance=submission)
    else:
        form = SubmissionForm()

    context["form"] = form

    return render(request, "courses/lecture_detail.html", context)
