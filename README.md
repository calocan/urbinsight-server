# urbinsight-server
Server for Urbinsight

Installation:

Create a virtual environment using
python3 -m venv virtualenvname
Activate it
source virtualenvname/bin/activate.py

# Install requirements
$VIRTUAL_ENV/bin/pip install --no-cache-dir  --upgrade -r requirements.txt

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
