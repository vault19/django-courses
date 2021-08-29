from django import template
from django.utils.safestring import mark_safe

from courses.models import LECTURE_TYPE

register = template.Library()


@register.filter
def get_run_dates(chapter, run):
    start, end = chapter.get_run_dates(run=run)
    return f"{start} - {end}"


@register.filter
def is_subscribed(run, user):
    return run.is_subscribed(user)


@register.filter()
def lecture_type_icon(lecture_type):
    icon = ''

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
