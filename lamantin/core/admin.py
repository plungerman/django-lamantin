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


admin.site.register(GenericChoice, GenericChoiceAdmin)
