# -*- coding: utf-8 -*-

"""Admin classes for data models."""

from django.contrib import admin
from django.db import models
from lamantin.geoc.models import Course
from lamantin.geoc.models import Outcome


class CourseAdmin(admin.ModelAdmin):
    """Course admin class."""

    list_display = (
        'title',
        'number',
        'user',
        'created_at',
        'updated_at',
        'approved_date',
        'approved',
    )
    list_editable = ['approved']
    list_per_page = 500


class OutcomeAdmin(admin.ModelAdmin):
    """Outcome admin class."""

    list_display = ('name', 'tag_list', 'active')
    list_per_page = 500
    list_editable = ['active']


admin.site.register(Course, CourseAdmin)
admin.site.register(Outcome, OutcomeAdmin)
