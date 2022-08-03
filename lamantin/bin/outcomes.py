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
            self.tags[tag]['outcomes'] = Outcome.objects.filter(tags__name__in=[tag])

    def check(self, outcomes):
        for outcome in outcomes:
            for tag, slo in self.tags.items():
                if outcome in slo['outcomes'] and tag not in self.error:
                    print(outcome)
                    self.error.append(tag)
                    slo['error'] = True


def main():
    """Main function that does something."""
    dupes = Dupes()
    dupes.get_outcomes()
    print('Course outcome dupes')
    course = Course.objects.get(pk=6)
    dupes.check(course.outcome.all())
    print(dupes.error)


if __name__ == '__main__':

    sys.exit(main())
