from flask import Flask
app = Flask(__name__)
import flaskr.main
from flask_bootstrap import Bootstrap

from flaskr import db
db.create_data()
db.create_persons()

bootstrap = Bootstrap(app)