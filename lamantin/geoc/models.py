# -*- coding: utf-8 -*-

"""Data models."""

import logging

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from djtools.fields.helpers import upload_to_path
from taggit.managers import TaggableManager


logger = logging.getLogger('debug_logfile')


class Outcome(models.Model):
    """Choices for model and form fields that accept for multiple values."""

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    rationale = models.TextField(null=True, blank=True)
    group = models.ManyToManyField(Group, blank=True)
    tags = TaggableManager(blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        """Attributes about the data model and admin options."""

        ordering = ['name']

    def __str__(self):
        """Default data for display."""
        return self.name

    def tag_list(self):
        return ', '.join(o.name for o in self.tags.all())

    def get_form(self):
        """Form name."""
        return self.name.replace(' ', '')


class Course(models.Model):
    """Choices for model and form fields that accept for multiple values."""

    # meta
    user = models.ForeignKey(
        User,
        verbose_name="Created by",
        related_name='created_by',
        on_delete=models.CASCADE,
        editable=settings.DEBUG,
    )
    updated_by = models.ForeignKey(
        User,
        verbose_name="Updated by",
        related_name='updated_by',
        on_delete=models.CASCADE,
        editable=settings.DEBUG,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField("Date Created", auto_now_add=True)
    updated_at = models.DateTimeField("Date Updated", auto_now=True)
    approved = models.BooleanField(
        help_text="Has the course been approved?",
        default=False,
    )
    approved_date = models.DateField(null=True, blank=True)
    save_submit = models.BooleanField(default=False)
    # core
    title = models.CharField(max_length=255)
    number = models.CharField(max_length=32)
    phile = models.FileField(
        "Syllabus",
        upload_to=upload_to_path,
        validators=settings.FILE_VALIDATORS,
        max_length=767,
        null=True,
        blank=True,
        help_text="PDF format",
    )
    outcome = models.ManyToManyField(
        Outcome,
        verbose_name="Outcomes",
        help_text="Check all that apply",
    )

    class Meta:
        """Attributes about the data model and admin options."""

        ordering = ['title']

    def __str__(self):
        """Default data for display."""
        return self.title

    def get_slug(self):
        """Slug for file uploads."""
        return 'files/course/'


class OutcomeElement(models.Model):
    """Description for each element of an Outcome."""

    outcome = models.ForeignKey(
        Outcome,
        related_name='elements',
        on_delete=models.CASCADE,
        editable=settings.DEBUG,
    )
    active = models.BooleanField(default=True)
    description = models.TextField()

    def __str__(self):
        """Default data for display."""
        return '{0}: {1}'.format(self.outcome, self.description)


class CourseOutcome(models.Model):
    """Specific SLO content provided by user for a course."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='outcomes',
        editable=settings.DEBUG,
    )
    slo = models.OneToOneField(
        OutcomeElement,
        related_name='slo',
        on_delete=models.CASCADE,
        editable=settings.DEBUG,
    )
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        """Default data for display."""
        return '[{0}] {1}: {2}'.format(self.course, self.slo, self.slo.description)


@receiver(models.signals.post_save, sender=Course)
def approved_date(sender, instance, created, **kwargs):
    """Post-save signal function to set approved_date."""
    if instance.approved and not instance.approved_date:
        from djtools.fields import NOW
        instance.approved_date = NOW
        instance.save()
    elif not instance.approved and instance.approved_date:
        instance.approved_date = None
        instance.save()


@receiver(models.signals.m2m_changed, sender=Course.outcome.through)
def signal_function(sender, instance, action, **kwargs):
    ids = kwargs.get('pk_set')
    for sid in ids:
        outcome = Outcome.objects.get(pk=sid)
        if action == 'post_add':
            for element in outcome.elements.all():
                slo = CourseOutcome(course=instance, slo=element)
                slo.save()
                element.slo=slo
                element.save()
                logger.debug('slo created: {0}'.format(element.slo))
        if action == 'pre_remove':
            for element in outcome.elements.all():
                try:
                    logger.debug('slo deleted: {0}'.format(element.slo))
                    element.slo.delete()
                except Exception as xcept:
                    logger.debug(xcept)
