import datetime

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from courses.models import Chapter, Run
from courses.settings import COURSES_ALLOW_ACCESS_TO_PASSED_CHAPTERS, COURSES_ALLOW_SUBMISSION_TO_PASSED_CHAPTERS
from django.utils.translation import ugettext_lazy as _


def get_run_chapter(run_slug, chapter_slug):
    run = get_object_or_404(Run, slug=run_slug)
    chapter = get_object_or_404(Chapter, slug=chapter_slug)

    return run, chapter


def verify_course_dates(start, end, context):
    if datetime.date.today() > end:
        if COURSES_ALLOW_ACCESS_TO_PASSED_CHAPTERS:
            context['alert'] = {"severity": "warning", "message": _("Chapter has already ended...")}
        else:
            raise PermissionDenied(_("Chapter has already ended...") + " " + _("Sorry it is not available any more."))

    if datetime.date.today() < start:
        raise PermissionDenied(_("Chapter hasnt started yet...") + " " + _("Please come back later."))
