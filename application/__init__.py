from flask import Flask
from flask_migrate import Migrate
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.from_object('config')
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'danishdanialzurkanain@gmail.com'
app.config['MAIL_PASSWORD'] = 'mgdeeubocvbxftiy'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "WEvZt&hk$8QKZD5"

db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type = True)
posta = Mail(app)

import application.views

if __name__ == '__main__':
    app.run()