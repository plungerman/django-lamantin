#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys


# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lamantin.settings.shell')


def main():
    """Main function that does something."""
    try:
        print("hello world")
    except Exception as error:
        print("does not exist")
        print("Exception: {0}".format(str(error)))
        sys.exit(1)


if __name__ == '__main__':

    sys.exit(main())
