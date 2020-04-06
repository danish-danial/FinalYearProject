import flask_whooshalchemy 
from . import app
from datetime import datetime
from flask_login import UserMixin
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from whoosh.analysis import StemmingAnalyzer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_whooshalchemy import StemmingAnalyzer

app.config.update(SQLALCHEMY_DATABASE_URI='postgresql://localhost:5432/patient_record')

db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type = True)


class User(db.Model, UserMixin):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key = True)
    fullname = db.Column(db.String(200))
    ic = db.Column(db.String(14))
    email = db.Column(db.String(200), unique = True)
    password = db.Column(db.String(15))
    phone = db.Column(db.String(15))
    dob = db.Column(db.String(10))
    age = db.Column(db.Integer)
    sex = db.Column(db.Integer)
    access_level = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    health = db.relationship('Health', backref = db.backref('user', lazy='joined'))
    previous_record = db.relationship('PreviousRecord', backref = db.backref('user', lazy='joined'))

    def set_password(self, password):
        self.password = generate_password_hash(password, method="sha256")

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"User('{self.fullname}')"

class Health(db.Model):

    __tablename__ = "health"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cp = db.Column(db.Integer)
    trestbps = db.Column(db.Integer)
    chol = db.Column(db.Integer)
    fbs = db.Column(db.Integer)
    restecg = db.Column(db.Integer)
    thalach = db.Column(db.Integer)
    exang = db.Column(db.Integer)
    oldpeak = db.Column(db.Float)
    slope = db.Column(db.Integer)
    ca = db.Column(db.Float)
    thal = db.Column(db.Float)
    target = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<Health {}>" % (self.target)

class PreviousRecord(db.Model):

    __tablename__ = "previous_record"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cp = db.Column(db.Integer)
    trestbps = db.Column(db.Integer)
    chol = db.Column(db.Integer)
    fbs = db.Column(db.Integer)
    restecg = db.Column(db.Integer)
    thalach = db.Column(db.Integer)
    exang = db.Column(db.Integer)
    oldpeak = db.Column(db.Float)
    slope = db.Column(db.Integer)
    ca = db.Column(db.Float)
    thal = db.Column(db.Float)
    target = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<PreviousRecord {}>" % (self.date_created)
