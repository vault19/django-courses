from django.contrib import admin
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.html import format_html
from django import forms

from courses.models import Course, Chapter, Lecture, Run, Submission, Review, Certificate, Meeting


class ChapterInlineAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['previous'].queryset = self.instance.previous.all()


class ChapterInline(admin.TabularInline):
    model = Chapter
    # form = ChapterInlineAdminForm
    show_change_link = True
    extra = 0


class RunInline(admin.TabularInline):
    model = Run
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "state", "view_run_link", "view_chapter_link",)
    list_filter = ("state",)
    inlines = (RunInline, ChapterInline,)

    def view_run_link(self, obj):
        count = obj.run_set.count()
        url = (
                reverse("admin:courses_run_changelist")
                + "?"
                + urlencode({"courses__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Run(s)</a>', url, count)

    view_run_link.short_description = "Runs"

    def view_chapter_link(self, obj):
        count = obj.chapter_set.count()
        url = (
                reverse("admin:courses_chapter_changelist")
                + "?"
                + urlencode({"courses__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Chapter(s)</a>', url, count)

    view_chapter_link.short_description = "Chapter"


class LectureDetailInline(admin.TabularInline):
    model = Lecture
    extra = 1


class MeetingInlineForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(MeetingInlineForm, self).__init__(*args, **kwargs)

        # ToDo - Add filtering based on Course as well
        self.fields['lecture'].queryset = Lecture.objects.filter(lecture_type='L')


class MeetingDetailInline(admin.TabularInline):
    model = Meeting
    extra = 0
    form = MeetingInlineForm


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "length", "view_details_link")
    inlines = (LectureDetailInline,)

    def view_details_link(self, obj):
        count = obj.lecture_set.count()

        return format_html('{} Detail(s)', count)

    view_details_link.short_description = "Details"


class SubmissionInline(admin.TabularInline):
    model = Submission
    fields = ("lecture", "author", "title", "description", "data")
    readonly_fields = ("lecture", "author", "title", "description", "data")
    show_change_link = True
    can_delete = False
    extra = 0


@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "start", "end", "view_submissions_link")
    list_filter = ("start",)
    inlines = (SubmissionInline, MeetingDetailInline,)

    def view_submissions_link(self, obj):
        count = obj.submission_set.count()
        url = (
                reverse("admin:courses_submission_changelist")
                + "?"
                + urlencode({"run__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Submission(s)</a>', url, count)

    view_submissions_link.short_description = "Submissions"


class ReviewInline(admin.TabularInline):
    model = Review
    fields = ("author", "title", "description", "accepted")
    extra = 0


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "lecture", "run", "view_reviews_link")
    list_filter = ("run",)
    inlines = (ReviewInline,)

    def view_reviews_link(self, obj):
        count = obj.review_set.count()
        return format_html('{} Review(s)', count)

    view_reviews_link.short_description = "Reviews"


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    pass
