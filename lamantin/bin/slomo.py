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
    course = Course.objects.get(pk=3)
    print(course)


    #for outcome in course.outcomes.all():
    for outcome in course.outcome.all():
        #print(outcome.elements.all())
        print(outcome)
        #for outcome in instance.outcomes.all():
        #for element in outcome.elements.all():
        for element in outcome.elements.all():
            #slo = element.slo.get(course=course)
            #print(slo.id)
            print(element.get_slo(course).id)
        '''
            if getattr(element, 'slo'):
                print(element.slo.id)
            else:
                print('no slo')
                #slo = CourseOutcome(course=course, slo=element)
                #slo.save()
                #element.slo=slo
                #element.save()
        '''


if __name__ == '__main__':

    sys.exit(main())
