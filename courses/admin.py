from django.contrib import admin
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.html import format_html
from django import forms

from courses.models import Course, Chapter, Lecture, Run, RunUsers, Submission, Review, Certificate, Meeting


class ChapterInlineAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.id:
            self.fields["previous"].queryset = Chapter.objects.filter(course=self.instance.course)


class ChapterInline(admin.StackedInline):
    model = Chapter
    form = ChapterInlineAdminForm
    show_change_link = True
    extra = 0
    # autocomplete_fields = ['previous']  # Creates select2, but does not respect form queryset filter!
    classes = ["collapse"]


class RunInline(admin.TabularInline):
    model = Run
    extra = 0
    autocomplete_fields = ["manager"]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "state",
        "view_run_link",
        "view_chapter_link",
    )
    list_filter = ("state",)
    search_fields = ["title"]
    autocomplete_fields = ["creator"]
    inlines = (
        ChapterInline,
        RunInline,
    )

    def view_run_link(self, obj):
        count = obj.run_set.count()
        url = reverse("admin:courses_run_changelist") + "?" + urlencode({"course__id__exact": f"{obj.id}"})
        return format_html('<a href="{}">{} Run(s)</a>', url, count)

    view_run_link.short_description = "Runs"

    def view_chapter_link(self, obj):
        count = obj.chapter_set.count()
        url = reverse("admin:courses_chapter_changelist") + "?" + urlencode({"course__id__exact": f"{obj.id}"})
        return format_html('<a href="{}">{} Chapter(s)</a>', url, count)

    view_chapter_link.short_description = "Chapter"

    def get_changeform_initial_data(self, request):
        get_data = super().get_changeform_initial_data(request)
        get_data["creator"] = request.user.pk

        return get_data


class LectureDetailInline(admin.StackedInline):
    model = Lecture
    extra = 1


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "length", "view_lectures_link")
    list_filter = ("course",)
    search_fields = ["title"]
    inlines = (LectureDetailInline,)

    def render_change_form(self, request, context, *args, **kwargs):
        context["adminform"].form.fields["previous"].queryset = Chapter.objects.filter(course=kwargs["obj"].course)
        return super().render_change_form(request, context, *args, **kwargs)

    def view_lectures_link(self, obj):
        count = obj.lecture_set.count()
        return format_html("{} Lecture(s)", count)

    view_lectures_link.short_description = "Lectures"


class SubmissionInline(admin.TabularInline):
    model = Submission
    fields = ("lecture", "author", "title", "description", "data", "metadata", "timestamp_added", "timestamp_modified")
    readonly_fields = (
        "lecture",
        "author",
        "title",
        "description",
        "data",
        "metadata",
        "timestamp_added",
        "timestamp_modified",
    )
    show_change_link = False
    can_delete = False
    can_add = False
    extra = 0
    classes = ["collapse"]


class MeetingInlineAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.id:
            self.fields["lecture"].queryset = Lecture.objects.filter(lecture_type="L").filter(
                chapter__course=self.instance.run.course
            )


class MeetingDetailInline(admin.StackedInline):
    model = Meeting
    extra = 0
    autocomplete_fields = ["leader", "organizer"]
    classes = ["collapse"]
    form = MeetingInlineAdminForm


class RunUsersDetailInline(admin.TabularInline):
    model = RunUsers
    extra = 2
    readonly_fields = ["timestamp_added", "timestamp_modified"]
    autocomplete_fields = ["user"]
    classes = ["collapse"]


@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "start", "end", "view_users_link", "view_submissions_link")
    list_filter = ("start", "manager", "course")
    search_fields = ["title"]
    autocomplete_fields = ["manager"]
    readonly_fields = ("end",)
    inlines = (
        MeetingDetailInline,
        RunUsersDetailInline,
        SubmissionInline,
    )

    def view_submissions_link(self, obj):
        count = obj.submission_set.count()
        url = reverse("admin:courses_submission_changelist") + "?" + urlencode({"run__id__exact": f"{obj.id}"})
        return format_html('<a href="{}">{} Submission(s)</a>', url, count)

    view_submissions_link.short_description = "Submissions"

    def view_users_link(self, obj):
        count = obj.users.count()
        return format_html("{} User(s)", count)

    view_users_link.short_description = "Users"

    def get_changeform_initial_data(self, request):
        get_data = super().get_changeform_initial_data(request)
        get_data["manager"] = request.user.pk

        return get_data


class ReviewInline(admin.TabularInline):
    model = Review
    fields = ("author", "title", "description", "accepted", "timestamp_added", "timestamp_modified")
    readonly_fields = ["timestamp_added", "timestamp_modified"]
    extra = 0


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("author", "title", "lecture", "run", "view_reviews_link")
    list_filter = ("run",)
    search_fields = ["title"]
    readonly_fields = ["timestamp_added", "timestamp_modified"]
    inlines = (ReviewInline,)

    def render_change_form(self, request, context, *args, **kwargs):
        submission = kwargs["obj"]

        context["adminform"].form.fields["chapter"].queryset = Chapter.objects.filter(course=submission.run.course)

        if submission.chapter:
            context["adminform"].form.fields["lecture"].queryset = Lecture.objects.filter(chapter=submission.chapter)
        else:
            context["adminform"].form.fields["lecture"].queryset = Lecture.objects.filter(
                chapter__chapter__course=submission.run.course
            )

        return super().render_change_form(request, context, *args, **kwargs)

    def view_reviews_link(self, obj):
        count = obj.review_set.count()
        return format_html("{} Review(s)", count)

    view_reviews_link.short_description = "Reviews"


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    pass
