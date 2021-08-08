import datetime

from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _


from courses.models import Chapter, Run
from courses.settings import COURSES_SHOW_FUTURE_CHAPTERS, COURSES_ALLOW_ACCESS_TO_PASSED_CHAPTERS


def index(request):
    course_runs = Run.objects\
        .filter(course__state='O')\
        .filter(Q(end__gte=datetime.datetime.today()) | Q(end=None))\
        .order_by('-start')
    context = {'course_runs': course_runs}

    return render(request, 'courses/index.html', context)


def closed_runs(request):
    course_runs = Run.objects \
        .filter(Q(course__state='O') | Q(course__state='C')) \
        .filter(Q(end__lt=datetime.datetime.today())) \
        .order_by('-start')
    context = {'course_runs': course_runs}

    return render(request, 'courses/index.html', context)


def course_run_detail(request, run_slug):
    try:
        run = Run.objects.get(slug=run_slug)
    except Run.DoesNotExist:
        raise Http404(_("Course does not exist..."))

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


def chapter_detail(request, run_slug, chapter_slug):
    try:
        run = Run.objects.get(slug=run_slug)
    except Run.DoesNotExist:
        raise Http404(_("Course does not exist..."))

    try:
        chapter = Chapter.objects.get(slug=chapter_slug)
    except Chapter.DoesNotExist:
        raise Http404(_("Chapter does not exist..."))

    start, end = chapter.get_run_dates(run=run)

    context = {'chapter': chapter, 'start': start, 'end': end}

    if datetime.date.today() > end:
        if COURSES_ALLOW_ACCESS_TO_PASSED_CHAPTERS:
            context['alert'] = {"severity": "warning", "message": _("Chapter has already ended...")}
        else:
            raise Http404(_("Chapter has already ended...") + " " + _("Sorry it is not available any more."))

    if datetime.date.today() < start:
        raise Http404(_("Chapter hasnt started yet...") + " " + _("Please come back later."))

    return render(request, 'courses/chapter.html', context)


# def lecture_detail(request, course_id, lecture_id):
#     try:
#         course = Run.objects.get(pk=course_id)
#     except Run.DoesNotExist:
#         raise Http404("Question does not exist")
#     return render(request, 'courses/detail.html', {'course': course})
