# -*- coding: utf-8 -*-

"""URLs for all views."""

import json
import logging

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template import loader
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from djauth.decorators import portal_auth_required
from djtools.utils.users import in_group
from lamantin.geoc.models import Annotation
from lamantin.geoc.models import Course


logger = logging.getLogger('debug_logfile')


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


@csrf_exempt
@portal_auth_required(
    session_var='LAMANTIN_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def course_status(request):
    """Set the status on a proposal."""
    user = request.user
    if request.POST:
        cid = request.POST.get('cid')
        try:
            cid = int(cid)
        except ValueError:
            return HttpResponse("Access Denied")
        course = get_object_or_404(Course, pk=cid)
        status = request.POST.get('status')
        if course.declined or course.approved:
            message = "{0} has already been {1}".format(course, status)
        else:
            if status in ['approved', 'declined']:
                from djtools.fields import NOW
                if status == 'approved':
                    course.approved = True
                    course.approved_date = NOW
                if status == 'declined':
                    course.declined = True
                    course.declined_date = NOW
                course.save()
                message = "Course has been {0}".format(status)
            else:
                message = "Requires 'declined' or 'approved'"
    else:
        message = "Requires POST request"

    return HttpResponse(message)


@portal_auth_required(
    group = settings.MANAGER_GROUP,
    session_var='LAMANTIN_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def delete_note(request, nid):
    """Delete a comment form an Alert."""
    note = get_object_or_404(Annotation, pk=nid)
    note.delete()
    messages.add_message(
        request,
        messages.SUCCESS,
        "Comment was deleted",
        extra_tags='alert-success',
    )
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@csrf_exempt
@portal_auth_required(
    group = settings.MANAGER_GROUP,
    session_var='LAMANTIN_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def annotation(request):
    """Manage annotations for a course on the detail view via ajax post."""
    user = request.user
    data =  {'msg': "Success", 'id': ''}
    if request.is_ajax() and request.method == 'POST':
        post = request.POST
        # simple error handling to prevent malicious values
        try:
            nid = int(post.get('nid'))
            cid = int(post.get('cid'))
        except:
            return HttpResponse("Invalid course or annotation ID")
        course = get_object_or_404(Course, pk=cid)
        note = None
        body = post.get('value')
        action = post.get('action')
        template = loader.get_template('dashboard/annotation.inc.html')
        logger.debug('course: {0}'.format(course));
        if nid == 0:
            note = Annotation.objects.create(
                course=course,
                created_by=user,
                updated_by=user,
                body=body,
                tags='Comments',
            )
            course.notes.add(note)
            context = {'note': note, 'bgcolor': 'bg-warning'}
            data['msg'] = template.render(context, request)
        else:
            try:
                note = Annotation.objects.get(pk=nid)
                if action == 'fetch':
                    data['msg'] = note.body
                elif action == 'delete':
                    note.delete()
                else:
                    note.body=body
                    note.updated_by = user
                    note.save()
                    context = {'note': note, 'bgcolor': 'bg-warning'}
                    data['msg'] = template.render(context, request)
                data['id'] = note.id
            except:
                data['msg'] = "Follow-up not found"
    else:
        data['msg'] = "Requires AJAX POST request"

    return HttpResponse(
        json.dumps(data), content_type='application/json; charset=utf-8',
    )
