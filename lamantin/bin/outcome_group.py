#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import django
import os
import sys

django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from lamantin.geoc.models import Course
from lamantin.geoc.models import Outcome


# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lamantin.settings.shell')


def main():
    """Main function that does something."""
    course = Course.objects.get(pk=3)
    user = User.objects.get(pk=settings.FACULTY_EXPLORATIONS)
    print(user)
    for outcome in course.outcome.all():
        print(outcome.group)


if __name__ == '__main__':

    sys.exit(main())
