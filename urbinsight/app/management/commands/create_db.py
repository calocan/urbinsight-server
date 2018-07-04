import logging

from django.core.management.base import BaseCommand

import psycopg2

import os
import time

log = logging.getLogger('info')


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('password', type=str)

    def handle(self, *args, **options):
        password = options['password']
        create_dbs(password)


def create_dbs(password):
    """
    Create databases from django settings, supports postgresql and MySql.
    :return: 
    """
    log.info(("create_dbs: let's go."))
    django_settings = __import__(os.environ['DJANGO_SETTINGS_MODULE'], fromlist=['DATABASES'])
    log.info(("create_dbs: got settings."))
    databases = django_settings.DATABASES
    #used to create the default db
    #This is just used with create_dbs
    postgres_user = os.environ.get('POSTGRES_DB_USER')
    postgres_pass = os.environ.get('POSTGRES_DB_PASS')
    postgres_host = os.environ.get('POSTGRES_DB_HOST', 'localhost')
    postgres_port = os.environ.get('POSTGRES_DB_PORT', 5432)
    for name, db in databases.items():
        host = db['HOST']
        password = db['PASSWORD'] or password
        db_name = db['NAME']
        db_type = db['ENGINE']
        # see if it is postgresql
        if db_type.endswith('postgresql_psycopg2') or db_type.endswith('django.contrib.gis.db.backends.postgis'):
            log.info('creating database %s on %s' % (db_name, host))
            con = psycopg2.connect(host=postgres_host, user=postgres_user, password=postgres_pass, port=postgres_port, database='postgres')
            con.set_isolation_level(0)
            cur = con.cursor()
            try:
                cur.execute('CREATE DATABASE {0}'.format(db_name))
            except psycopg2.ProgrammingError as detail:
                log.info(detail)

            try:
                cur.execute(
                    "CREATE ROLE {0} LOGIN PASSWORD '{1}'".format(
                        db['USER'],
                        password
                    ))
            except psycopg2.ProgrammingError as detail:
                log.info(detail)

            try:
                cur.execute("GRANT ALL PRIVILEGES ON DATABASE {0} TO {1}".format(
                    db['NAME'],
                    db['USER']
                ))
                cur.execute("ALTER ROLE {0} CREATEDB".format(
                    db['USER']
                ))
            except psycopg2.ProgrammingError as detail:
                log.info(detail)

        else:
            log.info(
                "ERROR: {0} is not supported by this script, you will need to create your database by hand.".format(
                    db_type)
            )
