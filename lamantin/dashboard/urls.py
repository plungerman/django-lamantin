# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.urls import path
from django.urls import include
from lamantin.dashboard import views


urlpatterns = [
    path(
        'course/<int:cid>/detail/',
        views.detail,
        name='detail',
    ),
    # delete Annotation object
    path(
        'course/annotation/<str:nid>/delete/',
        views.note_delete,
        name='note_delete',
    ),
    # delete course
    path(
        'course/<int:cid>/delete/',
        views.course_delete,
        name='course_delete',
    ),
    # course needs work
    path('course/<int:cid>/furbish/', views.furbish, name='furbish'),
    # phile upload
    path('course/phile/', views.phile_upload, name='phile_upload'),
    # manager course comments
    path('course/annotation/', views.annotation, name='annotation'),
    # course status view for 'approved'
    path('course/status/', views.status, name='status'),
    # course status view for 'approved'
    path('outcome/status/', views.outcome_status, name='outcome_status'),
    path('', views.home, name='dashboard_home'),
    # designations
    path('designation/', include('lamantin.dashboard.designation.urls')),
]
