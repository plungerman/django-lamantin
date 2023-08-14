#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import django
import os
import sys


django.setup()


from django.conf import settings
from lamantin.geoc.models import Course
from lamantin.geoc.models import OutcomeCourse


# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lamantin.settings.shell')


def main():
    """Main function that does something."""
    course = Course.objects.get(pk=settings.COURSE_TEST_ID)
    for outcome in course.outcome.all():
        oc = OutcomeCourse.objects.get(outcome=outcome, course=course)
        print(oc)
    print(course.get_outcomes())


if __name__ == '__main__':
    sys.exit(main())
