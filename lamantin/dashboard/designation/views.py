# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse_lazy
from djauth.decorators import portal_auth_required
from lamantin.geoc.models import Course
from lamantin.geoc.models import Outcome


@portal_auth_required(
    group=settings.MANAGER_GROUP,
    session_var='LAMANTIN_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def home(request):
    """GEOC dashboard for designations."""
    outcomes = Outcome.objects.all()
    courses = Course.objects.all()
    confirmed = 0
    provisional = 0
    for course in courses:
        if course.status == 'Confirmed':
            confirmed += 1
        else:
            provisional += 1
    return render(
        request,
        'dashboard/designation/home.html',
        {
            'outcomes': outcomes,
            'courses': courses,
            'confirmed': confirmed,
            'provisional': provisional,
        },
    )


@portal_auth_required(
    group=settings.MANAGER_GROUP,
    session_var='LAMANTIN_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def courses(request, oid):
    """GEOC courses for a given student learning outcome."""
    outcome = get_object_or_404(Outcome, pk=oid)
    courses = Course.objects.filter(outcome__id=oid)
    confirmed = 0
    percent = 0
    for course in courses:
        if course.status == 'Confirmed':
            confirmed += 1
    if courses.count() > 0:
        percent = round(confirmed / courses.count() * 100, 2)
    return render(
        request,
        'dashboard/designation/courses.html',
        {
            'courses': courses,
            'outcome': outcome,
            'confirmed': confirmed,
            'percent': percent,
        },
    )
