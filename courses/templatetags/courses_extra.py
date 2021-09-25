from datetime import date
from django import template
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _


from courses.models import Lecture, LECTURE_TYPE
from courses.settings import EXTENSION_VIDEO, EXTENSION_IMAGE

register = template.Library()


@register.filter
def get_run_dates(chapter, run):
    start, end = chapter.get_run_dates(run=run)
    return f"{start} - {end}"


@register.filter
def timedelta(value, arg=None):
    if not value:
        return ""

    if arg:
        cmp = arg
    else:
        cmp = date.today()

    if value > cmp:
        return _("unlocks in %(time)s") % {"time": timesince(cmp, value)}
    else:
        return _("%(time)s ago") % {"time": timesince(value, cmp)}


@register.filter
def subtract(value, arg):
    return value - arg


@register.filter
def is_subscribed(run, user):
    return run.is_subscribed(user)


@register.filter()
def lecture_type_icon(lecture_type):
    icon = ""

    if lecture_type == LECTURE_TYPE[0][0]:
        icon = '<i class="fas fa-film"></i>'
    elif lecture_type == LECTURE_TYPE[1][0]:
        icon = '<i class="fas fa-file-alt"></i>'
    elif lecture_type == LECTURE_TYPE[2][0]:
        icon = '<i class="fas fa-users"></i><i class="fas fa-tasks"></i>'
    elif lecture_type == LECTURE_TYPE[3][0]:
        icon = '<i class="fab fa-python"></i>'
    elif lecture_type == LECTURE_TYPE[4][0]:
        icon = '<i class="fas fa-tasks"></i>'
    elif lecture_type == LECTURE_TYPE[5][0]:
        icon = '<i class="fas fa-phone"></i>'

    return mark_safe(icon)


@register.filter
def is_pdf(data):
    return Lecture.check_file_extension(data, alloed_extensions=("pdf",))


@register.filter
def is_image(data):
    return Lecture.check_file_extension(data, alloed_extensions=EXTENSION_IMAGE)


@register.filter
def is_video(data):
    return Lecture.check_file_extension(data, alloed_extensions=EXTENSION_VIDEO)
