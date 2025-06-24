# -*- coding: utf-8 -*-

"""URLs for all views."""

import copy

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse_lazy
from djtools.utils.mail import send_mail
from lamantin.geoc.forms import AnnotationForm
from lamantin.geoc.forms import CourseForm
from lamantin.geoc.forms import CourseOutcomeForm
from lamantin.geoc.forms import DocumentForm
from lamantin.geoc.models import Course


@login_required
def course_create(request):
    """GEOC workflow form to create a course."""
    if request.method == 'POST':
        user = request.user
        post = request.POST
        form = CourseForm(
            post,
            use_required_attribute=settings.REQUIRED_ATTRIBUTE,
        )
        form_syllabus = DocumentForm(
            post,
            request.FILES,
            use_required_attribute=settings.REQUIRED_ATTRIBUTE,
            prefix='syllabus',
        )
        if form.is_valid() and form_syllabus.is_valid():
            course = form.save(commit=False)
            course.user = user
            course.updated_by = user
            course.save()
            form.save_m2m()
            # document syllabus
            doc = form_syllabus.save(commit=False)
            doc.course = course
            if not doc.name:
                doc.name = 'Syllabus: {0} ({1})'.format(course.title, course.number)
            doc.created_by = user
            doc.updated_by = user
            doc.save()
            doc.tags.add('Syllabus')
            if course.multipass:
                crosslist_dict = {
                    'crosslist1': request.POST.get('crosslist1'),
                    'crosslist2': request.POST.get('crosslist2'),
                    'crosslist3': request.POST.get('crosslist3'),
                    'crosslist4': request.POST.get('crosslist4'),
                }
                slos = course.outcome.all()
                for key, value in crosslist_dict.items():
                    if value:
                        #course.pk = None
                        #course._state.adding = True
                        #course.number = value
                        #course.save()
                        #course.outcome.set(slos)
                        crosslist = copy.deepcopy(course)
                        crosslist.id = None
                        crosslist.number = value
                        crosslist.save()
                        crosslist.outcome.set(slos)
                        course.cross_listing.add(crosslist)
                        # doc
                        doc.pk = None
                        doc.course = crosslist
                        doc._state.adding = True
                        doc.save()
                        doc.tags.add('Syllabus')
            messages.add_message(
                request,
                messages.SUCCESS,
                "Step 1 is complete. Please complete the outcomes below.",
                extra_tags='alert-success',
            )
            return HttpResponseRedirect(
                reverse_lazy('outcome_form', args=[course.id,]),
            )
    else:
        form = CourseForm(
            use_required_attribute=settings.REQUIRED_ATTRIBUTE,
        )
        form_syllabus = DocumentForm(
            use_required_attribute=settings.REQUIRED_ATTRIBUTE,
            prefix='syllabus',
        )
    return render(
        request,
        'geoc/form_course.html',
        {
            'form': form,
            'form_syllabus': form_syllabus,
        },
    )


@login_required
def course_update(request, cid):
    """GEOC workflow form to update a course."""
    course = get_object_or_404(Course, pk=cid)
    syllabus = None
    user = request.user
    if course.save_submit:
        messages.add_message(
            request,
            messages.WARNING,
            """
                The course you attempted to edit is complete.
                The GEOC committe will review your course and report back to you presently.
            """,
            extra_tags='alert-warning',
        )
        return HttpResponseRedirect(reverse_lazy('dashboard_home'))
    elif user != course.user:
        messages.add_message(
            request,
            messages.WARNING,
            "The course you attempted to edit is unavailable.",
            extra_tags='alert-warning',
        )
        return HttpResponseRedirect(reverse_lazy('dashboard_home'))

    if not course.parent():
        messages.add_message(
            request,
            messages.WARNING,
            """
                The course you attempted to edit is a crosslisted course and cannot be edited.
                Update the parent course instead.
            """,
            extra_tags='alert-warning',
        )
        return HttpResponseRedirect(reverse_lazy('dashboard_home'))

    if course.syllabus():
        syllabus = course.syllabus()

    if request.method == 'POST':
        post = request.POST
        form = CourseForm(
            post,
            instance=course,
            use_required_attribute=settings.REQUIRED_ATTRIBUTE,
        )
        form_syllabus = DocumentForm(
            post,
            request.FILES,
            instance=syllabus,
            use_required_attribute=settings.REQUIRED_ATTRIBUTE,
            prefix='syllabus',
        )
        if form.is_valid() and form_syllabus.is_valid():
            course = form.save(commit=False)
            course.user = user
            course.updated_by = user
            course.save()
            form.save_m2m()
            # document syllabus
            doc = form_syllabus.save(commit=False)
            doc.course = course
            if not doc.name:
                doc.name = 'Syllabus: {0} ({1})'.format(course.title, course.number)
            doc.created_by = user
            doc.updated_by = user
            doc.save()
            doc.tags.add('Syllabus')
            if course.multipass:
                # obtain the SLOs from the parent course
                slos = course.outcome.all()
                # crosslist course
                crosslist_dict = {
                    'crosslist1': request.POST.get('crosslist1'),
                    'crosslist2': request.POST.get('crosslist2'),
                    'crosslist3': request.POST.get('crosslist3'),
                    'crosslist4': request.POST.get('crosslist4'),
                }
                # remove all crosslisted courses first
                for cl in course.cross_listing.all():
                    cl.delete()
                # recreate all crosslisted courses
                for key, value in crosslist_dict.items():
                    if value:
                        crosslist = copy.deepcopy(course)
                        crosslist.id = None
                        crosslist.number = value
                        crosslist.save()
                        # add the SLOs from parent to child
                        crosslist.outcome.set(slos)
                        course.cross_listing.add(crosslist)
                        # doc
                        doc.pk = None
                        doc.course = crosslist
                        doc._state.adding = True
                        doc.save()
                        doc.tags.add('Syllabus')
            messages.add_message(
                request,
                messages.SUCCESS,
                "Step 1 is complete. Please complete the outcomes below.",
                extra_tags='alert-success',
            )
            return HttpResponseRedirect(
                reverse_lazy('outcome_form', args=[course.id,]),
            )
        else:
            messages.add_message(
                request,
                messages.WARNING,
                "Step 1 failed. Please try again.",
                extra_tags='alert-warning',
            )
    else:
        form = CourseForm(
            instance=course,
            use_required_attribute=settings.REQUIRED_ATTRIBUTE,
        )
        form_syllabus = DocumentForm(
            instance=syllabus,
            use_required_attribute=settings.REQUIRED_ATTRIBUTE,
            prefix='syllabus',
        )
    return render(
        request,
        'geoc/form_course.html',
        {
            'form': form,
            'course': course,
            'form_syllabus': form_syllabus,
        },
    )


