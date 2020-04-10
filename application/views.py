from . import app
from .classification_model import classification_model
from .models import db, User, Health, PreviousRecord

from flask import Flask, logging, Markup, jsonify, redirect, render_template, request, session, url_for
from flask_breadcrumbs import Breadcrumbs, register_breadcrumb
from flask_login import (
    LoginManager,
    login_required,
    logout_user,
    current_user,
    login_user,
)
from io import TextIOWrapper, BytesIO
from flask_weasyprint import HTML, render_pdf

import base64
import csv
import flask_whooshalchemy
import json
import io
import matplotlib.pyplot as plt
import numpy
import pandas
import seaborn

breadcrumbs = Breadcrumbs(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(id):
    if id is not None:
        return User.query.get(id)
    return None

@app.before_request
def before_request():
    if current_user.is_authenticated:
        flask_whooshalchemy.search_index(app, User)

@app.route("/")
def home():
    return redirect('/login')


# Login | Logout | Register
@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect("/dashboard")

    if request.method == "POST":
        user_email = request.form["email"]
        user_password = request.form["password"]

        validation = User.query.filter_by(
            email=user_email, password=user_password
        ).first()

        if validation is not None:
            login_user(validation)

            return redirect("/dashboard")
        else:
            return render_template('login.html', error = 'Incorrect Email or Password')

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        fullname_content = request.form["fullname"]
        ic_content = request.form["ic"]
        email_content = request.form["email"]
        password_content = request.form["password"]
        repassword_content = request.form["repassword"]
        phone_content = request.form["phone"]
        dob_content = request.form["dob"]
        age_content = request.form["age"]
        sex_content = request.form["sex"]
        access_level_content = request.form["access_level"]

        if password_content == repassword_content:
            new_user = User(
                fullname=fullname_content,
                ic=ic_content,
                email=email_content,
                password=password_content,
                phone=phone_content,
                dob=dob_content,
                age=age_content,
                sex=sex_content,
                access_level=access_level_content,
            )
        else:
            return render_template(
                "register.html", error="Password and Confirm are not match"
            )

        try:
            db.session.add(new_user)
            db.session.flush()
            new_patient = Health(user_id = new_user.id)
            db.session.add(new_patient)
            db.session.commit()
            return render_template("register.html", success="Registered Successfully")
        except:
            return "Error"

    else:
        return render_template("register.html")


#  User Section
@app.route("/add_patient", methods=["POST", "GET"])
@register_breadcrumb(app, '.patient_record.add_patient', 'Add Patient')
def add_patient():
    if request.method == "POST":
        fullname_content = request.form["fullname"]
        ic_content = request.form["ic"]
        email_content = request.form["email"]
        password_content = request.form["password"]
        phone_content = request.form["phone"]
        dob_content = request.form["dob"]
        age_content = request.form["age"]
        sex_content = request.form["sex"]
        access_level_content = request.form["access_level"]

        new_user = User(
            fullname=fullname_content,
            ic=ic_content,
            email=email_content,
            password=password_content,
            phone=phone_content,
            dob=dob_content,
            age=age_content,
            sex=sex_content,
            access_level=access_level_content,
        )
        
        try:
            db.session.add(new_user)
            db.session.flush()
            new_patient = Health(user_id = new_user.id)
            db.session.add(new_patient)
            db.session.commit()
            return render_template("dashboard/add_patient.html", success="Patient Registered Successfully")
        except:
            return "Error"
    
    else:
        return render_template("dashboard/add_patient.html")

@app.route("/dashboard", methods=["GET"])
@login_required
@register_breadcrumb(app, '.', 'Home')
def dashboard():
    users = User.query.join(Health).filter(User.id == Health.user_id).order_by(User.date_created.desc()).all()
    
    positive_result = Health.query.filter(Health.target == 1).count()
    negative_result = Health.query.filter(Health.target == 0).count()
    
    return render_template("/dashboard/index.html", users=users, positive_result = positive_result, negative_result = negative_result)

@app.route("/delete_patient/<int:id>")
def delete_patient(id):
    user_to_delete = User.query.get_or_404(id)

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return redirect("/patient_record")
    except:
        return "Error"


@app.route("/update_patient_record/<int:id>", methods=["GET", "POST"])
@register_breadcrumb(app, '.patient_record.update_patient_record', 'Update Patient Record')
def update_patient_record(id):
    user = User.query.get_or_404(id)

    if request.method == "POST":
        user.fullname = request.form["fullname"]
        user.ic = request.form["ic"]
        user.email = request.form["email"]
        user.phone = request.form["phone"]
        user.dob = request.form["dob"]
        user.age = request.form["age"]
        user.sex = request.form["sex"]

        try:
            db.session.commit()
            return redirect("/patient_record")
        except:
            return "Error"

    else:
        return render_template("dashboard/update_patient_record.html", user=user)


@app.route("/patient_record", methods=["POST", "GET"])
@register_breadcrumb(app, '.patient_record', 'Patient Records')
def patient_record():
    users = User.query.join(Health).filter(User.id == Health.user_id).order_by(User.date_created).all()
    return render_template("/dashboard/patient_record.html", users=users)

@app.route("/predict/<int:id>", methods=["GET", "POST"])
@register_breadcrumb(app, '.patient_record.predict', 'Prediction')
def predict(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':

        number_feature = [(n) for n in request.form.values()]
        feature = [numpy.array(number_feature)]
        prediction = classification_model.predict(feature)

        result = prediction[0]

        if result == 0:
            patient_target = 0
        else:
            patient_target = 1 

        patient_id = user.id
        patient_cp = request.form['cp']
        patient_trestbps = request.form['trestbps']
        patient_chol = request.form['chol']
        patient_fbs = request.form['fbs']
        patient_restecg = request.form['restecg']
        patient_thalach = request.form['thalach']
        patient_exang = request.form['exang']
        patient_oldpeak = request.form['oldpeak']
        patient_slope = request.form['slope']
        patient_ca = request.form['ca']
        patient_thal = request.form['thal']

        for health in user.health:
            health.cp = request.form['cp']
            health.trestbps = request.form['trestbps']
            health.chol = request.form['chol']
            health.fbs = request.form['fbs']
            health.restecg = request.form['restecg']
            health.thalach = request.form['thalach']
            health.exang = request.form['exang']
            health.oldpeak = request.form['oldpeak']
            health.slope = request.form['slope']
            health.ca = request.form['ca']
            health.thal = request.form['thal']
            health.target = patient_target
        
        previous_health_record = PreviousRecord(
            user_id = patient_id,
            cp = patient_cp,
            trestbps = patient_trestbps,
            chol = patient_chol,
            fbs = patient_fbs,
            restecg = patient_restecg,
            thalach = patient_thalach,
            exang = patient_exang,
            oldpeak = patient_oldpeak,
            slope = patient_slope,
            ca = patient_ca,
            thal = patient_thal,
            target = patient_target,
        )

        try:
            db.session.add(previous_health_record)
            db.session.commit()
            return render_template('dashboard/update_patient_record.html', user = user, result = result)
        except: 
            return 'Error'
    else:
        return render_template('dashboard/update_patient_record.html', user = user)
    
@app.route("/results", methods=["POST"])
def results():
    data = request.get_json(force=True)
    prediction = classification_model.predict([numpy.array(list(data.values))])

    result = prediction[0]
    return jsonify(result)

@app.route("/search_patient")
def search_patient():
    pass

@app.route('/upload_patient_record', methods = ['GET', 'POST'])
def upload_patient_record():
    if request.method == 'POST':
        csv_file = request.files['file']
        csv_file = TextIOWrapper(csv_file, encoding='utf-8')
        csv_reader = csv.reader(csv_file, delimiter=',')
    
        for row in csv_reader:
            patient_record = User(
                fullname = row[0], 
                ic = row[1],
                email = row[2],
                password = '12345',
                phone = row[3],
                dob = row[4],
                age = row[5],
                sex = row[6],
                access_level = row[7]
            )

            db.session.add(patient_record)
            db.session.flush()

            patient_health_record = Health(
                user_id = patient_record.id,
                cp = row[8],
                trestbps = row[9],
                chol = row[10],
                fbs = row[11],
                restecg = row[12],
                thalach = row[13],
                exang = row[14],
                oldpeak = row[15],
                slope = row[16],
                ca = row[17],
                thal = row[18],
                target = row[19]
            )
            
            db.session.add(patient_health_record)
            db.session.commit()

        return redirect('/patient_record')

    return render_template('dashboard/patient_record.html', success_csv = 'File Sucessfully Uploaded')        

@login_required
@register_breadcrumb(app, '.chart', 'Data Visualization')
@app.route('/data_visualization')
def data_visualization():    
    #Get the data from Postgresql and convert it to Matrics 
    user_dataset = pandas.read_sql(db.session.query(User).statement, db.session.bind)
    health_dataset = pandas.read_sql(db.session.query(Health).statement, db.session.bind)
    dataset = user_dataset.merge(health_dataset, left_on = 'id', right_on = 'user_id')

    X = request.args.get('X_value')
    y = request.args.get('y_value')

    gender = dataset['sex_x'].map({0: 'Female', 1: 'Male'})

    # As using the Matplotlib or Python, it need to change to binary then decode it 
    img = BytesIO()
    if X == 'age_x' and y == 'target':
        bar = seaborn.countplot(x = dataset['age_x'], hue = dataset['target'])
        bar.legend_.remove()
        plt.title('Target versus Age')
        plt.xlabel('Age')
        plt.ylabel('Count')
        plt.legend(title = 'Result', loc = 'upper right', labels=['Negative', 'Positive'])
        plt.show(bar)
    elif X == 'sex_x' and y == 'target':
        bar = seaborn.countplot(x = gender, hue = dataset['target'])
        bar.legend_.remove()
        plt.title('Result versus Gender')
        plt.xlabel('Gender')
        plt.ylabel('Count')
        plt.legend(title = 'Result', loc = 'upper right', labels=['Negative', 'Positive'])
    else:
        bar = seaborn.countplot(x = dataset['age_x'], hue = gender)
        bar.legend_.remove()
        plt.title('Gender versus Age')
        plt.xlabel('Age')
        plt.ylabel('Count')
        plt.legend(title = 'Gender', loc = 'upper right', labels=['Male', 'Female'])
        plt.show(bar)

    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)

    plot_url = base64.b64encode(img.getvalue()).decode()


    return render_template('dashboard/chart.html', plot_url = plot_url)

@login_required
@register_breadcrumb(app, '.summary_report', 'Summary Report')
@app.route('/summary_report')
def summary_report():
    users = User.query.join(PreviousRecord).filter(PreviousRecord.user_id == User.id ).order_by(User.date_created).all()
    
    return render_template('dashboard/summary_report.html', users = users)

@app.route('/print/<int:id>/summary_report.pdf', methods=['GET', 'POST'])
def print_summary_report(id):
    id = User.query.get_or_404(id)
    html = render_template('dashboard/print_summary_report.html', id = id)
    return render_pdf(HTML(string=html))

