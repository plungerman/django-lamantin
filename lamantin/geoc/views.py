# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.conf import settings
from django.shortcuts import render
from lamantin.geoc.forms import CourseForm


def home(request):
    """GEOC dashboard."""
    return render(
        request, 'geoc/home.html', {},
    )


def courses(request):
    """ """
    form = CourseForm()
    return render(
        request, 'geoc/form.html', {'form': form}
    )
