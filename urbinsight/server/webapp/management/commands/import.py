import logging
import time
import os

import sys
import traceback

from django.core.management import BaseCommand

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
import django
django.setup()
log = logging.getLogger("info")
from django.db import connection

class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        """
        :return:
        """
        verbosity = int(options['verbosity'])
        root_logger = logging.getLogger('')
        if verbosity > 1:
            root_logger.setLevel(logging.DEBUG)

        ImportWorker().run()

class ImportWorker(object):
    def run(self):
        pass
