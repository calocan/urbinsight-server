import logging

from django.core.management.base import BaseCommand

import psycopg2

import os
import time
log = logging.getLogger('info')


class Command(BaseCommand):
    def handle(self, *args, **options):
        create_dbs()


def create_dbs():
    """
    Create databases from django settings, supports postgresql and MySql.
    :return: 
    """
    
    deadline = time.time() + 60
    while time.time() < deadline:
        try:
            log.info(("create_dbs: let's go."))
            django_settings = __import__(os.environ['DJANGO_SETTINGS_MODULE'], fromlist='DATABASES')
            log.info(("create_dbs: got settings."))
            databases = django_settings.DATABASES
            postgres = databases['postgres']
            for name, db in databases.items():
                if name == 'postgres':
                    continue
                host = db['HOST']
                user = postgres['USER']
                password = postgres['PASSWORD']
                port = db['PORT']
                db_name = db['NAME']
                db_type = db['ENGINE']
                # see if it is postgresql
                if db_type.endswith('postgresql_psycopg2'):
                    log.info( 'creating database %s on %s' % (db_name, host))
                    con = psycopg2.connect(host=host, user=user, password=password, port=port, database='postgres')
                    con.set_isolation_level(0)
                    cur = con.cursor()
                    try:
                        cur.execute('IF NOT EXISTSCREATE DATABASE %s' % db_name)
                    except psycopg2.ProgrammingError as detail:
                        log.info( detail)
                        log.info( 'moving right along...')
                    try:
                        cur.execute("IF NOT EXISTS (SELECT * FROM pg_user WHERE username = '{0}') BEGIN CREATE ROLE {0} LOGIN PASSWORD 'my_password'; END; ".format(
                            db['USER']
                        ))
                        cur.execute("GRANT ALL PRIVILEGES ON DATABASE {0} TO {1}".format(
                            db['NAME'],
                            db['USER']
                        ))
                    except:
                        log.info( detail)
                        log.info( 'moving right along...')
                    exit(0)
                else:
                    log.info(("ERROR: {0} is not supported by this script, you will need to create your database by hand.".format(db_type)))
                    exit(1)
        except psycopg2.OperationalError:
            log.info( "Could not connect to database. Waiting a little bit.")
            time.sleep(10)

    log.info( 'Could not connect to database after 1 minutes. Something is wrong.')
