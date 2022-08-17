# -*- coding: utf-8 -*-

"""Data models."""

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from djtools.fields.helpers import upload_to_path
from taggit.managers import TaggableManager


ICONS = {
    'xls': 'excel',
    'xlsx': 'excel',
    'pdf': 'pdf',
    'doc': 'word',
    'docx': 'word',
    'txt': 'text',
    'png': 'image',
    'jpg': 'image',
    'jpeg': 'image',
}


class Outcome(models.Model):
    """Choices for model and form fields that accept for multiple values."""

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    rationale = models.TextField(null=True, blank=True)
    group = models.ForeignKey(
        Group,
        related_name='group',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
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
    furbish = models.BooleanField(
        help_text="Needs work?",
        default=False,
    )
    save_submit = models.BooleanField(default=False)
    # core
    title = models.CharField(max_length=255)
    number = models.CharField(max_length=32)
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

    def syllabus(self):
        """Obtain course syllabus if one exists."""
        phile = None
        for doc in self.docs.annotate(tag_name=models.F('tags__name')):
            if doc.tag_name == 'Syllabus':
                phile = doc
                break
        return phile


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

    def get_slo(self, course):
        return self.slo.get(course=course)


class CourseOutcome(models.Model):
    """Specific SLO content provided by user for a course."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='outcomes',
        editable=settings.DEBUG,
    )
    slo = models.ForeignKey(
        OutcomeElement,
        related_name='slo',
        on_delete=models.CASCADE,
        editable=settings.DEBUG,
    )
    description = models.TextField(
        help_text="Please indicate how this course meets this SLO.",
        null=True,
        blank=True,
    )

    def __str__(self):
        """Default data for display."""
        return '[{0}] {1}: {2}'.format(self.course, self.slo, self.slo.description)


class Document(models.Model):
    """Supporting documents for a course."""

    created_by = models.ForeignKey(
        User,
        related_name='doc_creator',
        on_delete=models.CASCADE,
    )
    updated_by = models.ForeignKey(
        User,
        related_name='doc_updated',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField("Date Created", auto_now_add=True)
    updated_at = models.DateTimeField("Date Updated", auto_now=True)
    course = models.ForeignKey(
        Course,
        related_name='docs',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        "Short description of file",
        max_length=128,
        null=True,
        blank=True,
    )
    phile = models.FileField(
        "Supporting documentation",
        upload_to=upload_to_path,
        validators=settings.FILE_VALIDATORS,
        max_length=767,
        help_text="PDF format",
        null=True,
        blank=True,
    )
    tags = TaggableManager(blank=True)

    class Meta:
        ordering  = ['created_at']
        get_latest_by = 'created_at'

    def get_slug(self):
        """Return the slug value for this data model class."""
        return 'files/course/'

    def get_icon(self):
        """Obtain the icon for a field."""
        ext = self.phile.path.rpartition(".")[-1]
        try:
            icon = ICONS[ext.lower()]
        except:
            icon = ICONS['file']
        return icon

    def __str__(self):
        """Default data for display."""
        return str(self.course)


class Annotation(models.Model):
    """Notes related to a Course."""

    course = models.ForeignKey(
        Course,
        related_name='notes',
        on_delete=models.CASCADE,
    )
    created_by = models.ForeignKey(
        User,
        verbose_name="Created by",
        related_name='note_creator',
        on_delete=models.PROTECT,
    )
    updated_by = models.ForeignKey(
        User,
        verbose_name="Updated by",
        related_name='note_updated',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField("Date Created", auto_now_add=True)
    updated_at = models.DateTimeField("Date Updated", auto_now=True)
    body = models.TextField()
    status = models.BooleanField(default=True, verbose_name="Active?")
    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        """Default data for display."""
        return "{0}, {1}".format(
            self.created_by.last_name, self.created_by.first_name
        )


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
                element.slo.add(slo)
                element.save()
        if action == 'pre_remove':
            for element in outcome.elements.all():
                slo = element.get_slo(instance)
                slo.delete()
