from django.contrib import admin
from courses.models import Courses, Curriculums, CurriculumDetails, Runs, Artefact, PeerReview, Certificates


class CoursesAdmin(admin.ModelAdmin):
    pass


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
