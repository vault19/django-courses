import datetime
import json

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from courses.models import Submission, Lecture
from courses.utils import get_run_chapter_context, array_merge
from courses.settings import (
    COURSES_ALLOW_SUBMISSION_TO_PASSED_CHAPTERS,
)


@login_required
def video_lecture_submission(request, run_slug, chapter_slug, lecture_slug):
    lecture = get_object_or_404(Lecture, slug=lecture_slug)
    context = get_run_chapter_context(request, run_slug, chapter_slug)

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

        # time range from one session is nicely merged with javascript
        data = json.loads(request.body)

        if not submission.metadata:
            submission.metadata = data
        elif "watched_video_time_range" in submission.metadata:
            submission.metadata["watched_video_time_range"] = array_merge(
                data["watched_video_time_range"] + submission.metadata["watched_video_time_range"]
            )
        else:
            submission.metadata["watched_video_time_range"] = data["watched_video_time_range"]

        submission.save()

        return HttpResponse('{"Data": "Saved"}', content_type="application/json")
    else:
        return HttpResponse('{"Data": "Not processed"}', content_type="application/json")
