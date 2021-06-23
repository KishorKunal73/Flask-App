from flask import Flask, render_template, request, url_for, redirect, session
from flask import send_from_directory, send_file, current_app, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from werkzeug.utils import secure_filename
import json
from datetime import datetime
import os
from flask import flash
import secrets


def save_image(qimage):
    hash_qimage = secrets.token_urlsafe(10)
    _, file_extesion = os.path.splitext(qimage.filename)
    qimage_name = hash_qimage + file_extesion
    file_path = os.path.join(current_app.root_path, 'static/img', qimage_name)
    qimage.save(file_path)
    return qimage_name


def save_image(aimage):
    hash_aimage = secrets.token_urlsafe(10)
    _, file_extesion = os.path.splitext(aimage.filename)
    aimage_name = hash_aimage + file_extesion
    file_path = os.path.join(current_app.root_path, 'static/img', aimage_name)
    aimage.save(file_path)
    return aimage_name


with open('config.json', 'r') as c:
    params = json.load(c)["params"]

UPLOAD_FOLDER = params["uplod_location"]
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


local_server = True
app = Flask(__name__)
app.secret_key = 'edubaaz lol'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)
mail = Mail(app)


if (local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]


db = SQLAlchemy(app)


class Contacts(db.Model):

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)


class Questions(db.Model):

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    question = db.Column(db.String(120), nullable=False)
    question_img = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)


class Qnas(db.Model):

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=True)
    question = db.Column(db.String(40), nullable=False)
    qimage = db.Column(db.String(120), default='image.jpg')
    answer = db.Column(db.String(400), nullable=False)
    aimage = db.Column(db.String(120), default='image.jpg')
    slug = db.Column(db.String(50), nullable=True)
    date = db.Column(db.String(20), nullable=True)


@app.route("/")
def home():
    return render_template('index.html', params=params)


class Posts(db.Model):

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)


@app.route("/post")
def post():
    return render_template('subjectpage.html', params=params)

@app.route("/notes")
def notes():
    return render_template('notes.html', params=params)

@app.route("/up_notes")
def uploadNotes():
    return render_template('up_notes.html', params=params)


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():

    if ('user' in session and session['user'] == params['admin_username']):
        qnas = Qnas.query.all()
        return render_template('dashboard.html', params=params, qnas=qnas)

    if request.method == 'POST':
        username = request.form.get('Uname')
        password = request.form.get('Pass')
        if (username == params['admin_username'] and password == params['admin_password']):
            session['user'] = username
            qnas = Qnas.query.all()
            return render_template('dashboard.html', params=params, qnas=qnas)

    return render_template('login.html', parasm=params)


@app.route("/up_qna", methods=['GET', 'POST'])
def up_qna():
     if ('user' in session and session['user'] == params['admin_username']):

        if (request.method == 'POST'):
             
             name = request.form.get('name')
             question = request.form.get('question')
             qimage = save_image(request.files.get('qimage'))
             answer = request.form.get('answer')
             aimage = save_image(request.files.get('aimage'))
             slug = request.form.get('slug')

             entry = Qnas(name=name, question=question, qimage=qimage,
                            answer=answer, aimage=aimage, slug=slug, date=datetime.now())
             db.session.add(entry)
             db.session.commit()
             flash('your post has been submitted', 'success')
             return redirect('dashboard')
        return render_template('up_qna.html', params=params)


@app.route("/about")
def about():
    return render_template('about.html', params=params)


@app.route("/qnapage")
def qnapage():
    return render_template('qnapage.html', params=params)



@app.route("/qna/<string:qna_slug>", methods=['GET'])
def qna_render(qna_slug):
    qna = Qnas.query.filter_by(slug=qna_slug).first()
    return render_template('qna.html', params=params, qna=qna)



@app.route("/qnasection")
def qnasection():

    qnas = Qnas.query.all()[0:8]
    return render_template('qnasection.html', params=params, qnas=qnas)






@app.route("/upquestion")
def upquestion():
    return render_template('upquestion.html', params=params)


@app.route("/logout")
def logout():
    session.pop('user', None)
    return "<h1> Successfully Logout</h1>"  


@app.route("/delete/<string:sno>", methods = ['GET', 'POST'])
def delete(sno):

    if ('user' in session and session['user'] == params['admin_username']):
        qna = Qnas.query.filter_by(sno=sno).first()
        db.session.delete(qna)
        db.session.commit()
    
    return redirect ('/dashboard')

    
    return "<h1> Successfully Logout</h1>"  

@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if ('user' in session and session['user'] == params['admin_username']):
        if request.method== 'POST':
            name=request.form.get('name')
            question=request.form.get('question')
            qimage = save_image(request.files.get('qimage'))
            answer=request.form.get('answer')
            aimage = save_image(request.files.get('aimage'))
            slug=request.form.get('slug')
                  
            qna =Qnas.query.filter_by(sno=sno).first()
            qna.name = name 
            qna.question = question
            qna.qimage = qimage
            qna.answer = answer
            qna.aimage = aimage
            qna.slug = slug
            db.session.commit()
            return redirect('/edit/'+ sno)
    qna =Qnas.query.filter_by(sno=sno).first()
    return render_template('edit.html', params=params, qna=qna)        





     

@app.route("/uploadquestion", methods=['GET', 'POST'])
def upsection():
    if (request.method == 'POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        question = request.form.get('question')

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        entry = Questions(name=name, email=email, question=question,
                          question_img=filename, date=datetime.now())
        db.session.add(entry)
        db.session.commit()

        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients=[params['gmail-user']],
                          body=question
                          )

    return render_template('complete.html', params=params)


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if(request.method == 'POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, phone_num=phone,
                         msg=message, date=datetime.now(), email=email)
        db.session.add(entry)
        db.session.commit()

        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients=[params['gmail-user']],
                          body=message + "\n" + phone
                          )

    return render_template('contact.html', params=params)


app.run(debug=True)
