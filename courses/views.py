import datetime

from django.db.models import Q
from django.http import Http404
from django.shortcuts import render

from courses.models import Chapter, Run


def index(request):
    course_runs = Run.objects\
        .filter(course__state='O')\
        .filter(Q(end__gte=datetime.datetime.today()) | Q(end=None))\
        .order_by('-start')
    context = {'course_runs': course_runs}

    return render(request, 'courses/index.html', context)


def course_run_detail(request, run_slug):
    try:
        run = Run.objects.get(slug=run_slug)
    except Run.DoesNotExist:
        raise Http404("Course does not exist...")
    return render(request, 'courses/run_detail.html', {'run': run})


def chapter_detail(request, run_slug, chapter_slug):
    try:
        chapter = Chapter.objects.get(slug=chapter_slug)
    except Chapter.DoesNotExist:
        raise Http404("Chapter does not exist...")
    return render(request, 'courses/chapter.html', {'chapter': chapter})


# def lecture_detail(request, course_id, lecture_id):
#     try:
#         course = Run.objects.get(pk=course_id)
#     except Run.DoesNotExist:
#         raise Http404("Question does not exist")
#     return render(request, 'courses/detail.html', {'course': course})
