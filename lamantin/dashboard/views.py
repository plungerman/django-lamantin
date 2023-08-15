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
from djtools.utils.mail import send_mail
from djtools.utils.users import in_group
from lamantin.geoc.forms import AnnotationForm
from lamantin.geoc.forms import DocumentRequiredForm
from lamantin.geoc.models import Annotation
from lamantin.geoc.models import Course
from lamantin.geoc.models import Outcome
from lamantin.geoc.models import OutcomeCourse


logger = logging.getLogger('debug_logfile')


@portal_auth_required(
    session_var='LAMANTIN_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def home(request):
    """GEOC dashboard."""
    user = request.user
    manager = in_group(user, settings.MANAGER_GROUP)
    courses = None
    show = None
    if manager:
        if request.POST:
            show = int(request.POST.get('show'))
            if show == 1:
                courses = Course.objects.filter(archive=True)
            else:
                if show:
                    courses = Course.objects.filter(outcome__id=show).filter(archive=False)
                else:
                    courses = Course.objects.filter(archive=False)
        else:
            courses = Course.objects.filter(archive=False)
    else:
        courses = Course.objects.filter(user=user).filter(archive=False)
    outcomes = Outcome.objects.filter(active=True)
    return render(
        request,
        'dashboard/home.html',
        {
            'courses': courses,
            'outcomes': outcomes,
            'manager': manager,
            'show': show,
        },
    )


def detail(request, cid):
    """View course details."""
    user = request.user
    course = Course.objects.get(pk=cid)
    perms = course.permissions(user)
    if course.user == user or perms:
        response = render(
            request,
            'dashboard/detail.html',
            {'course': course, 'perms': perms},
        )
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
def outcome_status(request):
    """Update the status of a course outcome."""
    if request.POST:
        oid = request.POST.get('oid')
        field = request.POST.get('field')
        status = request.POST.get('status')
        # simple data validation
        if field in {'approved', 'furbish'} and status in {'true', 'false'}:
            try:
                oc = OutcomeCourse.objects.get(pk=oid)
            except Exception:
                oc = None
            course = oc.course
            if oc:
                status = True
                if status == 'false':
                    status = False
                setattr(oc, field, status)
                oc.save()
                if course.outcomes_status(field):
                    setattr(course, field, True)
                    if field == 'furbish':
                        field = 'Needs Work'
                    message = 'All course outcomes have been set to "{0}".'.format(field)
                    course.save()
                else:
                    if field == 'furbish':
                        field = 'Needs Work'
                    message = "Course outcome status for {0} set to: {1}.".format(oc.outcome.name, field)
            else:
                message = "Could not find course outcome with that ID."
        else:
            message = "Invalid field or status."
    else:
        message = "Requires POST request."

    messages.add_message(
        request,
        messages.WARNING,
        message,
        extra_tags='alert-success',
    )

    return HttpResponse(message)


@portal_auth_required(
    session_var='LAMANTIN_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def furbish(request, cid):
    """Set the status on a course."""
    user = request.user
    course = get_object_or_404(Course, pk=cid)
    if request.POST:
        form = AnnotationForm(
            request.POST,
            use_required_attribute=settings.REQUIRED_ATTRIBUTE,
        )
        if form.is_valid():
            note = form.save(commit=False)
            note.course = course
            note.created_by = user
            note.updated_by = user
            note.save()
            note.tags.add('Furbish')
            course.furbish = True
            course.save()
            course.status = 'needs work'
            course.note = note
            bcc = [settings.MANAGERS[0][1]]
            to_list = [course.user.email]
            # set course outcomes values for 'approve' and 'furbish'.
            course.set_outcome('approve', False, None)
            course.set_outcome('furbish', True, None)
            for outcome in course.get_outcomes():
                outcome.furbish = True
                outcome.save()
            message = '''
                The status of course {0} ({1}) has been set to "needs more work"
                and we have sent an email to {2} {3} with your comments.
            '''.format(
                course.title,
                course.number,
                course.user.first_name,
                course.user.last_name,
            )
            messages.add_message(
                request,
                messages.WARNING,
                message,
                extra_tags='alert-success',
            )
            subject = '[GEOC] {0} ({1}) has been set to "needs more work"'.format(
                course.title,
                course.number,
            )
            if settings.DEBUG:
                course.to_list = to_list
                to_list = bcc
            recci = send_mail(
                request,
                to_list,
                subject,
                course.user.email,
                'geoc/email_status.html',
                course,
                bcc,
            )
            return HttpResponseRedirect(reverse_lazy('dashboard_home'))
    else:
        form = AnnotationForm(use_required_attribute=settings.REQUIRED_ATTRIBUTE)

    return render(
        request,
        'dashboard/furbish.html',
        {'course': course, 'form': form},
    )


@csrf_exempt
@portal_auth_required(
    group = settings.MANAGER_GROUP,
    session_var='LAMANTIN_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def status(request):
    """Set the status on a course."""
    user = request.user
    message = ""
    if request.POST:
        cid = request.POST.get('cid')
        try:
            cid = int(cid)
        except ValueError:
            return HttpResponse("Access Denied")
        course = get_object_or_404(Course, pk=cid)
        status = request.POST.get('status')
        if course.approved and status == 'approve':
            message = "{0} has already been approved".format(course)
        elif course.furbish and status == 'furbish':
            message = "{0} has already been flagged as needing more work".format(course, status)
        else:
            valid_status = [
                'approve',
                'archive',
                'furbish',
                'reopen',
                'unapprove',
                'unarchive',
            ]
            if status in valid_status:
                from djtools.fields import NOW
                if status == 'approve':
                    course.approved = True
                    course.approved_date = NOW
                    subject = message = "{0} ({1}) has been approved".format(
                        course.title,
                        course.number,
                    )
                    # approve each course outcome
                    course.set_outcome('approve', True, NOW)
                    course.set_outcome('furbish', False, None)
                if status == 'unapprove':
                    course.approved = False
                    course.approved_date = None
                    message = "{0} ({1}) has been changed from approved to un-approved".format(
                        course.title,
                        course.number,
                    )
                    # un-approve each course outcome
                    course.set_outcome('approve', False, None)
                    course.set_outcome('furbish', False, None)
                if status == 'reopen':
                    course.save_submit = False
                    course.furbish = False
                    subject = message = "{0} ({1}) has been reopened for updates".format(
                        course.title,
                        course.number,
                    )
                    # un-approve each course outcome
                    course.set_outcome('approve', False, None)
                    course.set_outcome('furbish', False, None)
                if status == 'archive':
                    course.archive = True
                    message = "{0} ({1}) has been archived".format(
                        course.title,
                        course.number,
                    )
                if status == 'unarchive':
                    course.archive = False
                    subject = message = "{0} ({1}) has been re-actived".format(
                        course.title,
                        course.number,
                    )
                messages.add_message(
                    request,
                    messages.WARNING,
                    message,
                    extra_tags='alert-success',
                )
                course.save()
                if status in ['approve', 'reopen', 'unarchive']:
                    course.status = status
                    bcc = [settings.MANAGERS[0][1]]
                    to_list = [course.user.email]
                    if status == 'approve':
                        to_list.append(settings.REGISTRAR_EMAIL)
                    if settings.DEBUG:
                        course.to_list = to_list
                        to_list = bcc
                    send_mail(
                        request,
                        to_list,
                        subject,
                        course.user.email,
                        'geoc/email_status.html',
                        course,
                        bcc,
                    )
            else:
                message = "Requires '{0}'".format(valid_status)
    else:
        message = "Requires POST request"

    return HttpResponse(message)


@portal_auth_required(
    session_var='LAMANTIN_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def course_delete(request, cid):
    """Delete a course form."""
    course = get_object_or_404(Course, pk=cid)
    user = request.user
    if course.user == user or user.is_superuser and not course.save_submit:
        course.delete()
        mtype = messages.SUCCESS
        extra_tags='alert-success'
        message = "Course was deleted"
    else:
        mtype = messages.WARNING
        extra_tags = 'alert-warning'
        message = "You do not have permission to delete this Course."
    messages.add_message(
        request,
        mtype,
        message,
        extra_tags=extra_tags,
    )
    return HttpResponseRedirect(reverse_lazy('dashboard_home'))


@portal_auth_required(
    group = settings.MANAGER_GROUP,
    session_var='LAMANTIN_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def note_delete(request, nid):
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


@portal_auth_required(
    session_var='LAMANTIN_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def phile_upload(request):
    """Upload a file for a course."""
    user = request.user
    message = None
    mtype = messages.WARNING
    extra_tags = 'alert-warning'
    if request.POST:
        cid = request.POST.get('cid')
        try:
            cid = int(cid)
        except ValueError:
            message = "Invalid course ID"
        if cid:
            course = get_object_or_404(Course, pk=cid)
            form = DocumentRequiredForm(
                request.POST,
                request.FILES,
                use_required_attribute=settings.REQUIRED_ATTRIBUTE,
            )

            if form.is_valid():
                doc = form.save(commit=False)
                doc.course = course
                doc.created_by = user
                doc.updated_by = user
                doc.save()
                message = "File uploaded successfully."
                mtype = messages.SUCCESS
                extra_tags = 'alert-success'
            else:
                message = "Upload failed. Please provide a valid file and description."
    else:
        message = "Requires POST."
    if message:
        messages.add_message(
            request,
            mtype,
            message,
            extra_tags=extra_tags,
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
        ctype = post.get('ctype')
        template = loader.get_template('dashboard/annotation.inc.html')
        if nid == 0:
            note = Annotation.objects.create(
                course=course,
                created_by=user,
                updated_by=user,
                body=body,
            )
            note.tags.add(ctype.capitalize())
            course.notes.add(note)
            context = {'note': note, 'bgcolor': 'bg-warning'}
            data['msg'] = template.render(context, request)
            if ctype == 'furbish':
                course.body = note.body
                bcc = [settings.MANAGERS[0][1]]
                to_list = [course.user.email]
                if settings.DEBUG:
                    course.to_list = to_list
                    to_list = bcc
                subject = message = "{0} ({1}): new comment from {2} {3}".format(
                    course.title,
                    course.number,
                    user.first_name,
                    user.last_name,
                )
                send_mail(
                    request,
                    to_list,
                    subject,
                    user.email,
                    'dashboard/email_note.html',
                    course,
                    bcc,
                )
        else:
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
    else:
        data['msg'] = "Requires AJAX POST request"

    return HttpResponse(
        json.dumps(data), content_type='application/json; charset=utf-8',
    )
