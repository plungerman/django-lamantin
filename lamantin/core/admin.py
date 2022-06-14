# -*- coding: utf-8 -*-

"""Admin classes for data models."""

from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple
from django.utils.safestring import mark_safe

from lamantin.core.models import GenericChoice


class GenericChoiceAdmin(admin.ModelAdmin):
    """GenericChoice admin class."""

    list_display = ('name', 'value', 'rank', 'active', 'admin')
    list_editable = ('active', 'admin')
    list_per_page = 500
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    readonly_fields = ('',)
    search_fields = ('',)
    raw_id_fields = ('',)

    def summary_strip(self, instance):
        """Mark html content for summary field as safe."""
        return mark_safe(instance.summary)
    summary_strip.short_description = 'Summary'

    class Media:
        """Static files like javascript and style sheets."""

        js = [
            '/static/lamantin/js/foobar.js',
        ]


admin.site.register(GenericChoice, GenericChoiceAdmin)
