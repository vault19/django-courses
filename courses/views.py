import datetime
from django.http import Http404
from django.shortcuts import render
from courses.models import Curriculum, Run


def index(request):
    course_runs = Run.objects.filter(course__state='O').filter(start__gt=datetime.datetime.today()).order_by('-start')
    context = {'course_runs': course_runs}

    return render(request, 'courses/index.html', context)


def course_run_detail(request, run_slug):
    try:
        run = Run.objects.get(slug=run_slug)
    except Run.DoesNotExist:
        raise Http404("Course does not exist...")
    return render(request, 'courses/run_detail.html', {'run': run})


def curriculum_detail(request, run_slug, curriculum_slug):
    try:
        curriculum = Curriculum.objects.get(slug=curriculum_slug)
    except Curriculum.DoesNotExist:
        raise Http404("Curriculum does not exist...")
    return render(request, 'courses/curriculum.html', {'curriculum': curriculum})


# def lecture_detail(request, course_id, lecture_id):
#     try:
#         course = Run.objects.get(pk=course_id)
#     except Run.DoesNotExist:
#         raise Http404("Question does not exist")
#     return render(request, 'courses/detail.html', {'course': course})
