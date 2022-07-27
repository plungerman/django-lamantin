# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from djauth.decorators import portal_auth_required
from djtools.utils.users import in_group
from lamantin.geoc.models import Course


@portal_auth_required(
    session_var='LAMANTIN_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def home(request):
    """GEOC dashboard."""
    user = request.user
    group = in_group(user, settings.MANAGER_GROUP)
    if group:
        courses = Course.objects.all()
    else:
        courses = Course.objects.filter(user=user)
    return render(request, 'dashboard/home.html', {'courses': courses})


def course_detail(request, cid):
    """View course details."""
    user = request.user
    group = in_group(user, settings.MANAGER_GROUP)
    course = Course.objects.get(pk=cid)
    if course.user == user or group:
        response = render(request, 'dashboard/detail.html', {'course': course})
    else:
        messages.add_message(
            request,
            messages.WARNING,
            "The course you attempted to edit is unavailable.",
            extra_tags='alert-warning',
        )
        response = HttpResponseRedirect(reverse_lazy('dashboard_home'))
    return response
