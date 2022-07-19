# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.urls import path
from lamantin.dashboard import views


urlpatterns = [
    path(
        'search/',
        views.search, name='dashboard_search'
    ),
    path('', views.home, name='dashboard_home'),
]
