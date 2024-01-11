# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.urls import path
from lamantin.dashboard.designation import views


urlpatterns = [
    path(
        'outcome/<int:oid>/courses/',
        views.courses,
        name='courses',
    ),
    path('', views.home, name='designation_home'),
]
