#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lamantin.settings.shell')

# required if using django models
import django
django.setup()

from django.conf import settings

import argparse
import logging

logger = logging.getLogger('debug_logfile')

# set up command-line options
desc = """
Accepts as input...
"""

# RawTextHelpFormatter method allows for new lines in help text
parser = argparse.ArgumentParser(
    description=desc, formatter_class=argparse.RawTextHelpFormatter,
)

parser.add_argument(
    '-x',
    '--equis',
    required=True,
    help="Lorem ipsum dolor sit amet.",
    dest='equis',
)
parser.add_argument(
    '--test',
    action='store_true',
    help="Dry run?",
    dest='test',
)


def main():
    """Main function description."""
    if test:
        print("this is a test")
        logger.debug("debug = %s" % test)
    else:
        print("this is not a test")


if __name__ == '__main__':
    args = parser.parse_args()
    equis = args.equis
    test = args.test

    if test:
        print(args)

    sys.exit(main())
