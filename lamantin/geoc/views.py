# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.conf import settings
from django.shortcuts import render
from lamantin.geoc.forms import CourseForm


def home(request):
    """Dashboard home."""
    return render(
        request, 'geoc/home.html', {'foobar': settings.FOO_BAR},
    )


def courses(request):
    """ """
    form = CourseForm()
    return render(
        request, 'geoc/form.html', {'form': form}
    )
