# -*- coding: utf-8 -*-

"""Admin classes for data models."""

from django.contrib import admin
from django.db import models
from lamantin.geoc.models import Annotation
from lamantin.geoc.models import Course
from lamantin.geoc.models import CourseOutcome
from lamantin.geoc.models import Outcome
from lamantin.geoc.models import OutcomeElement


class AnnotationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'course', 'creator_name', 'created_at', 'status')
    raw_id_fields = ('created_by', 'updated_by', 'course')
    list_editable = ['status']

    def creator_name(self, obj):
        return '{0}, {1}'.format(
            obj.created_by.last_name,obj.created_by.first_name,
        )
    creator_name.admin_order_field  = 'created_by'
    creator_name.short_description = "Submitted by"


class CourseAdmin(admin.ModelAdmin):
    """Course admin class."""

    list_display = (
        'title',
        'number',
        'user',
        'created_at',
        'updated_at',
        'approved_date',
        'save_submit',
        'approved',
    )
    list_editable = ('approved', 'save_submit')
    list_per_page = 500


class OutcomeAdmin(admin.ModelAdmin):
    """Outcome admin class."""

    list_display = ('name', 'tag_list', 'active')
    list_per_page = 500
    list_editable = ['active']


class OutcomeElementAdmin(admin.ModelAdmin):
    """Outcome element admin class."""

    list_display = ('outcome', 'description', 'active')
    list_per_page = 500
    list_editable = ['active']


admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(CourseOutcome)
admin.site.register(Outcome, OutcomeAdmin)
admin.site.register(OutcomeElement, OutcomeElementAdmin)
