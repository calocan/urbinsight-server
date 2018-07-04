# urbinsight-server
Server for Urbinsight

Installation:

Create a virtual environment using
python3 -m venv virtualenvname
Activate it
source virtualenvname/bin/activate

# Install requirements
$VIRTUAL_ENV/bin/pip install --no-cache-dir  --upgrade -r requirements.txt

# Install Postgis 
Stop Postgres:
pg_ctl -D /usr/local/var/postgres stop -s -m fast
Upgrade postgres:
brew postgresql-upgrade-database
Install Postgis, following these intstructions:
https://docs.djangoproject.com/en/2.0/ref/contrib/gis/install
After installing required libraries, make sure to isntall Postgis in postgres:
$ createdb  <db name>
$ psql <db name>
> CREATE EXTENSION postgis;
Make sure you switch to db_name before running CREATE EXTENSION postgis
Note that for testing, the database user must be a superuser to create the test_post
$ psql postgres
=# ALTER ROLE urbuser SUPERUSER;
Make sure to never do this in production, or unset with
=# ALTER ROLE urbuser NO_SUPERUSER;

Note that I found on OSX that this missed up my virtualenv installation and pip installation,
so I had to reinstall pip after and recreate my virtualenv. Hopefully that was a one-off incident
Start Postgres
pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start


# Create the database, db users and tables
It's best to define a .pgpass file in your ~ directory with this line:
127.0.0.1:5432:urbinsight:urbuser:urbpasswd
where dbname, username, and pw can be what you want if it matches those in settings.py

Create the user in settings.py with the matching password provided, since we normally omit it from
settings.py
python3 manage.py create_db urbpasswd

Migrate to create the database tables
python3 manage.py migrate

# Run tests
python3 manage.py test

# Run the server
python3 manage.py runserver
