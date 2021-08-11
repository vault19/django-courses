from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='courses_index'),
    path('closed/', views.closed_runs, name='closed_runs'),
    path('course/<str:run_slug>/', views.course_run_detail, name='course_run_detail'),
    path('course/<str:run_slug>/subscribe/', views.subscribe_to_run, name='subscribe_to_run'),
    path('course/<str:run_slug>/unsubscribe/', views.unsubscribe_from_run, name='unsubscribe_from_run'),
    path('course/<str:run_slug>/<str:chapter_slug>/', views.chapter_detail, name='chapter_detail'),
    path('course/<str:run_slug>/<str:chapter_slug>/submission/', views.chapter_submission, name='chapter_submission'),
    # path('course/<str:run_slug>/<str:curriculum_slug>/<int:lecture_id>/', views.lecture_detail, name='lecture_detail'),

    # path('<int:question_id>/results/', views.results, name='results'),
    # path('<int:question_id>/vote/', views.vote, name='vote'),
]