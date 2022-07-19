# -*- coding: utf-8 -*-

"""Data models."""

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from djtools.fields.helpers import upload_to_path
from taggit.managers import TaggableManager


class Outcome(models.Model):
    """Choices for model and form fields that accept for multiple values."""

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    rationale = models.TextField(null=True, blank=True)
    group = models.ManyToManyField(Group, blank=True)
    tags = TaggableManager(blank=True)
    slo1 = models.CharField(
        "Student Learning Outcome 1",
        max_length=255,
        null=True,
        blank=True,
    )
    slo2 = models.CharField(
        "Student Learning Outcome 2",
        max_length=255,
        null=True,
        blank=True,
    )
    slo3 = models.CharField(
        "Student Learning Outcome 3",
        max_length=255,
        null=True,
        blank=True,
    )
    slo4 = models.CharField(
        "Student Learning Outcome 4",
        max_length=255,
        null=True,
        blank=True,
    )
    slo5 = models.CharField(
        "Student Learning Outcome 5",
        max_length=255,
        null=True,
        blank=True,
    )
    slo6 = models.CharField(
        "Student Learning Outcome 6",
        max_length=255,
        null=True,
        blank=True,
    )

    class Meta:
        """Attributes about the data model and admin options."""

        ordering = ['name']

    def __str__(self):
        """Default data for display."""
        return self.name

    def tag_list(self):
        return ', '.join(o.name for o in self.tags.all())


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

    class Meta:
        """Attributes about the data model and admin options."""

        ordering = ['title']

    def __str__(self):
        """Default data for display."""
        return self.title

    def get_slug(self):
        """Slug for file uploads."""
        return 'files/course/'


class CourseOutcome(models.Model):
    """Choices for model and form fields that accept for multiple values."""

    course = models.ForeignKey(
        Course,
        related_name='course',
        on_delete=models.CASCADE,
        editable=settings.DEBUG,
    )
    outcome = models.ForeignKey(
        Outcome,
        related_name='outcome',
        on_delete=models.CASCADE,
        editable=settings.DEBUG,
    )
    description = models.TextField()


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
