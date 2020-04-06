from flask import Flask
import os

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "this_is_a_secret_word"

import application.views

if __name__ == '__main__':
    app.run()