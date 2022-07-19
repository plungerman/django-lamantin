# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.urls import path
from django.urls import reverse_lazy
from django.views.generic import RedirectView
from lamantin.geoc import views


urlpatterns = [
    path('form/', views.course, name='course'),
    # home: redirect to dashboard
    path('', RedirectView.as_view(url=reverse_lazy('course'))),
]
