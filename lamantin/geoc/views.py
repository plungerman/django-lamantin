# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.conf import settings
from django.shortcuts import render
from django.urls import reverse_lazy
from djauth.decorators import portal_auth_required
from lamantin.geoc.forms import CourseForm


@portal_auth_required(
    session_var='DJCHEKHOV_AUTH',
    redirect_url=reverse_lazy('access_denied'),
    group='carthageStaffStatus',
)
def course(request):
    """ """
    form = CourseForm()
    return render(request, 'geoc/form.html', {'form': form})
