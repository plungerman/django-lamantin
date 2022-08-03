#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

import django
django.setup()
from lamantin.geoc.models import Course
from lamantin.geoc.models import CourseOutcome
from lamantin.geoc.models import Outcome


# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lamantin.settings.shell')


class Dupes:
    """Data model for managing form validation for outcomes."""

    def __init__(self):
        self.tags = {
            'Abilities': {'outcomes': [], 'error': False},
            'Explorations': {'outcomes': [], 'error': False},
            'Perspectives': {'outcomes': [], 'error': False},
        }
        self.error = []

    def get_outcomes(self):
        for tag, outcomes in self.tags.items():
            print(tag)
            self.tags[tag]['outcomes'] = Outcome.objects.filter(tags__name__in=[tag])
            print(self.tags[tag]['outcomes'])
            print(self.tags[tag]['error'])

    def check(self, course):
        for outcome in course.outcome.all():
            for tag, slo in self.tags.items():
                #print('\t{0}'.format(self.tags[tag]['outcomes']))
                if outcome in slo['outcomes'] and not slo['error']:
                    print(outcome)
                    slo['error'] = True


def main():
    """Main function that does something."""
    dupes = Dupes()
    dupes.get_outcomes()
    print('Course outcomes')
    course = Course.objects.get(pk=6)
    dupes.check(course)


if __name__ == '__main__':

    sys.exit(main())
