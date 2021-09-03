from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from courses.models import Chapter, Run
from courses.settings import COURSES_ALLOW_SUBMISSION_TO_CHAPTERS, \
    COURSES_ALLOW_SUBMISSION_TO_LECTURES, COURSES_DISPLAY_CHAPTER_DETAILS


def get_run_chapter_context(request, run_slug, chapter_slug, raise_unsubscribed=True, raise_wrong_dates=True):
    run = get_object_or_404(Run, slug=run_slug)
    chapter = get_object_or_404(Chapter, slug=chapter_slug)

    if raise_unsubscribed:
        run.is_subscribed(request.user, raise_unsubscribed=raise_unsubscribed)

    start, end = chapter.get_run_dates(run=run, raise_wrong_dates=raise_wrong_dates)

    breadcrumbs = [
        {
            'url': reverse('courses'),
            'title': _('Courses'),
        },
        {
            'url': reverse('course_detail', args=(run.course.slug,)),
            'title': run.course.title,
        },
        {
            'url': reverse('course_run_detail', args=(run_slug,)),
            'title': run.title.upper(),
        },
        {
            'title': chapter.title,
        },
    ]

    context = {
        'run': run,
        'chapter': chapter,
        'lectures': chapter.lecture_set.all().order_by('order', 'title'),
        'start': start,
        'end': end,
        'subscribed': run.is_subscribed(request.user),
        'breadcrumbs': breadcrumbs,
        'COURSES_DISPLAY_CHAPTER_DETAILS': COURSES_DISPLAY_CHAPTER_DETAILS,
        'COURSES_ALLOW_SUBMISSION_TO_CHAPTERS': COURSES_ALLOW_SUBMISSION_TO_CHAPTERS,
        'COURSES_ALLOW_SUBMISSION_TO_LECTURES': COURSES_ALLOW_SUBMISSION_TO_LECTURES,
    }

    return context
