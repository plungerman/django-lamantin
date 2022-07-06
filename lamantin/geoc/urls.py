# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.urls import path
from lamantin.geoc import views


urlpatterns = [
    path('', views.home, name='geoc_home'),
]
