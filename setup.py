from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
# toolbar = DebugToolbarExtension(app)
