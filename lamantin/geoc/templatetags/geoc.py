# -*- coding: utf-8 -*-

from django import template
from lamantin.geoc.models import OutcomeCourse


register = template.Library()


@register.simple_tag
def get_outcome(course, outcome):
    try:
        oc = OutcomeCourse.objects.get(outcome=outcome, course=course)
    except Exception:
        oc = None
    return oc
