import datetime

from django import template


register = template.Library()


@register.filter
def get_run_dates(chapter, run):
    start, end = chapter.get_run_dates(run=run)


    return f"{start} - {end}"
