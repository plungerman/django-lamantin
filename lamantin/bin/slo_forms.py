#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

import django
django.setup()
from lamantin.geoc.models import Course
from lamantin.geoc.models import CourseOutcome
from lamantin.geoc.forms import CourseOutcomeForm


# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lamantin.settings.shell')


def main():
    """Main function that does something."""
    course = Course.objects.get(pk=2)
    forms_dict = {}
    for outcome in course.outcome.all():
        forms = []
        for element in outcome.elements.all():
            form = CourseOutcomeForm(prefix='slo{0}'.format(element.slo.id), instance=element.slo)
            forms.append(form)
        forms_dict[outcome.get_form()] = forms

    for key, val in forms_dict.items():
        print(key)
        for f in val:
            print(f)


if __name__ == '__main__':

    sys.exit(main())
