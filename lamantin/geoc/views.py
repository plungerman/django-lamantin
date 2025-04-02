# -*- coding: utf-8 -*-

"""URLs for all views."""

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
            messages.add_message(
                request,
                messages.SUCCESS,
                "Step 1 is complete. Please complete the outcomes below.",
                extra_tags='alert-success',
            )
            return HttpResponseRedirect(
                reverse_lazy('update', args=['outcome', course.id]),
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
            instance=phile,
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
            messages.add_message(
                request,
                messages.SUCCESS,
                "Step 1 is complete. Please complete the outcomes below.",
                extra_tags='alert-success',
            )
            return HttpResponseRedirect(
                reverse_lazy('update', args=['outcome', course.id]),
            )
    else:
        form = CourseForm(
            instance=course,
            use_required_attribute=settings.REQUIRED_ATTRIBUTE,
        )
        form_syllabus = DocumentForm(
            instance=phile,
            use_required_attribute=settings.REQUIRED_ATTRIBUTE,
            prefix='syllabus',
        )
    return render(
        request,
        template,
        {
            'form': form,
            'form_syllabus': form_syllabus,
        },
    )


@login_required
def outcome_form(request, step='course', cid=None):
    """GEOC workflow form to update a course."""
    course = None
    template = 'geoc/form_{0}.html'.format(step)
    forms_dict = {}
    errors = False
    user = request.user
    form_note = None
    form_syllabus = None
    adendum = None
    phile = None
    if cid:
        course = Course.objects.get(pk=cid)
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
        if course.syllabus():
            phile = course.syllabus()

    if request.method == 'POST':
        post = request.POST
        if step=='outcome':
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

            if not errors and post.get('save_submit') and not course.save_submit:
                # set the save submit flag so user cannot update
                course.save_submit = True
                course.save()
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
            form = CourseForm(
                post,
                instance=course,
                use_required_attribute=settings.REQUIRED_ATTRIBUTE,
            )
            form_syllabus = DocumentForm(
                post,
                request.FILES,
                instance=phile,
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
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    "Step 1 is complete. Please complete the outcomes below.",
                    extra_tags='alert-success',
                )
                return HttpResponseRedirect(
                    reverse_lazy('update', args=['outcome', course.id]),
                )
    else:
        if step == 'course':
            form = CourseForm(
                instance=course,
                use_required_attribute=settings.REQUIRED_ATTRIBUTE,
            )
            form_syllabus = DocumentForm(
                instance=phile,
                use_required_attribute=settings.REQUIRED_ATTRIBUTE,
                prefix='syllabus',
            )
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
        template,
        {
            'form': form,
            'form_note': form_note,
            'form_syllabus': form_syllabus,
            'errors': errors,
            'step': step,
            'course': course,
        },
    )
