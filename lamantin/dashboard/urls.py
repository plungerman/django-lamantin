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
    path('', views.home, name='dashboard_home'),
]
