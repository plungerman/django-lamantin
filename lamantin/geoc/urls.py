# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.urls import path
from django.urls import reverse_lazy
from django.views.generic import RedirectView
from lamantin.geoc import views


urlpatterns = [
    path(
        'form/<int:cid>/update/',
        views.course_update,
        name='course_update',
    ),
    path('form/', views.course_create, name='course_create'),
    # home: redirect to dashboard
    path('', RedirectView.as_view(url=reverse_lazy('dashboard_home'))),
]
