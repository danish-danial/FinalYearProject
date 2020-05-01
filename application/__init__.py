from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "WEvZt&hk$8QKZD5"

db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type = True)

import application.views

if __name__ == '__main__':
    app.run()