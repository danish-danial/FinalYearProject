import os

from flask import Flask

app = Flask(__name__)
app.secret_key = "this_is_a_secret_word"

import application.views

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 80)