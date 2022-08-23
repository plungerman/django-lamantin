#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

import django
django.setup()
from lamantin.geoc.models import Course


# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lamantin.settings.shell')


def main():
    """Main function that does something."""
    #courses = Course.objects.all()
    courses = Course.objects.filter(outcome__name='Artistic Inquiries')
    for course in courses:
        print(course)
        #print(course.outcome.all())


if __name__ == '__main__':

    sys.exit(main())
