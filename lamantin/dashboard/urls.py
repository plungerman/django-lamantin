# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.urls import path
from lamantin.dashboard import views


urlpatterns = [
    path(
        'course/<int:cid>/detail/',
        views.course_detail,
        name='course_detail',
    ),
    # delete Annotation object
    path(
        'course/annotation/<str:nid>/delete/',
        views.delete_note,
        name='delete_note',
    ),
    # manager course comments
    path('course/annotation/', views.annotation, name='annotation'),
    # course status view for 'approve' or 'decline' actions
    path('course/status/', views.course_status, name='course_status'),
    path('', views.home, name='dashboard_home'),
]
