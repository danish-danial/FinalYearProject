from . import app, db
from .classification_model import classification_model
from .models import User, Health, PreviousRecord

from bokeh.embed import components, file_html
from bokeh.models import ColumnDataSource
from bokeh.palettes import Viridis5
from bokeh.plotting import figure
from bokeh.resources import CDN

from flask import Flask, flash, logging, Markup, jsonify, redirect, render_template, request, session, url_for

from flask_breadcrumbs import Breadcrumbs, register_breadcrumb

from flask_login import (
    LoginManager,
    login_required,
    logout_user,
    current_user,
    login_user,
)

from flask_weasyprint import HTML, render_pdf

from io import TextIOWrapper, BytesIO

import base64
import csv
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

@app.route("/")
def home():
    return redirect('/login')


# SECTION Forgot Password | Login | Logout | Register

# SECTION Forgot Password
@app.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
   pass
# !SECTION

# SECTION Login
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
# !SECTION

# SECTION Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")
# !SECTION

# SECTION Register
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
# !SECTION

# !SECTION

@app.route("/dashboard", methods=["GET"])
@login_required
@register_breadcrumb(app, '.', 'Home')
def dashboard():
    users = User.query.join(Health).filter(User.id == Health.user_id).order_by(User.date_created.desc()).limit(5).all()
    
    positive_result = Health.query.filter(Health.target == 1).count()
    negative_result = Health.query.filter(Health.target == 0).count()
    
    return render_template("/dashboard/index.html", users=users, positive_result = positive_result, negative_result = negative_result)

# SECTION User Management

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
        except:
            return "Error"
    
        flash('Patient Registered Successfully')
        return redirect(url_for('patient_record'))
    else:
        return render_template("dashboard/add_patient.html")

@app.route("/delete_patient/<int:id>")
def delete_patient(id):
    user_to_delete = User.query.get_or_404(id)

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return redirect("/patient_record")
    except:
        return "Error"

@app.route("/patient_record", methods=["POST", "GET"])
@register_breadcrumb(app, '.patient_record', 'Patient Records')
def patient_record():
    users = User.query.join(Health).filter(User.id == Health.user_id).order_by(User.date_created).all()
    return render_template("/dashboard/patient_record.html", users=users)

@app.route('/print/<int:id>/summary_report.pdf', methods=['GET', 'POST'])
def print_summary_report(id):
    id = User.query.get_or_404(id)
    html = render_template('dashboard/print_summary_report.html', id = id)
    return render_pdf(HTML(string=html))

@login_required
@register_breadcrumb(app, '.summary_report', 'Summary Report')
@app.route('/summary_report')
def summary_report():
    users = User.query.join(PreviousRecord).filter(PreviousRecord.user_id == User.id ).order_by(User.date_created).all()
    
    return render_template('dashboard/summary_report.html', users = users)

@app.route("/users")
def users():
    users = User.query.all()
    return jsonify([user.serialize for user in users])

@app.route('/autocomplete', methods = ['GET'])
def autocomplete():
    search = request.args.get('q')
    query = User.query(User.fullname).filter(User.fullname.like('%' + str(search) + '%'))
    results = [mv[0] for mv in query.all()]
    return jsonify(matching_results=results)

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
        except:
            return render_template('dashboard/update_patient_record.html', error = "Something Wrong. Please Try Again.")

        flash("Successfully Update Patient Information")
        return redirect(url_for('update_patient_record', id = id))
    else:
        return render_template("dashboard/update_patient_record.html", user=user)

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

# !SECTION

# SECTION Prediction

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

# !SECTION

# SECTION Data Visualization

@login_required
@register_breadcrumb(app, '.chart', 'Data Visualization')
@app.route('/data_visualization')
def data_visualization():
    dataset = pandas.read_sql(db.session.query(User).statement, db.session.bind).merge(pandas.read_sql(db.session.query(Health).statement, db.session.bind), left_on = 'id', right_on = 'user_id')
    
    # Second Chart
    X = request.args.get('X_value')

    if X == 'age_x':
        data = pandas.DataFrame({'count': dataset.groupby(['age_x', 'target']).size()}).reset_index() 
        data['result'] = data['age_x'].map(str) + " : " + data['target'].map({0: 'Negative', 1: 'Positive'})
    else:
        data = pandas.DataFrame({'count': dataset.groupby(['sex_x', 'target']).size()}).reset_index() 
        data['result'] = data['sex_x'].map({0: 'Female', 1: 'Male'}) + " : " + data['target'].map({0: 'Negative', 1: 'Positive'})

    data['target'] = data['target'].dropna()
    result = data['result'].tolist()
    count = data['count'].tolist()

    source = ColumnDataSource(data = dict(result = result, count = count, color = Viridis5))

    TOOLTIPS = [("Count", "@count")]
    
    plot = figure(x_range = result, y_range = (0, len(dataset)), toolbar_location = None, tooltips = TOOLTIPS, sizing_mode = 'scale_width')
    plot.vbar(x = 'result', top = 'count', source = source, width = 0.5, legend_group = 'result', color = 'color')
    
    # Third Chart
    Xs = request.args.get('X_values')

    if Xs == 'age_x':
        datas = pandas.DataFrame({'count': dataset.groupby(['age_x', 'chol']).size()}).reset_index() 
        datas['result'] = datas['age_x'].map(str) + " | " + datas['chol'].map(str)
    else:
        datas = pandas.DataFrame({'count': dataset.groupby(['sex_x', 'chol']).size()}).reset_index() 
        datas['result'] = datas['sex_x'].map({0: 'Female', 1: 'Male'}) + " : " + datas['chol'].map(str)

    results = datas['result'].tolist()
    counts = datas['count'].tolist()

    sources = ColumnDataSource(data = dict(results = results, counts = counts, color = Viridis5))

    TOOLTIPS2 = [("Count", "@counts")]
    
    plots = figure(x_range = results, y_range = (0, len(dataset)), toolbar_location = None, tooltips = TOOLTIPS2, sizing_mode = 'scale_width')
    plots.vbar(x = 'results', top = 'counts', source = sources, width = 0.5, legend_group = 'results', color = 'color')
    
    chart = file_html(plot, CDN)
    charts = file_html(plots, CDN)

    return render_template('dashboard/chart.html', chart = chart, charts = charts)

# !SECTION
