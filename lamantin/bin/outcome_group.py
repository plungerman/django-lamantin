#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

import django
django.setup()
from lamantin.geoc.models import Course
from lamantin.geoc.models import Outcome


# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lamantin.settings.shell')


def main():
    """Main function that does something."""
    course = Course.objects.get(pk=3)
    for outcome in course.outcome.all():
        print(outcome.group.all())


if __name__ == '__main__':

    sys.exit(main())
