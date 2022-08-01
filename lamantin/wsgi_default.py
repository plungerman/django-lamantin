# -*- coding: utf-8 -*-

"""WSGI configuration."""

import os
import sys

from django.core.wsgi import get_wsgi_application


# python
sys.path.append('/d2/python_venv/3.8/djlamantin/lib/python3.8/')
sys.path.append('/d2/python_venv/3.8/djlamantin/lib/python3.8/site-packages/')
# django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lamantin.settings.production')
os.environ.setdefault('PYTHON_EGG_CACHE', '/var/cache/python/.python-eggs')
os.environ.setdefault('TZ', 'America/Chicago')
# informix
os.environ['INFORMIXSERVER'] = ''
os.environ['DBSERVERNAME'] = ''
os.environ['INFORMIXDIR'] = ''
os.environ['ODBCINI'] = ''
os.environ['ONCONFIG'] = ''
os.environ['INFORMIXSQLHOSTS'] = ''
os.environ['LD_LIBRARY_PATH'] = """
    {0}/lib:{0}/lib/esql:{0}/lib/tools:/usr/lib/apache2/modules:{0}/lib/cli
""".format(os.environ['INFORMIXDIR'])
os.environ['LD_RUN_PATH'] = os.environ['LD_LIBRARY_PATH']
# wsgi
application = get_wsgi_application()