@login_required
def outcome_form(request, cid):
    """GEOC workflow form to update a course."""
    forms_dict = {}
    errors = False
    user = request.user
    form_note = None
    adendum = None
    phile = None
    course = get_object_or_404(Course, pk=cid)
    adendum = course.notes.filter(tags__name__in=['Adenda']).first()
    form_note = AnnotationForm(
        instance=adendum,
        use_required_attribute=settings.REQUIRED_ATTRIBUTE,
    )
    if course.save_submit:
        messages.add_message(
            request,
            messages.WARNING,
            """
                The course you attempted to edit is complete.
                The GEOC committe will review your course and report back to you presently.
            """,
            extra_tags='alert-warning',
        )
        return HttpResponseRedirect(reverse_lazy('dashboard_home'))
    elif user != course.user:
        messages.add_message(
            request,
            messages.WARNING,
            "The course you attempted to edit is unavailable.",
            extra_tags='alert-warning',
        )
        return HttpResponseRedirect(reverse_lazy('dashboard_home'))

    if request.method == 'POST':
        post = request.POST
        # SLOs
        for outcome in course.outcome.all():
            if outcome.active:
                forms = []
                for element in outcome.elements.all():
                    slo = element.slo.get(course=course)
                    form = CourseOutcomeForm(
                        post,
                        request=request,
                        prefix='slo{0}'.format(slo.id),
                        instance=slo,
                    )
                    if form.is_valid():
                        form.save()
                    else:
                        errors = True
                    # do we need this?
                    forms.append(form)
                forms_dict[outcome.get_form()] = forms
        # note
        form_note = AnnotationForm(
            post,
            instance=adendum,
            use_required_attribute=settings.REQUIRED_ATTRIBUTE,
        )
        if adendum:
            note = form_note.save()
        elif form_note.is_valid():
            note = form_note.save(commit=False)
            note.course = course
            note.created_by = user
            note.updated_by = user
            note.save()
            note.tags.add('Adenda')
        # update crosslisted courses if need be:
        if not errors and course.multipass:
            # comments
            for cl in course.cross_listing.all():
                cl_note = copy.deepcopy(note)
                cl_note.id = None
                cl_note.course = cl
                cl_note.save()
                cl_note.tags.add('Adenda')
            # SLOs
            for outcome in course.outcomes.all():
                for cl in course.cross_listing.all():
                    for cl_outcome in cl.outcomes.filter(slo=outcome.slo):
                        cl_outcome.description = outcome.description
                        cl_outcome.save()

        if not errors and post.get('save_submit') and not course.save_submit:
            # set the save submit flag so user cannot update
            course.save_submit = True
            course.save()
            # update crosslisted courses
            for cl in course.cross_listing.all():
                cl.save_submit = True
                cl.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                "Step 2 is complete. The GEOC committe will review your course and report back to you presently.",
                extra_tags='alert-success',
            )
            subject = '[GEOC] {0} ({1})'.format(course.title, course.number)
            managers = []
            for man in User.objects.filter(groups__name='Managers'):
                managers.append(man.email)
            if settings.DEBUG:
                course.managers = managers
                to_list = bcc = [settings.MANAGERS[0][1]]
            else:
                to_list = [course.user.email]
                bcc = managers
            frum = course.user.email
            send_mail(
                request,
                to_list,
                subject,
                frum,
                'geoc/email_submit.html',
                course,
                reply_to=[frum,],
                bcc=bcc,
            )
            return HttpResponseRedirect(reverse_lazy('dashboard_home'))
        elif not errors:
            messages.add_message(
                request,
                messages.SUCCESS,
                "Your course has been saved but has not been submitted to GEOC for review.",
                extra_tags='alert-success',
            )
            return HttpResponseRedirect(reverse_lazy('dashboard_home'))
    else:
        form_note = AnnotationForm(
            instance=adendum,
            use_required_attribute=settings.REQUIRED_ATTRIBUTE,
        )
        for outcome in course.outcome.all():
            if outcome.active:
                forms = []
                for element in outcome.elements.all():
                    slo = element.slo.get(course=course)
                    form = CourseOutcomeForm(
                        prefix='slo{0}'.format(slo.id),
                        request=request,
                        instance=slo,
                    )
                    forms.append(form)
                forms_dict[outcome.get_form()] = forms

    return render(
        request,
        'geoc/form_outcome.html',
        {
            'form': form,
            'form_note': form_note,
            'errors': errors,
            'course': course,
        },
    )
