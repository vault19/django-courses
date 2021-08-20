import datetime

from django.db.models import Q
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from courses.forms import SubmissionForm
from courses.models import Course, Run, Submission
from courses.utils import get_run_chapter, verify_course_dates
from courses.settings import COURSES_LANDING_PAGE_URL, COURSES_SHOW_FUTURE_CHAPTERS, \
    COURSES_ALLOW_SUBMISSION_TO_PASSED_CHAPTERS


def index(request):
    return redirect(COURSES_LANDING_PAGE_URL)


def courses(request):
    courses = Course.objects \
        .filter(state='O') \
        .order_by('name')
    context = {'courses': courses}

    return render(request, 'courses/courses.html', context)


def all_active_runs(request):
    course_runs = Run.objects\
        .filter(course__state='O')\
        .filter(Q(end__gte=datetime.datetime.today()) | Q(end=None))\
        .order_by('-start')
    context = {'course_runs': course_runs}

    return render(request, 'courses/index.html', context)


@login_required
def all_closed_runs(request):
    course_runs = Run.objects \
        .filter(Q(course__state='O') | Q(course__state='C')) \
        .filter(Q(end__lt=datetime.datetime.today())) \
        .order_by('-start')
    context = {'course_runs': course_runs}

    return render(request, 'courses/index.html', context)


def course_run_detail(request, run_slug):
    run = get_object_or_404(Run, slug=run_slug)
    chapters = []

    for chapter in run.course.chapter_set.all():
        start, end = chapter.get_run_dates(run=run)

        if COURSES_SHOW_FUTURE_CHAPTERS or start <= datetime.date.today():
            chapters.append({
                'start': start,
                'end': end,
                'title': chapter.title,
                'slug': chapter.slug,
                'perex': chapter.perex,
                'description': chapter.description,
                'course': chapter.course,
                'length': chapter.length,
                'active': start <= datetime.date.today() <= end,
                'passed': end < datetime.date.today(),
            })

    return render(request, 'courses/run_detail.html', {'run': run, 'chapters': chapters})


@login_required
def chapter_detail(request, run_slug, chapter_slug):
    run, chapter = get_run_chapter(run_slug, chapter_slug)
    start, end = chapter.get_run_dates(run=run)
    context = {
        'run': run,
        'chapter': chapter,
        'start': start,
        'end': end
    }
    verify_course_dates(start, end)

    return render(request, 'courses/chapter.html', context)


@login_required
def chapter_submission(request, run_slug, chapter_slug):
    run, chapter = get_run_chapter(run_slug, chapter_slug)
    start, end = chapter.get_run_dates(run=run)
    context = {
        'run': run,
        'chapter': chapter,
        'start': start,
        'end': end
    }
    verify_course_dates(start, end)
    user_submissions = Submission.objects.filter(author=request.user).filter(run=run).filter(chapter=chapter).all()

    if request.method == 'POST':
        if datetime.date.today() > end and not COURSES_ALLOW_SUBMISSION_TO_PASSED_CHAPTERS:
            raise PermissionDenied(_("Chapter has already ended...") + " " + _("Submission is not allowed."))

        if len(user_submissions) == 1:
            submission = user_submissions[0]
        else:
            submission = Submission(chapter=chapter, run=run, author=request.user)

        form = SubmissionForm(request.POST, request.FILES, instance=submission)

        if form.is_valid():
            form.save()

            messages.success(request, _('Your submission has been saved.'))
            return redirect('chapter_submission', run_slug=run_slug, chapter_slug=chapter_slug)
    else:
        if datetime.date.today() > end and not COURSES_ALLOW_SUBMISSION_TO_PASSED_CHAPTERS:
            context['user_submissions'] = user_submissions
            form = None
        elif len(user_submissions) == 1:
            submission = user_submissions[0]
            form = SubmissionForm(instance=submission)
        else:
            form = SubmissionForm()

    context['form'] = form

    return render(request, 'courses/chapter_submission.html', context)


@login_required
def subscribe_to_run(request, run_slug):
    run = get_object_or_404(Run, slug=run_slug)
    run.users.add(request.user)
    run.save()

    messages.success(request, _('You have been subscribed to course: %s' % run))
    return redirect('course_run_detail', run_slug=run_slug)


@login_required
def unsubscribe_from_run(request, run_slug):
    run = get_object_or_404(Run, slug=run_slug)
    run.users.remove(request.user)
    run.save()

    messages.success(request, _('You have been unsubscribed from course: %s' % run))
    return redirect('course_run_detail', run_slug=run_slug)


# @login_required
# def lecture_detail(request, course_id, lecture_id):
#     try:
#         course = Run.objects.get(pk=course_id)
#     except Run.DoesNotExist:
#         raise Http404("Question does not exist")
#     return render(request, 'courses/detail.html', {'course': course})
