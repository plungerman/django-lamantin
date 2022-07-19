# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.conf import settings
from django.shortcuts import render
from django.urls import reverse_lazy
from djauth.decorators import portal_auth_required
from lamantin.geoc.models import Course


@portal_auth_required(
    session_var='DJCHEKHOV_AUTH',
    redirect_url=reverse_lazy('access_denied'),
    group='carthageStaffStatus',
)
def home(request):
    """GEOC dashboard."""
    courses = Course.objects.all()
    return render(request, 'dashboard/home.html', {'courses': courses})


def search(request):
    """Dashboard search."""
    return render(
        request, 'dashboard/search.html', {}
    )
