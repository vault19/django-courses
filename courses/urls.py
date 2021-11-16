from django.urls import path

from .views import views
from .views import views_staff
from .views import views_ajax

urlpatterns = [
    path("", views.index, name="index"),
    path("courses/", views.courses, name="courses"),
    path("courses/open/", views.all_active_runs, name="all_active_runs"),
    path("courses/closed/", views.all_closed_runs, name="all_closed_runs"),
    path("courses/subscribed/", views.all_subscribed_active_runs, name="all_subscribed_active_runs"),
    path("courses/subscribed/closed/", views.all_subscribed_closed_runs, name="all_subscribed_closed_runs"),
    path("course/<str:course_slug>/details/", views.course_detail, name="course_detail"),
    path("course/<str:run_slug>/", views.course_run_detail, name="course_run_detail"),
    path("course/<str:run_slug>/subscribe/", views.subscribe_to_run, name="subscribe_to_run"),
    path("course/<str:run_slug>/unsubscribe/", views.unsubscribe_from_run, name="unsubscribe_from_run"),
    path("course/<str:run_slug>/<str:chapter_slug>/", views.chapter_detail, name="chapter_detail"),
    path("course/<str:run_slug>/<str:chapter_slug>/submission/", views.chapter_submission, name="chapter_submission"),
    path(
        "course/<str:run_slug>/<str:chapter_slug>/filter/<str:lecture_type>/",
        views.chapter_lecture_types,
        name="chapter_lecture_types",
    ),
    path("course/<str:run_slug>/<str:chapter_slug>/<str:lecture_slug>/", views.lecture_detail, name="lecture_detail"),
    path(
        "course/<str:run_slug>/<str:chapter_slug>/<str:lecture_slug>/video-duration/",
        views_ajax.video_lecture_duration,
        name="video_duration",
    ),
    path(
        "course/<str:run_slug>/<str:chapter_slug>/<str:lecture_slug>/video-ping/",
        views_ajax.video_lecture_submission,
        name="video_ping",
    ),
    path(
        "stuff/runs/",
        views_staff.runs,
        name="runs",
    ),
    path(
        "stuff/run/<str:run_slug>/attendees/",
        views_staff.run_attendees,
        name="run_attendees",
    ),
    path(
        "stuff/run/<str:run_slug>/attendee/<int:user_id>/",
        views_staff.run_attendee_submissions,
        name="run_attendee_submissions",
    ),
    path(
        "course/<str:run_slug>/<str:chapter_slug>/<str:lecture_slug>/submissions/",
        views_staff.lecture_submissions,
        name="lecture_submissions",
    ),
    path(
        "course/<str:run_slug>/<str:chapter_slug>/<str:lecture_slug>/submission/<int:submission_id>",
        views_staff.lecture_submission_review,
        name="lecture_submission_review",
    ),
    # path('<int:question_id>/results/', views.results, name='results'),
    # path('<int:question_id>/vote/', views.vote, name='vote'),
]
