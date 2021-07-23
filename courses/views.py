import datetime
from django.http import Http404
from django.shortcuts import render
from courses.models import Run


def index(request):
    courses_list = Run.objects.filter(course__state='O').filter(start__gt=datetime.datetime.today()).order_by('-start')
    context = {'courses_list': courses_list}

    return render(request, 'courses/index.html', context)


def detail(request, id):
    try:
        course = Run.objects.get(pk=id)
    except Run.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'courses/detail.html', {'course': course})
