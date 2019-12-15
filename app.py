from flask import Flask, render_template, request, session, redirect, g, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, ValidationError
from wtforms.validators import InputRequired, Email, Length
import ctypes
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'fgfghjghghfgfggg'
app.secret_key = 'DSADSAFDET$%TE%dffgfdgfdg6767$@$$^%'
Bootstrap(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(80))
    twofa = db.Column(db.String(15))
    datecreated = db.Column(db.DateTime, default=datetime.now)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15))
    queryhistory = db.Column(db.String(255))
    queryresults = db.Column(db.String(255))
    datecreated = db.Column(db.DateTime, default=datetime.now)

class Login_History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15))
    logouttime = db.Column(db.DateTime)
    datecreated = db.Column(db.DateTime, default=datetime.now)

class LoginForm(FlaskForm):
    uname = StringField('username', validators=[InputRequired('Incorrect'), Length(min=4, max=15)])
    pword = PasswordField('password', validators=[InputRequired('Incorrect'), Length(min=8, max=80)])
    twofa = StringField('twofa', validators=[InputRequired('Two-factor failure'), Length(min=10, max=15)], id='2fa')

class LoginHistoryForm(FlaskForm):
    uname = StringField('username', validators=[InputRequired('Incorrect'), Length(min=4, max=15)])


class HistoryForm(FlaskForm):
    uname = StringField('username', validators=[InputRequired('Incorrect'), Length(min=4, max=15)])


def validate_uname(self, uname):
    user_object = session['user']
    if user_object:
        raise ValidationError("Username already exists. Select a different username")
#    if user_object == User.query.filter_by(username=username).first()
#        raise ValidationError("Username already exists. Select a different username")

class RegisterForm(FlaskForm):
    uname = StringField('username', validators=[InputRequired(message='Username incorrect'), Length(min=4, max=15)])
    pword = PasswordField('password', validators=[InputRequired(message='Password incorrect'), Length(min=8, max=80)])
    twofa = StringField('twofa', validators=[InputRequired('Two-factor failure'), Length(min=10, max=15)], id='2fa')

class SpellCheckForm(FlaskForm):
    inputtext = StringField('SpellCheck', validators=[InputRequired(message='Check Spelling'), Length(min=4, max=255)])


@app.route('/', methods=['GET', 'POST'])
def index():

    return redirect(url_for('register'))

@app.route('/history', methods=['GET', 'POST'])
def history():

    history_form = HistoryForm()

    if g.user == 'admin' and request.method == 'POST' and history_form.validate():
        db.create_all()
        queries = History.query.filter(History.username == history_form.uname.data).all()
        totalnumqueries = History.query.filter_by(username=history_form.uname.data).count()
        return render_template('history.html', queries=queries, totalnumqueries=totalnumqueries, history_form=history_form)
    if g.user:
        db.create_all()
        queries = History.query.filter((History.username == g.user) | (g.user == 'admin')).all()
        totalnumqueries = History.query.filter_by(username=g.user).count()
        return render_template('history.html', queries=queries, totalnumqueries=totalnumqueries, history_form=history_form)
    return redirect(url_for('login'))


@app.route('/history/query<id>', methods=['GET'])
def historybyid(id):

    history_form = HistoryForm()
    if request.method == 'GET':
        db.create_all()
        queries = History.query.filter_by(id=id).all()
        for query in queries:
            if g.user == query.username or g.user == "admin":
                totalnumqueries = 1
                return render_template('history.html', queries=queries, totalnumqueries=totalnumqueries, history_form=history_form)
    return redirect(url_for('login'))


@app.route('/login_history', methods=['GET', 'POST'])
def login_history():
    loginhistory_form = LoginHistoryForm()

    if g.user == "admin" and request.method == 'POST' and loginhistory_form.validate():
        login_history_query = Login_History.query.filter_by(username=loginhistory_form.uname.data).all()
        username = loginhistory_form.uname.data
        # totalnumqueries = User.query.filter_by(username=g.user).count()
        return render_template('loginhistory.html', loginhistory_form=loginhistory_form, login_history_query=login_history_query)
    return render_template('loginhistory.html', loginhistory_form=loginhistory_form)
    # return redirect(url_for('login'))


