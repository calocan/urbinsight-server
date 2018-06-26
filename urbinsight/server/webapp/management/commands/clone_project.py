import logging

from helpers.project_helpers import clone_project
from django.core.management.base import BaseCommand, CommandError

log = logging.getLogger('info')

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('project_id', type=int)

    def handle(self, *args, **options):
        """
        Clones the given project
        """
        project_id = options['project_id']
        clone_project(project_id)
