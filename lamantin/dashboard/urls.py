# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.urls import path
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
        views.delete_note,
        name='delete_note',
    ),
    # course needs work
    path('course/<int:cid>/furbish/', views.furbish, name='furbish'),
    # phile upload
    path('course/phile/', views.phile_upload, name='phile_upload'),
    # manager course comments
    path('course/annotation/', views.annotation, name='annotation'),
    # course status view for 'approved'
    path('course/status/', views.status, name='status'),
    path('', views.home, name='dashboard_home'),
]
