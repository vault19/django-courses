from django.contrib import admin
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.html import format_html

from courses.models import Course, Curriculum, CurriculumDetail, Run, Artefact, Review, Certificate


class CurriculumInline(admin.TabularInline):
    model = Curriculum
    extra = 0


class RunInline(admin.TabularInline):
    model = Run
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "state", "view_run_link", "view_curriculum_link",)
    list_filter = ("state",)
    inlines = (RunInline, CurriculumInline,)

    def view_run_link(self, obj):
        count = obj.run_set.count()
        url = (
                reverse("admin:courses_run_changelist")
                + "?"
                + urlencode({"courses__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Run(s)</a>', url, count)

    view_run_link.short_description = "Runs"

    def view_curriculum_link(self, obj):
        count = obj.curriculum_set.count()
        url = (
                reverse("admin:courses_curriculum_changelist")
                + "?"
                + urlencode({"courses__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Curriculum(s)</a>', url, count)

    view_curriculum_link.short_description = "Curriculums"


class CurriculumDetailInline(admin.TabularInline):
    model = CurriculumDetail
    extra = 1


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "length", "view_details_link")
    inlines = (CurriculumDetailInline,)

    def view_details_link(self, obj):
        count = obj.curriculumdetail_set.count()

        return format_html('{} Detail(s)', count)

    view_details_link.short_description = "Details"


class ArtefactInline(admin.TabularInline):
    model = Artefact
    fields = ("curriculum", "author", "title", "description", "data")
    readonly_fields = ("curriculum", "author", "title", "description", "data")
    extra = 0


@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "start", "end", "view_artefacts_link")
    list_filter = ("start",)
    inlines = (ArtefactInline,)

    def view_artefacts_link(self, obj):
        count = obj.artefact_set.count()
        url = (
                reverse("admin:courses_artefact_changelist")
                + "?"
                + urlencode({"run__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Artefact(s)</a>', url, count)

    view_artefacts_link.short_description = "Artefacts"


class ReviewInline(admin.TabularInline):
    model = Review
    fields = ("author", "title", "description")
    readonly_fields = ("author", "title", "description")
    extra = 0


@admin.register(Artefact)
class ArtefactAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "curriculum", "run", "view_reviews_link")
    list_filter = ("run",)
    inlines = (ReviewInline,)

    def view_reviews_link(self, obj):
        count = obj.review_set.count()
        url = (
                reverse("admin:courses_review_changelist")
                + "?"
                + urlencode({"artefact__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Review(s)</a>', url, count)

    view_reviews_link.short_description = "Reviews"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("title", "artefact", "author")


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    pass
