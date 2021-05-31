import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
username = "postgres"
password = "Sameh416"
host = "localhost"
port = 5432
dbname = "fyyur"
# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = f'postgresql://{username}:{password}@{host}:{port}/{dbname}'