# User registration: /your/webroot/register
@app.route('/register', methods=['GET', 'POST'])
def register():
    request_form = RegisterForm()

    db.create_all()

    exists = User.query.filter_by(username="admin").first()
    if not exists:
        set_admin = User(username="admin", password="Administrator@1", twofa="12345678901")
        db.create_all()
        db.session.add(set_admin)
        db.session.commit()

    if request.method == 'POST' and request_form.validate():
        # session['user'] = request.form['uname']
        # session['password'] = request.form['pword']
        # session['twofa'] = request.form['twofa']

        new_user = User(username=request.form['uname'], password=request.form['pword'], twofa=request.form['twofa'])
        db.create_all()
        db.session.add(new_user)
        db.session.commit()

        # new_history = History(username=request.form['uname'], queryhistory="Test test")
        # db.create_all()
        # db.session.add(new_history)
        # db.session.commit()

        # form.validate_on_submit():
        success = "success"
        return '<div id="success">Success Proceed to Login page<a href="/login">Login</a></div>'

    # else:
    # return '<div id="success">Failure return to Registration page<a href="/register">Re-register</a></div>'
    success ="failure"
    return render_template('register.html', request_form=request_form)


# User login: /your/webroot/loginetsession
@app.route('/login', methods=['GET', 'POST'])
def login():

    login_form = LoginForm()

    db.create_all()

    exists = User.query.filter_by(username="admin").first()
    if not exists:
        set_admin = User(username="admin", password="Administrator@1", twofa="12345678901")
        db.create_all()
        db.session.add(set_admin)
        db.session.commit()

    # if form.validate_on_submit():
    # if 'user' in session:

    new_login = User.query.filter_by(username=login_form.uname.data).first()
    if new_login:
        if new_login.password == login_form.pword.data and new_login.twofa == login_form.twofa.data:


        # if request.method == 'POST' and login_form.validate() and session['user'] == login_form.uname.data and session['password'] == login_form.pword.data and session['twofa'] == login_form.twofa.data:

            session['user'] = login_form.uname.data
            result = "success"

            set_history_login = Login_History(username=login_form.uname.data)
            db.create_all()
            db.session.add(set_history_login)
            db.session.commit()

            # return '<div id="request">success Proceed to Spell Check page<a href="/spell_check">Spell Check</a></div>'

        return redirect(url_for('spell_check'))

    result = "failure"
    # return '<div id="result">failure</div>'
    return render_template('login.html', login_form=login_form)


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']


@app.route('/getsession')
def getsession():
    if 'user' in session:
        return session['user']

    return 'Not logged in'


@app.route('/dropsession')
def dropsession():
    session.pop('user', None)
    return 'Dropped!'


# Result retrieval: /your/webroot/spell_check
@app.route('/spell_check', methods=['GET', 'POST'])
def spell_check():
    if g.user:
        spell_check_form = SpellCheckForm()

        if request.method == 'POST' and spell_check_form.validate():
            # return '<div id="success">success</div>'
            # inputTextString = login_form.inputtext.data
            inputTextString = request.form['inputtext']
            # inputTextString = spell_check_form.inputtext.data


            # new_user = History(username=request.form['uname'], queryhistory=login_form.inputtext.data)

            #new_history = History(username=request.form['uname'], queryhistory=inputTextString)
            db.create_all()

            new_history = History(username=g.user, queryhistory=inputTextString)
            db.create_all()
            db.session.add(new_history)
            db.session.commit()


            return '<div id="success">{}</div>'.format(inputTextString)
            checkspell = ctypes.cdll('a.o')
            checkspell.argtypes(ctypes.c_char_p)
            misspelledString = checkspell.check_words(inputTextString)
            return '<h1 id="misspelled">Misspelled words are {}.'.format(misspelledString)

        return render_template('spell_check.html', spell_check_form=spell_check_form)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
