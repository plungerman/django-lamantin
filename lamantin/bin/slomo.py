#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

import django
django.setup()
from lamantin.geoc.models import Course
from lamantin.geoc.models import CourseOutcome


# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lamantin.settings.shell')


def main():
    """Main function that does something."""
    course = Course.objects.get(pk=1)
    for outcome in course.outcome.all():
        print(outcome)
        for element in outcome.elements.all():
            print(element)
            try:
                print(element.slo)
            except Exception:
                slo = CourseOutcome(course=course, slo=element)
                slo.save()
                element.slo=slo
                element.save()


if __name__ == '__main__':

    sys.exit(main())
