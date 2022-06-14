# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.conf import settings
from django.shortcuts import render


def home(request):
    """Application home."""
    return render(
        request, 'index.html', {'foobar': settings.FOO_BAR},
    )
