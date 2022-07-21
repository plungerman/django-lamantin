# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from djauth.decorators import portal_auth_required
from lamantin.geoc.forms import CourseForm
from lamantin.geoc.models import Course


@portal_auth_required(
    session_var='DJCHEKHOV_AUTH',
    redirect_url=reverse_lazy('access_denied'),
    group='carthageStaffStatus',
)
def course_form(request, step='course', cid=None):
    """GEOC workflow form. """
    course = None
    template = 'geoc/form_{0}.html'.format(step)
    if cid:
        course = Course.objects.get(pk=cid)
    if request.method == 'POST':
        form = CourseForm(
            request.POST,
            instance=course,
            use_required_attribute=settings.REQUIRED_ATTRIBUTE,
        )
        if form.is_valid():
            user = request.user
            course = form.save(commit=False)
            course.user = user
            course.updated_by = user
            course.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                "Step 1 is complete. Please complete the outcomes below.",
                extra_tags='alert-success',
            )
            return HttpResponseRedirect(
                reverse_lazy('course_update', args=['outcome', course.id]),
            )
    else:
        if step == 'course':
            form = CourseForm(
                instance=course,
                use_required_attribute=settings.REQUIRED_ATTRIBUTE,
            )
        else:
            form = []
    return render(
        request,
        template,
        {'form': form, 'step': step, 'course': course},
    )
