from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from courses.models import Chapter, Run
from courses.settings import (
    COURSES_ALLOW_SUBMISSION_TO_CHAPTERS,
    COURSES_ALLOW_SUBMISSION_TO_LECTURES,
    COURSES_DISPLAY_CHAPTER_DETAILS,
)


def get_run_chapter_context(request, run_slug, chapter_slug, raise_unsubscribed=True, raise_wrong_dates=True):
    run = get_object_or_404(Run, slug=run_slug)
    chapter = get_object_or_404(Chapter, slug=chapter_slug)

    if raise_unsubscribed:
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
