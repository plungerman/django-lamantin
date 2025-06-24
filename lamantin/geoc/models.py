# -*- coding: utf-8 -*-

"""Data models."""

import datetime

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from djtools.fields import BINARY_CHOICES
from djtools.fields.helpers import upload_to_path
from djtools.utils.users import in_group
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
STATUS_CHOICES = (
    ('Provisional', 'Provisional'),
    ('Confirmed', 'Confirmed'),
)


class Outcome(models.Model):
    """Choices for model and form fields that accept for multiple values."""

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    rationale = models.TextField(null=True, blank=True)
    mechanism = models.TextField(null=True, blank=True)
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
    cross_listing = models.ManyToManyField('self', blank=True)
    created_at = models.DateTimeField("Date Created", auto_now_add=True)
    updated_at = models.DateTimeField("Date Updated", auto_now=True)
    # status
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
    archive = models.BooleanField(default=False)
    status = models.CharField(
        max_length=32,
        choices=STATUS_CHOICES,
        null=True,
        blank=True,
    )
    confirmed_date = models.DateField(null=True, blank=True)
    # core
    title = models.CharField(
        max_length=255,
        help_text="""
            Course name or a descriptive title if you are submiting multiple courses
        """,
    )
    number = models.CharField(
        "Number",
        max_length=255,
        help_text="FORMAT: AAA 1234 or AAA 123X e.g. HIS 4200, BIO 420T",
    )
    multipass = models.CharField(
        "I am submitting multiple courses under the same SLO's",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    outcome = models.ManyToManyField(
        Outcome,
        through='OutcomeCourse',
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

    def comments(self):
        """Return annotation comments."""
        return self.notes.filter(tags__name__in=['Comments'])

    def adenda(self):
        """Return adenda comments."""
        return self.notes.filter(tags__name__in=['Furbish', 'Adenda'])

    def permissions(self, user):
        status = in_group(user, settings.MANAGER_GROUP)
        for outcome in self.outcome.all():
            if user.groups.filter(name=outcome.group).exists():
                status = True
        return status

    def abilities(self):
        """Return abilities SLO."""
        return self.outcome.filter(group__name='Abilities')

    def explorations(self):
        """Return explorations SLO."""
        return self.outcome.filter(group__name='Explorations')

    def get_outcomes(self):
        """Get outcomes."""
        outcomes = []
        for outcome in self.outcome.all():
            oc = OutcomeCourse.objects.get(outcome=outcome, course=self)
            outcomes.append(oc)
        return outcomes

    def perspectives(self):
        """Return perspective SLO."""
        return self.outcome.filter(group__name='Perspectives')

    def outcomes_status(self, field):
        """Check if all outcomes are approved."""
        status = False
        outcomes = self.outcome.all().count()
        count = 0
        for outcome in self.outcome.all():
            oc = OutcomeCourse.objects.get(outcome=outcome, course=self)
            if getattr(oc, field):
                count += 1
        if count >= outcomes:
            status = True
        return status

    def set_outcome(self, state, status, date):
        """Set outcome status."""
        for outcome in self.outcome.all():
            outcome_course = OutcomeCourse.objects.get(outcome=outcome, course=self)
            if state == 'approve':
                outcome_course.approved = status
                outcome_course.approved_date = date
            if state == 'furbish':
                outcome_course.furbish = status
            outcome_course.save()

    def wellness(self):
        """Return wellnesse SLO."""
        return self.outcome.filter(group__name='Wellness')

    def parent(self):
        """Determine parent."""
        parent = True
        for cross_list in self.cross_listing.all():
            if self.id > cross_list.id:
                parent = False
                break
            else:
                parent = True
        return parent


class OutcomeCourse(models.Model):
    """Specific Outocomes for each course."""

    outcome = models.ForeignKey(
        Outcome,
        related_name='course_outcomes',
        on_delete=models.CASCADE,
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    approved_date = models.DateField(null=True, blank=True)
    furbish = models.BooleanField(
        help_text="Needs work?",
        default=False,
    )

    class Meta:
        db_table = 'geoc_course_outcome'

    def __str__(self):
        """Default data for display."""
        return '{0} ({1}): {2}'.format(self.course, self.course.id, self.outcome)

    def is_approved(self):
        status = False
        if self.course.approved or self.approved:
            status = True
        return status

    def is_furbished(self):
        status = False
        if self.course.furbish or self.furbish:
            status = True
        return status


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
        return '[{0} ({1})] {2}: {3}'.format(
            self.course, self.course.id, self.slo, self.slo.description,
        )


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
        max_length=255,
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
        now = datetime.datetime.now()
        instance.approved_date = now
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
