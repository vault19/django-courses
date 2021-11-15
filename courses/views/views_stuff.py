import datetime

from django.db.models import Q, F
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.urls import reverse

from courses.forms import SubmissionForm, SubscribeForm, ReviewForm
from courses.models import Course, Run, Submission, Lecture
from courses.utils import get_run_chapter_context
from courses.settings import COURSES_LANDING_PAGE_URL, COURSES_LANDING_PAGE_URL_AUTHORIZED


@login_required
@user_passes_test(lambda u: u.is_staff)
def runs(request):
    runs = Run.objects.order_by('-end').all()

    context = {}
    context["breadcrumbs"] = [
        {
            "title": _("Review Courses"),
        },
    ]

    context["runs"] = runs

    return render(request, "courses/stuff/runs.html", context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def run_attendees(request, run_slug):
    run = Run.objects.filter(slug=run_slug).order_by('-end').get()

    context = {}
    context["run"] = run
    context["breadcrumbs"] = [
        {
            "url": reverse("runs"),
            "title": _("Review Courses"),
        },
        {
            "title": run.title,
        },
        {
            "title": _("Attendees"),
        },
    ]

    return render(request, "courses/stuff/run_attendees.html", context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def run_attendee_submissions(request, run_slug, user_id):
    run = Run.objects.filter(slug=run_slug).order_by('-end').get()

    context = {}
    context["run"] = run
    context["breadcrumbs"] = [
        {
            "url": reverse("runs"),
            "title": _("Review Courses"),
        },
        {
            "title": run.title,
        },
        {
            "url": reverse("run_attendees", args=(run.slug,)),
            "title": _("Attendees"),
        },
        {
            "title": _("Submissions"),
        },
    ]

    context["submissions"] = Submission.objects.filter(run=run, author_id=user_id).all()
    context['passed'] = run.passed(user_id)

    return render(request, "courses/stuff/run_attendee_submissions.html", context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def lecture_submissions(request, run_slug, chapter_slug, lecture_slug):
    lecture = get_object_or_404(Lecture, slug=lecture_slug)
    context = get_run_chapter_context(request, run_slug, chapter_slug)
    submissions = Submission.objects.filter(lecture=lecture).filter(run=context["run"]).all()

    if context["run"].get_setting("COURSES_DISPLAY_CHAPTER_DETAILS"):
        context["breadcrumbs"][3]["url"] = reverse("chapter_detail", args=(run_slug, chapter_slug))

    context["breadcrumbs"].append(
        {"title": lecture.title, "url": reverse("lecture_detail", args=(run_slug, chapter_slug, lecture_slug))}
    )
    context["breadcrumbs"].append(
        {"title": _("Submissions"), "url": reverse("lecture_submissions", args=(run_slug, chapter_slug, lecture_slug))}
    )

    context["lecture"] = lecture
    context["submissions"] = submissions

    return render(request, "courses/lecture_submissions.html", context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def lecture_submission_review(request, run_slug, chapter_slug, lecture_slug, submission_id):
    lecture = get_object_or_404(Lecture, slug=lecture_slug)
    run = get_object_or_404(Run, slug=run_slug)
    submission = get_object_or_404(Submission, lecture=lecture, run=run, id=submission_id)

    context = get_run_chapter_context(request, run_slug, chapter_slug)
    context["lecture"] = lecture

    if context["run"].get_setting("COURSES_DISPLAY_CHAPTER_DETAILS"):
        context["breadcrumbs"][3]["url"] = reverse("chapter_detail", args=(run_slug, chapter_slug))

    context["breadcrumbs"].append(
        {"title": lecture.title, "url": reverse("lecture_detail", args=(run_slug, chapter_slug, lecture_slug))}
    )
    context["breadcrumbs"].append(
        {"title": _("Submissions"), "url": reverse("lecture_submissions", args=(run_slug, chapter_slug, lecture_slug))}
    )
    context["breadcrumbs"].append({"title": _("Review Submission") + f": {submission.title}"})

    context["submission"] = submission
    instance = None

    for review in submission.review_set.all():
        if review.author == request.user:
            instance = review

    if request.method == "POST":
        form = ReviewForm(submission_id=submission.id, author=request.user.id, data=request.POST, instance=instance)

        if form.is_valid():
            form.save()
            messages.success(request, _("Your review has been saved."))

            return redirect(reverse("lecture_submissions", args=(run_slug, chapter_slug, lecture_slug)))
        else:
            context["form_errors"] = True
    else:
        form = ReviewForm(submission_id=submission.id, author=request.user.id, instance=instance)

    context["form"] = form

    return render(request, "courses/lecture_submission_review.html", context)
