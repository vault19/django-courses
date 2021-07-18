from django.contrib import admin
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.html import format_html

from courses.models import Courses, Curriculums, CurriculumDetails, Runs, Artefact, PeerReview, Certificates


class CoursesAdmin(admin.ModelAdmin):
    list_display = ("name", "state", "view_runs_link", "view_curriculums_link")

    def view_runs_link(self, obj):
        count = obj.runs_set.count()
        url = (
                reverse("admin:courses_runs_changelist")
                + "?"
                + urlencode({"courses__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Run(s)</a>', url, count)

    view_runs_link.short_description = "Runs"

    def view_curriculums_link(self, obj):
        count = obj.runs_set.count()
        url = (
                reverse("admin:courses_curriculums_changelist")
                + "?"
                + urlencode({"courses__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Curriculum(s)</a>', url, count)

    view_curriculums_link.short_description = "Curriculums"


class CurriculumsAdmin(admin.ModelAdmin):
    pass


class CurriculumDetailsAdmin(admin.ModelAdmin):
    pass


class RunsAdmin(admin.ModelAdmin):
    pass


class ArtefactAdmin(admin.ModelAdmin):
    pass


class PeerReviewAdmin(admin.ModelAdmin):
    pass


class CertificatesAdmin(admin.ModelAdmin):
    pass


admin.site.register(Courses, CoursesAdmin)
admin.site.register(Curriculums, CurriculumsAdmin)
admin.site.register(CurriculumDetails, CurriculumDetailsAdmin)
admin.site.register(Runs, RunsAdmin)
admin.site.register(Artefact, ArtefactAdmin)
admin.site.register(PeerReview, PeerReviewAdmin)
admin.site.register(Certificates, CertificatesAdmin)
