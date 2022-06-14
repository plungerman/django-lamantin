# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.conf import settings
from django.shortcuts import render


def home(request):
    """Dashboard home."""
    return render(
        request, 'dashboard/home.html', {'foobar': settings.FOO_BAR},
    )


def search(request):
    """Dashboard search."""
    return render(
        request, 'dashboard/search.html', {}
    )
